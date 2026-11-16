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
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

COMPILE_TIMEOUT = 25
RUN_TIMEOUT = 10
MAX_CODE_BYTES = 512 * 1024


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
        return ("mono", mcs, mono)

    # 2) Windows：.NET Framework 自带的 csc.exe
    candidates = [
        r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
        r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ("csc", p, None)

    # 3) 兜底：dotnet CLI（如果装了 SDK）
    dotnet = shutil.which("dotnet")
    if dotnet:
        return ("dotnet", dotnet, None)

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


# ---------------------------------------------------------------- 编译执行

def run_code(code: str) -> dict:
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

    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return {"ok": False, "err": "代码太大了（上限 512 KB）"}

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
            return {"ok": False, "err": "dotnet CLI 模式尚未启用，请装 mono 或使用 Windows"}

        try:
            b = subprocess.run(
                build_cmd, capture_output=True, timeout=COMPILE_TIMEOUT, cwd=workdir,
                stdin=subprocess.DEVNULL
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "err": "编译超时（超过 %d 秒）" % COMPILE_TIMEOUT}

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
            exec_cmd = [runner or "mono", exe]
        else:
            exec_cmd = [exe]

        t0 = time.time()
        try:
            r = subprocess.run(
                exec_cmd, capture_output=True, timeout=RUN_TIMEOUT, cwd=workdir,
                stdin=subprocess.DEVNULL
            )
        except subprocess.TimeoutExpired:
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
                "err": (err or "程序异常退出，返回码 %d" % r.returncode),
            }

        return {"ok": True, "out": out, "err": err, "ms": elapsed}

    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------- HTTP 服务

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # APK 里的页面从 assets 加载（虚拟域名），访问本服务属于跨域，必须放行
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        # Private Network Access：APK 页面(miccode.local) 访问 127.0.0.1 时必需的预检应答
        self.send_header("Access-Control-Allow-Private-Network", "true")
        if self.path.endswith((".json", ".js", ".css")):
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        # 预检请求：前端发 Content-Type: application/json 时会触发
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        route = self.path.split("?")[0]
        if route == "/api/info":
            kind, compiler, runner = TOOLCHAIN
            lang = {"mono": 7, "csc": 5, "dotnet": 9}.get(kind, 0)
            self._json({
                "compiler": kind or "none",
                "csharp": lang,
                "builder": compiler or "",
                "platform": platform.system(),
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
        if route == "/api/split":
            self._handle_split()
            return
        if route != "/api/run":
            self.send_error(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_CODE_BYTES * 2:
                raise ValueError("bad length")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            code = payload.get("code", "")
        except Exception as e:
            self._json({"ok": False, "err": "请求格式不对：%s" % e})
            return

        result = run_code(code)
        self._json(result)

    def _handle_split(self):
        """
        尝试让另一个 App 在相邻窗口打开 —— 真·系统分屏。

        靠 FLAG_ACTIVITY_LAUNCH_ADJACENT (0x08000000)，Android 12L(API 32) 以上有效。
        这个 flag 只能由原生 startActivity 发出，网页做不到；但 Termux 有 shell，
        可以借系统自带的 am 命令把它发出去。PC 上必然失败，前端会降级成 iframe。
        """
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except Exception:
            payload = {}

        pkg = (payload.get("package") or "com.deepseek.chat").strip()
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

    def _json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
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
