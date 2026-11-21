#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py — C# 练习本的本地服务

职责：
  1. 把当前目录当静态站点托管（index.html / symbols.json / vendor/）
  2. 提供 POST /api/run：编译并运行提交的 C# 代码

零依赖，只用 Python 标准库。

用法：
    python server.py              # 默认 http://127.0.0.1:8080
    python server.py --port 9000
    python server.py --no-browser # 不自动打开浏览器

编译器自动探测：
    Termux / Linux  → mcs + mono      （pkg install mono）
    Windows         → csc.exe          （系统自带 .NET Framework）
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

COMPILE_TIMEOUT = 25
RUN_TIMEOUT = 10
MAX_CODE_BYTES = 512 * 1024
MAX_STDIN_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 256 * 1024  # stdout 与 stderr 合计上限
MAX_REQUEST_BYTES = 4 * 1024 * 1024
MAX_CONCURRENT_RUNS = 2
APK_ORIGIN = "http://miccode.local"
RUN_SLOTS = threading.BoundedSemaphore(MAX_CONCURRENT_RUNS)


# ---------------------------------------------------------------- 工具链探测

def find_toolchain():
    """
    返回 (kind, compiler, runner)
      ("mono", "/path/mcs", "/path/mono")
      ("csc",  "C:/.../csc.exe", None)
      (None, None, None)
    """
    # 1) Termux / Linux / macOS：mono 系
    mcs = shutil.which("mcs") or shutil.which("csc") or shutil.which("mcs.exe")
    if mcs:
        mono = shutil.which("mono")
        if mono:
            return ("mono", mcs, mono)
        print("  警告：找到编译器 %s 但没找到 mono，运行功能不可用" % mcs)

    # 2) Windows：.NET Framework 自带的 csc.exe
    candidates = [
        r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
        r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ("csc", p, None)

    return (None, None, None)


TOOLCHAIN = find_toolchain()


def decode_output(raw: bytes) -> str:
    """Windows 下编译器/程序输出可能是 GBK，Termux 下是 UTF-8。依次尝试。"""
    if not raw:
        return ""
    for enc in ("utf-8", "gbk", "cp936", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def run_limited(cmd, timeout: int, cwd: str, stdin_data=None):
    """运行子进程，分别限制 stdout / stderr 的内存占用，并在超限时终止进程。"""
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE if stdin_data is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        bufsize=0,
    )
    stdout = bytearray()
    stderr = bytearray()
    output_exceeded = threading.Event()
    output_lock = threading.Lock()
    output_size = [0]

    def drain(stream, buffer):
        while True:
            chunk = stream.read(8192)
            if not chunk:
                return
            with output_lock:
                remaining = MAX_OUTPUT_BYTES - output_size[0]
                kept = min(len(chunk), max(0, remaining))
                if kept:
                    buffer.extend(chunk[:kept])
                    output_size[0] += kept
                if len(chunk) > kept:
                    output_exceeded.set()

    readers = [
        threading.Thread(target=drain, args=(proc.stdout, stdout), daemon=True),
        threading.Thread(target=drain, args=(proc.stderr, stderr), daemon=True),
    ]
    for reader in readers:
        reader.start()

    writer = None
    if stdin_data is not None:
        def write_stdin():
            try:
                if stdin_data:
                    proc.stdin.write(stdin_data)
            except (BrokenPipeError, OSError):
                pass
            finally:
                try:
                    proc.stdin.close()
                except OSError:
                    pass

        writer = threading.Thread(target=write_stdin, daemon=True)
        writer.start()

    deadline = time.monotonic() + timeout
    timed_out = False

    def stop_process():
        try:
            proc.kill()
        except OSError:
            # 进程可能刚好自行退出。
            pass

    while proc.poll() is None:
        if output_exceeded.is_set():
            stop_process()
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            stop_process()
            break
        try:
            proc.wait(timeout=min(0.05, remaining))
        except subprocess.TimeoutExpired:
            continue

    proc.wait()
    for reader in readers:
        reader.join(timeout=1)
    if writer:
        writer.join(timeout=1)
    return subprocess.CompletedProcess(
        cmd, proc.returncode, bytes(stdout), bytes(stderr),
    ), timed_out, output_exceeded.is_set()


# ---------------------------------------------------------------- 编译执行

def run_code(code: str, stdin_text: str = "") -> dict:
    kind, compiler, runner = TOOLCHAIN
    if kind is None:
        return {
            "ok": False,
            "err": (
                "找不到 C# 编译器。\n\n"
                "  在 Termux 里执行：pkg install mono\n"
                "  Windows 一般自带 csc.exe（.NET Framework）\n\n"
                "装完重启本服务。"
            ),
        }

    try:
        code_size = len(code.encode("utf-8"))
        stdin_data = stdin_text.encode("utf-8")
    except UnicodeEncodeError:
        return {"ok": False, "err": "代码或输入包含无效的 Unicode 字符"}
    if code_size > MAX_CODE_BYTES:
        return {"ok": False, "err": "代码太大了（上限 512 KB）"}
    if len(stdin_data) > MAX_STDIN_BYTES:
        return {"ok": False, "err": "输入太大了（上限 64 KB）"}

    workdir = tempfile.mkdtemp(prefix="cspad_")
    try:
        src = os.path.join(workdir, "Program.cs")
        exe = os.path.join(workdir, "Program.exe")

        # utf-8-sig 带 BOM：让 csc 正确识别源码编码，中文注释不会乱码
        with open(src, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(code)

        if kind == "mono":
            build_cmd = [compiler, "-out:" + exe, src]
        elif kind == "csc":
            build_cmd = [compiler, "/nologo", "/out:" + exe, src]
        else:
            return {"ok": False, "err": "当前编译器类型不受支持"}

        try:
            b, timed_out, output_exceeded = run_limited(
                build_cmd, COMPILE_TIMEOUT, workdir,
            )
        except OSError as e:
            return {"ok": False, "err": "无法启动编译器：%s" % e}
        if timed_out:
            return {"ok": False, "err": "编译超时（超过 %d 秒）" % COMPILE_TIMEOUT}
        if output_exceeded:
            return {
                "ok": False,
                "err": (decode_output(b.stdout) + decode_output(b.stderr)).strip()
                       + "\n编译器输出超过 256 KB，已终止。",
            }

        if b.returncode != 0 or not os.path.exists(exe):
            msg = (decode_output(b.stdout) + decode_output(b.stderr)).strip()
            # 去掉临时目录的绝对路径，错误信息更好读
            msg = msg.replace(workdir + os.sep, "").replace(workdir, "")

            # 老编译器不认插值字符串时，给出能直接照做的建议
            if "CS1056" in msg and "$" in code:
                msg += (
                    "\n\n———— 提示 ————\n"
                    "当前编译器只支持到 C# 5，不认 $\"…{x}…\" 插值字符串。\n"
                    "改成这两种写法之一：\n"
                    "  string.Format(\"{0} 的平方是 {1}\", i, i * i)\n"
                    "  \"平方是 \" + (i * i)\n"
                    "（平板上的 mcs 支持 C# 7，可以放心用 $\"\"）"
                )
            return {"ok": False, "err": msg or "编译失败（无输出）"}

        if kind == "mono":
            if not runner:
                return {"ok": False, "err": "找不到 mono 运行时，只能编译不能运行。\n\n"
                                           "在 Termux 执行 pkg install mono 后重启服务。"}
            exec_cmd = [runner, exe]
        else:
            exec_cmd = [exe]

        t0 = time.time()
        try:
            r, timed_out, output_exceeded = run_limited(
                exec_cmd, RUN_TIMEOUT, workdir, stdin_data=stdin_data,
            )
        except OSError as e:
            return {"ok": False, "err": "无法启动运行时：%s" % e}
        if timed_out:
            return {
                "ok": False,
                "err": "运行超时（超过 %d 秒）—— 大概率是死循环，检查 while / for 的退出条件"
                       % RUN_TIMEOUT,
            }

        out = decode_output(r.stdout)
        err = decode_output(r.stderr)
        elapsed = int((time.time() - t0) * 1000)

        if r.returncode != 0:
            return {
                "ok": False,
                "out": out,
                "err": (err or "程序异常退出，返回码 %d" % r.returncode)
                       + ("\n输出超过 256 KB，已终止。" if output_exceeded else ""),
            }

        if output_exceeded:
            return {
                "ok": False,
                "out": out,
                "err": "输出超过 256 KB，已终止。",
            }

        return {"ok": True, "out": out, "err": err, "ms": elapsed}

    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------- HTTP 服务

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # 只有通过 API Origin 检查的请求会设置 _cors_origin；静态页面和非法来源
        # 不会获得 CORS / Private Network Access 放行头。
        cors_origin = getattr(self, "_cors_origin", None)
        if cors_origin:
            self.send_header("Access-Control-Allow-Origin", cors_origin)
            self.send_header("Vary", "Origin")
            if self.command == "OPTIONS":
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                if (cors_origin == APK_ORIGIN and
                        self.headers.get("Access-Control-Request-Private-Network", "").lower() == "true"):
                    self.send_header("Access-Control-Allow-Private-Network", "true")
        if self.path.split("?")[0].endswith((".json", ".js", ".css")):
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _authorize_api_origin(self):
        """只允许请求来源为当前服务同源或 APK 的固定虚拟 Origin。"""
        self._cors_origin = None
        origin = self.headers.get("Origin")
        if origin:
            if origin == APK_ORIGIN:
                self._cors_origin = origin
                return True
            try:
                parsed = urlsplit(origin)
                request_host = self.headers.get("Host", "")
                if (parsed.scheme == "http" and parsed.netloc.lower() == request_host.lower()
                        and not parsed.path and not parsed.query and not parsed.fragment
                        and parsed.username is None and parsed.password is None):
                    self._cors_origin = origin
                    return True
            except ValueError:
                pass
            return False

        # 同源 GET 通常不发送 Origin。只对浏览器明确标记为 same-origin/none，
        # 或 Referer 与当前 Host 一致的只读 API 请求提供兼容；变更状态的 POST
        # 和 CORS 预检必须带可验证的 Origin。
        if self.command != "GET":
            return False
        if self.headers.get("Sec-Fetch-Site", "").lower() in ("same-origin", "none"):
            return True
        referer = self.headers.get("Referer")
        if referer:
            try:
                ref = urlsplit(referer)
                return (ref.scheme == "http" and
                        ref.netloc.lower() == self.headers.get("Host", "").lower())
            except ValueError:
                return False
        return False

    def do_OPTIONS(self):
        route = self.path.split("?")[0]
        if not route.startswith("/api/"):
            self.send_error(404, "Not Found")
            return
        if not self._authorize_api_origin():
            self._json({"ok": False, "err": "请求来源不受允许"}, status=403)
            return
        # 预检请求：前端发 Content-Type: application/json 时会触发
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        route = self.path.split("?")[0]
        if route.startswith("/api/") and not self._authorize_api_origin():
            self._json({"ok": False, "err": "请求来源不受允许"}, status=403)
            return
        if route == "/api/info":
            kind, compiler, runner = TOOLCHAIN
            lang = {"mono": 7, "csc": 5}.get(kind, 0)
            self._json({
                "compiler": kind or "none",
                "csharp": lang,
                "builder": compiler or "",
                "platform": platform.system(),
                "stdin": True,
                "stdin_max_bytes": MAX_STDIN_BYTES,
            })
            return
        if route == "/api/apps":
            self._handle_apps()
            return
        super().do_GET()

    def _handle_apps(self):
        """
        列出设备上已安装的第三方应用包名，供前端做"选择分屏搭档"。
        网页本身没有枚举应用的权限，但 Termux 里可以跑 pm list packages。
        """
        if platform.system() != "Linux":
            self._json({"ok": False, "apps": [], "reason": "not_android",
                        "msg": "只有 Android/Termux 上才能读取已安装应用"})
            return

        pm = shutil.which("pm") or "/system/bin/pm"
        if not shutil.which("pm") and not os.path.exists(pm):
            self._json({"ok": False, "apps": [], "reason": "no_pm", "msg": "找不到 pm 命令"})
            return

        try:
            r = subprocess.run([pm, "list", "packages", "-3"],
                               capture_output=True, timeout=10)
            out = decode_output(r.stdout)
            pkgs = [line[len("package:"):].strip()
                    for line in out.splitlines() if line.startswith("package:")]
            self._json({"ok": True, "apps": sorted(set(pkgs)), "count": len(pkgs)})
        except subprocess.TimeoutExpired:
            self._json({"ok": False, "apps": [], "reason": "timeout"})
        except Exception as e:
            self._json({"ok": False, "apps": [], "reason": "error", "msg": str(e)[:200]})

    def do_POST(self):
        route = self.path.split("?")[0]
        if route.startswith("/api/") and not self._authorize_api_origin():
            self._json({"ok": False, "err": "请求来源不受允许"}, status=403)
            return
        if route == "/api/split":
            self._handle_split()
            return
        if route != "/api/run":
            self.send_error(404, "Not Found")
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("bad length")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                self._json({"ok": False, "err": "请求内容必须是 JSON 对象"}, status=400)
                return
            code = payload.get("code", "")
            if not isinstance(code, str):
                self._json({"ok": False, "err": "code 必须是字符串"}, status=400)
                return
            stdin_text = payload.get("stdin", "")
            if not isinstance(stdin_text, str):
                self._json({"ok": False, "err": "stdin 必须是字符串"}, status=400)
                return
        except Exception as e:
            self._json({"ok": False, "err": "请求格式不对：%s" % e}, status=400)
            return

        if not RUN_SLOTS.acquire(blocking=False):
            self._json({"ok": False, "err": "运行繁忙，请稍后重试"}, status=429)
            return
        try:
            result = run_code(code, stdin_text)
            self._json(result)
        finally:
            RUN_SLOTS.release()

    def _handle_split(self):
        """
        尝试让另一个 App 在相邻窗口打开 —— 真·系统分屏。

        靠 FLAG_ACTIVITY_LAUNCH_ADJACENT (0x08000000)，Android 12L(API 32) 以上有效。
        这个 flag 只能由原生 startActivity 发出，网页做不到；但 Termux 有 shell，
        可以借系统自带的 am 命令把它发出去。PC 上必然失败，前端会降级成 iframe。
        """
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length < 0 or length > MAX_REQUEST_BYTES:
                self._json({"ok": False, "reason": "bad_payload", "msg": "请求内容太大"}, status=413)
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            if not isinstance(payload, dict):
                self._json({"ok": False, "reason": "bad_payload", "msg": "请求内容必须是 JSON 对象"}, status=400)
                return
        except Exception:
            self._json({"ok": False, "reason": "bad_payload", "msg": "请求格式不对"}, status=400)
            return

        pkg = payload.get("package") or "com.deepseek.chat"
        if not isinstance(pkg, str):
            self._json({"ok": False, "reason": "bad_package", "msg": "包名不合法"}, status=400)
            return
        pkg = pkg.strip()
        if not pkg or len(pkg) > 200:
            self._json({"ok": False, "reason": "bad_package", "msg": "包名不合法"})
            return

        if platform.system() != "Linux":
            self._json({
                "ok": False, "reason": "not_android",
                "msg": "当前不是 Android/Termux 环境，无法调用 am",
            })
            return

        am = shutil.which("am") or "/system/bin/am"
        if not shutil.which("am") and not os.path.exists(am):
            self._json({"ok": False, "reason": "no_am", "msg": "找不到 am 命令"})
            return

        try:
            r = subprocess.run(
                [am, "start",
                 "-a", "android.intent.action.MAIN",
                 "-c", "android.intent.category.LAUNCHER",
                 "-p", pkg,
                 # 0x18000000 = FLAG_ACTIVITY_LAUNCH_ADJACENT (0x08000000)
                 #            | FLAG_ACTIVITY_NEW_TASK      (0x10000000)
                 # 官方文档要求两者必须配合，只给前者会退化成自由窗口/悬浮窗
                 "--activity-flags", "0x18000000"],
                capture_output=True, timeout=8,
            )
            out = decode_output(r.stdout + r.stderr).strip()
            bad = ("Error" in out) or ("Exception" in out) or ("Warning" in out and "unable" in out)
            sys.stderr.write("  [分屏] %s -> %s\n" % (pkg, out or "(无输出)"))
            self._json({"ok": r.returncode == 0 and not bad, "package": pkg, "msg": out[:400]})
        except subprocess.TimeoutExpired:
            self._json({"ok": False, "reason": "timeout", "msg": "am 命令超时（8 秒）"})
        except Exception as e:
            self._json({"ok": False, "reason": "error", "msg": str(e)[:300]})

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # 只记录 /api/run，静态资源不刷屏
        if "/api/run" in (args[0] if args else ""):
            sys.stderr.write("  [运行] %s\n" % (args[1] if len(args) > 1 else ""))


def main():
    ap = argparse.ArgumentParser(description="C# 练习本本地服务")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)

    if not os.path.exists(os.path.join(root, "symbols.json")):
        print("！ 缺少 symbols.json，先运行：python build_symbols.py <Unity的Managed/UnityEngine目录>")

    kind, compiler, runner = TOOLCHAIN
    print("=" * 52)
    print("  C# 练习本")
    print("=" * 52)
    print("  地址    http://%s:%d" % (args.host, args.port))
    if kind == "mono":
        print("  编译器  mcs  (%s)" % compiler)
        print("  运行器  %s" % (runner or "mono（未找到！）"))
    elif kind == "csc":
        print("  编译器  csc  (%s)" % compiler)
    else:
        print("  编译器  ！未找到 —— 代码编辑器可用，但「运行」会报错")
        if platform.system() == "Windows":
            print("           Windows 一般自带 csc.exe，检查 .NET Framework 是否完整")
        else:
            print("           执行 pkg install mono 后重启本服务")
    print("-" * 52)

    handler = partial(Handler, directory=root)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)

    if not args.no_browser:
        try:
            webbrowser.open("http://%s:%d" % (args.host, args.port))
        except Exception:
            pass

    print("  按 Ctrl+C 停止\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止")
        httpd.server_close()


if __name__ == "__main__":
    main()
