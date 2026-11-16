package com.miccode.app;

import android.app.Activity;
import android.app.ActivityOptions;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.DocumentsContract;
import android.util.Base64;
import android.view.KeyEvent;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.ValueCallback;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * MiCCode 的安卓外壳。
 *
 * 关键设计：**界面和编译是分开的**。
 *
 *   界面  → 打包在 APK 的 assets/www 里，通过虚拟域名 miccode.local 加载，
 *           没网、没 Termux 也能打开、能补全、能悬停看签名。
 *   编译  → 仍然在 Termux 里的 server.py（mono），只有点「运行」时才需要。
 *
 * 所以启动顺序是：先把界面放出来，再在后台悄悄把服务拉起来。
 */
public class MainActivity extends Activity {

    private static final String HOST = "miccode.local";
    private static final String PAGE_URL = "http://" + HOST + "/index.html";
    private static final String PROBE_URL = "http://127.0.0.1:8080/api/info";
    private static final String TERMUX_PREFIX = "/data/data/com.termux/files/usr";
    private static final String TERMUX_HOME = "/data/data/com.termux/files/home";
    private static final String START_CMD =
            "cd $HOME/miccode && python server.py --no-browser";

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;   // 文件选择回调（导入 .cs 用）

    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#080808"));

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);       // 草稿、分屏搭档、图标都存这里
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (u != null && HOST.equals(u.getHost())) {
                    return fromAssets(u.getPath());
                }
                return null;   // 127.0.0.1 的 API 请求交给系统正常发出
            }
        });

        // 没有 WebChromeClient 时网页的 <input type=file> 完全不工作
        // （点了没反应）—— 导入 .cs、上传图标都靠它
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb,
                                             FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = cb;
                try {
                    // 不用 params.createIntent()：系统选择器认不出 .cs 的 MIME，
                    // 会把文件过滤得一个都看不见。直接放开全部文件，前端校验扩展名
                    Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("*/*");
                    // 网页端 input 带 multiple 时要允许多选（长按第一个文件可多选）
                    if (params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE) {
                        i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                    }
                    startActivityForResult(Intent.createChooser(i, "选择代码文件"), 1001);
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        // 暴露给网页：真·分屏只能由本应用自己 startActivity 发起
        web.addJavascriptInterface(new Bridge(), "MiCCodeNative");

        setContentView(web);

        // 先把界面放出来 —— 这一步不依赖任何外部服务
        web.loadUrl(PAGE_URL);

        // 界面已经在跑了，后台再慢慢把编译服务拉起来
        kickServer();
    }

    /** 用 assets/www 里的文件响应 miccode.local 的请求 */
    private WebResourceResponse fromAssets(String path) {
        String name = (path == null || path.equals("/") || path.isEmpty())
                ? "/index.html" : path;
        try {
            InputStream in = getAssets().open("www" + name);
            String mime = mimeOf(name);
            boolean isText = mime.startsWith("text/")
                    || mime.contains("json")
                    || mime.contains("javascript")
                    || mime.contains("svg");
            return new WebResourceResponse(mime, isText ? "utf-8" : null, in);
        } catch (Exception e) {
            return new WebResourceResponse("text/plain", "utf-8",
                    new ByteArrayInputStream(("missing: " + name).getBytes()));
        }
    }

    private String mimeOf(String n) {
        if (n.endsWith(".html")) return "text/html";
        if (n.endsWith(".js")) return "application/javascript";
        if (n.endsWith(".css")) return "text/css";
        if (n.endsWith(".json")) return "application/json";
        if (n.endsWith(".png")) return "image/png";
        if (n.endsWith(".svg")) return "image/svg+xml";
        return "application/octet-stream";
    }

    /** 暴露给网页的原生能力 */
    public class Bridge {
        /**
         * 返回诊断字符串，前端据此提示：
         *   "mode4"    —— 已明确请求把目标放到分屏的右/下半（SECONDARY）
         *   "flag"     —— 反射不可用，只带了 LAUNCH_ADJACENT，左右由系统安排
         *   "notfound" —— 设备上没有这个包
         *   "error"    —— 其他异常
         */
        @JavascriptInterface
        public String split(String pkg) {
            return splitLaunch(pkg);
        }

        /** 让用户选一个文件夹；结果异步回传 window.__onFolder({files,cut}) */
        @JavascriptInterface
        public void importFolder() {
            runOnUiThread(new Runnable() {
                public void run() {
                    try {
                        startActivityForResult(
                                new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE), 1002);
                    } catch (Throwable ignored) { }
                }
            });
        }

        /**
         * 导出单个文件到 下载/MiCCode/。
         * MediaStore Downloads API（29+）不用存储权限；文件重名系统自动加 " (1)"。
         * 返回 "ok:文件名" / "unsupported" / "error"
         */
        @JavascriptInterface
        public String exportFile(String name, String content) {
            try {
                if (Build.VERSION.SDK_INT < 29) return "unsupported";
                String safe = (name == null || name.trim().isEmpty())
                        ? "code.cs" : name.replaceAll("[\\\\/:*?\"<>|]", "_");
                android.content.ContentValues cv = new android.content.ContentValues();
                cv.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, safe);
                cv.put(android.provider.MediaStore.MediaColumns.MIME_TYPE, "text/plain");
                cv.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
                        android.os.Environment.DIRECTORY_DOWNLOADS + "/MiCCode");
                Uri uri = getContentResolver().insert(
                        android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (uri == null) return "error";
                java.io.OutputStream os = getContentResolver().openOutputStream(uri);
                os.write((content == null ? "" : content).getBytes("UTF-8"));
                os.close();
                return "ok:" + safe;
            } catch (Throwable t) {
                return "error";
            }
        }

        /**
         * 把「设备上真的装了哪些应用」连同**真实图标**回传给网页。
         *
         * 为什么网页做不到：纯网页没有 PackageManager。而本应用在 manifest 的
         * <queries> 里声明了 MAIN/LAUNCHER，Android 11+ 才允许 queryIntentActivities
         * 看到全部桌面应用；图标则由系统直接解析（getApplicationIcon / loadIcon），
         * 不需要读 /data/app 下的 APK 文件 —— 那是 SELinux 拦着的。
         *
         * 结果异步回传：window.__onApps([{pkg,label,icon,sys}, ...])
         */
        @JavascriptInterface
        public void listApps() {
            new Thread(new Runnable() {
                public void run() {
                    final String json = buildAppsJson();
                    web.post(new Runnable() {
                        public void run() {
                            try {
                                web.evaluateJavascript(
                                        "window.__onApps && window.__onApps(" + json + ");", null);
                            } catch (Throwable ignored) { }
                        }
                    });
                }
            }).start();
        }
    }

    /** 收集桌面应用，编成 JSON 数组字符串 */
    private String buildAppsJson() {
        StringBuilder sb = new StringBuilder("[");
        try {
            PackageManager pm = getPackageManager();
            Intent main = new Intent(Intent.ACTION_MAIN);
            main.addCategory(Intent.CATEGORY_LAUNCHER);

            List<ResolveInfo> all = pm.queryIntentActivities(main, 0);
            List<ResolveInfo> user = new ArrayList<ResolveInfo>();
            List<ResolveInfo> system = new ArrayList<ResolveInfo>();
            Set<String> seen = new HashSet<String>();

            for (int k = 0; k < all.size(); k++) {
                ResolveInfo ri = all.get(k);
                if (ri == null || ri.activityInfo == null) continue;
                String pkg = ri.activityInfo.packageName;
                if (pkg == null || pkg.equals(getPackageName())) continue;  // 别把自己列进去
                if (!seen.add(pkg)) continue;                               // 一个应用多个入口时去重

                boolean isSys = ri.activityInfo.applicationInfo != null
                        && (ri.activityInfo.applicationInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0;
                (isSys ? system : user).add(ri);
            }

            Comparator<ResolveInfo> byName = new Comparator<ResolveInfo>() {
                public int compare(ResolveInfo a, ResolveInfo b) {
                    return String.valueOf(a.loadLabel(getPackageManager()))
                            .compareToIgnoreCase(String.valueOf(b.loadLabel(getPackageManager())));
                }
            };
            Collections.sort(user, byName);
            Collections.sort(system, byName);

            int n = 0;
            // 第三方应用排前面，系统应用垫后 —— 找搭子时几乎只用点前一半
            for (int pass = 0; pass < 2; pass++) {
                List<ResolveInfo> src = (pass == 0) ? user : system;
                for (int k = 0; k < src.size() && n < 160; k++, n++) {
                    ResolveInfo ri = src.get(k);
                    String pkg = ri.activityInfo.packageName;
                    CharSequence lbl = ri.loadLabel(pm);
                    if (n > 0) sb.append(',');
                    sb.append("{\"pkg\":\"").append(jsonEsc(pkg)).append("\",\"label\":\"")
                      .append(jsonEsc(lbl == null ? pkg : lbl.toString())).append("\",\"sys\":")
                      .append(pass == 1);
                    String icon = iconDataUri(pm, ri);
                    if (icon != null) {
                        sb.append(",\"icon\":\"").append(icon).append('"');
                    }
                    sb.append('}');
                }
            }
        } catch (Throwable t) {
            // 出任何问题都返回空数组，网页会退回预设列表
        }
        return sb.append(']').toString();
    }

    /** 把应用图标渲染成 64×64 的 PNG data URI */
    private String iconDataUri(PackageManager pm, ResolveInfo ri) {
        try {
            Drawable d = ri.loadIcon(pm);
            if (d == null) return null;
            final int S = 64;
            Bitmap bmp = Bitmap.createBitmap(S, S, Bitmap.Config.ARGB_8888);
            Canvas c = new Canvas(bmp);
            d.setBounds(0, 0, S, S);
            d.draw(c);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            bmp.compress(Bitmap.CompressFormat.PNG, 90, bos);
            bmp.recycle();
            return "data:image/png;base64,"
                    + Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP);
        } catch (Throwable t) {
            return null;
        }
    }

    /** JSON 字符串转义，控制字符一律压成空格（只用于应用名这类短文本） */
    private static String jsonEsc(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length() + 8);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': case '\r': case '\t':
                    b.append(' '); break;
                default:
                    if (c < 0x20) b.append(' ');
                    else b.append(c);
            }
        }
        return b.toString();
    }

    /**
     * 代码内容专用的转义：换行/制表符必须转成 \\n \\t 转义序列，不能压成空格，
     * 否则到了网页端整段代码会被拉成一行（缩进还在、换行全没）。
     */
    private static String jsonEscText(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length() + 64);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(' ');
                    else b.append(c);
            }
        }
        return b.toString();
    }

    /**
     * 让目标应用在相邻窗口打开（真·分屏）。
     *
     * 必须由本 Activity 自己 startActivity。用 am 命令发起时，发起方是 shell，
     * shell 不在任何任务栈里，系统没有「当前全屏应用」这个上下文，
     * LAUNCH_ADJACENT 就退化成自由窗口 —— 表现就是弹出悬浮窗。
     *
     * 关于左右位置：请求的是 WINDOWING_MODE_SPLIT_SCREEN_SECONDARY(4)，即「右/下半」，
     * 本应用留在左/上半。原生 Android 7~11 按这个执行；Android 12L+ 厂商接管了
     * 分屏管理，位置可能被系统重新安排 —— 那时只能靠分屏条上的交换按钮。
     */
    private String splitLaunch(String pkg) {
        try {
            PackageManager pm = getPackageManager();
            Intent i = pm.getLaunchIntentForPackage(pkg);
            if (i == null) return "notfound";   // 没装这个包

            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_LAUNCH_ADJACENT);
            final Intent target = i;

            // 反射在调用线程（JavaBridge）同步完成，这样返回值准确；
            // startActivity 必须在 UI 线程。
            ActivityOptions opts = null;
            try {
                opts = ActivityOptions.makeBasic();
                // WINDOWING_MODE_SPLIT_SCREEN_SECONDARY = 4
                // 隐藏 API（android.jar 里没有），运行时存在，只能反射调。
                java.lang.reflect.Method m = ActivityOptions.class
                        .getMethod("setLaunchWindowingMode", int.class);
                m.invoke(opts, Integer.valueOf(4));
            } catch (Throwable t) {
                // 反射被拦（非 SDK 接口限制）或方法不存在：退回只带 flag，左右由系统定
                opts = null;
            }

            final ActivityOptions fopts = opts;
            runOnUiThread(new Runnable() {
                public void run() {
                    try {
                        if (fopts != null) startActivity(target, fopts.toBundle());
                        else startActivity(target);
                    } catch (Exception ignored) { }
                }
            });
            return (fopts != null) ? "mode4" : "flag";
        } catch (Exception e) {
            return "error";
        }
    }

    /** 后台检查服务是否已在跑；没有就请 Termux 起来 */
    private void kickServer() {
        new Thread(new Runnable() {
            public void run() {
                if (isServerUp()) return;
                launchTermux();
            }
        }).start();
    }

    private boolean isServerUp() {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(PROBE_URL).openConnection();
            c.setConnectTimeout(700);
            c.setReadTimeout(700);
            c.setRequestMethod("GET");
            return c.getResponseCode() == 200;
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    /** 通过 Termux 官方的 RUN_COMMAND Intent 启动后台服务 */
    private void launchTermux() {
        try {
            Intent i = new Intent();
            i.setClassName("com.termux", "com.termux.app.RunCommandService");
            i.setAction("com.termux.RUN_COMMAND");
            i.putExtra("com.termux.RUN_COMMAND_PATH", TERMUX_PREFIX + "/bin/bash");
            i.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", new String[] { "-c", START_CMD });
            i.putExtra("com.termux.RUN_COMMAND_WORKDIR", TERMUX_HOME);
            i.putExtra("com.termux.RUN_COMMAND_BACKGROUND", true);
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(i);
            else startService(i);
        } catch (Exception e) {
            // Termux 没装 / 没授权 —— 不影响编辑，只是不能运行
        }
    }

    /** 文件选择器返回：把结果转给网页 */
    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req == 1001 && fileCallback != null) {
            fileCallback.onReceiveValue(
                    WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCallback = null;
        } else if (req == 1002 && res == RESULT_OK && data != null && data.getData() != null) {
            final Uri tree = data.getData();
            new Thread(new Runnable() {
                public void run() {
                    final String json = readFolderJson(tree);
                    web.post(new Runnable() {
                        public void run() {
                            try {
                                web.evaluateJavascript(
                                        "window.__onFolder && window.__onFolder(" + json + ");", null);
                            } catch (Throwable ignored) { }
                        }
                    });
                }
            }).start();
        } else {
            super.onActivityResult(req, res, data);
        }
    }

    /** 递归读取 SAF 目录树里的 .cs 文件，编成 JSON。上限 60 个 / 单文件 200KB / 深 6 层 */
    private String readFolderJson(Uri tree) {
        List<String[]> files = new ArrayList<String[]>();
        int[] cut = new int[1];
        try {
            walkTree(tree, DocumentsContract.getTreeDocumentId(tree), files, cut, 0);
        } catch (Throwable ignored) { }
        StringBuilder sb = new StringBuilder("{\"files\":[");
        for (int i = 0; i < files.size(); i++) {
            if (i > 0) sb.append(',');
            sb.append("{\"name\":\"").append(jsonEsc(files.get(i)[0]))
              .append("\",\"code\":\"").append(jsonEscText(files.get(i)[1])).append("\"}");
        }
        sb.append("],\"cut\":").append(cut[0]).append('}');
        return sb.toString();
    }

    private void walkTree(Uri tree, String parentDocId, List<String[]> out, int[] cut, int depth) {
        if (depth > 6 || cut[0] > 200) return;   // cut 超限说明文件夹大得离谱，停止递归
        Cursor c = null;
        try {
            Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, parentDocId);
            c = getContentResolver().query(children, new String[] {
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE }, null, null, null);
            if (c == null) return;
            while (c.moveToNext()) {
                String docId = c.getString(0);
                String name = c.getString(1) == null ? "" : c.getString(1);
                String mime = c.getString(2) == null ? "" : c.getString(2);

                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    walkTree(tree, docId, out, cut, depth + 1);
                    continue;
                }
                if (!name.toLowerCase().endsWith(".cs")) continue;
                if (out.size() >= 60) { cut[0]++; continue; }

                try {
                    java.io.InputStream in = getContentResolver().openInputStream(
                            DocumentsContract.buildDocumentUriUsingTree(tree, docId));
                    ByteArrayOutputStream bos = new ByteArrayOutputStream();
                    byte[] buf = new byte[8192];
                    int n, total = 0;
                    while ((n = in.read(buf)) > 0 && total < 200 * 1024) {
                        bos.write(buf, 0, n);
                        total += n;
                    }
                    in.close();
                    out.add(new String[] { name, bos.toString("UTF-8") });
                } catch (Throwable ignored) { }
            }
        } catch (Throwable ignored) {
        } finally {
            if (c != null) c.close();
        }
    }

    @Override
    public boolean onKeyDown(int code, KeyEvent e) {
        if (code == KeyEvent.KEYCODE_BACK) {
            if (web != null && web.canGoBack()) {
                web.goBack();
                return true;
            }
            askExit();
            return true;
        }
        return super.onKeyDown(code, e);
    }

    /**
     * 退出前先落盘，再按情况提示：
     *   empty   → 没内容，直接退
     *   named   → 已存成文件，静默落盘后直接退（自动保存，不打扰）
     *   unnamed → 只是草稿，问一句要不要先存成文件
     */
    private void askExit() {
        if (web == null) { finish(); return; }
        web.evaluateJavascript(
            "(window.__exitState && window.__exitState()) || 'empty'",
            new ValueCallback<String>() {
                public void onReceiveValue(String v) {
                    String st = v == null ? "empty" : v.replace("\"", "").trim();
                    if (!"unnamed".equals(st)) { finish(); return; }
                    try {
                        new AlertDialog.Builder(MainActivity.this)
                            .setTitle("还没存成文件")
                            .setMessage("当前内容只是草稿（会自动保存，但不在文件列表里）。要先存成文件吗？")
                            .setPositiveButton("去保存", new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface d, int w) {
                                    web.evaluateJavascript(
                                        "window.__openFilePanel && window.__openFilePanel()", null);
                                }
                            })
                            .setNegativeButton("直接退出", new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface d, int w) { finish(); }
                            })
                            .setNeutralButton("取消", null)
                            .show();
                    } catch (Throwable t) {
                        finish();   // 弹窗失败也不能卡住退出
                    }
                }
            });
    }

    /** 切后台/被系统回收前，让网页立即落盘（不等 400ms 防抖） */
    @Override
    protected void onPause() {
        super.onPause();
        try {
            if (web != null) {
                web.evaluateJavascript("window.__flush && window.__flush()", null);
            }
        } catch (Throwable ignored) { }
    }

    @Override
    protected void onDestroy() {
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
