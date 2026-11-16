# MiCCode

一个跑在浏览器里的 C# 编辑器，带补全和签名提示。可以在安卓平板上离线使用，也可以在 PC 上跑。

## 现在能做到什么

| 能力 | 说明 |
|---|---|
| 两种模式 | 左上角切换「C# 脚本 / Unity 脚本」，只载入对应的 API 集合 |
| 语法高亮 | C# 关键字、字符串、注释、行号、括号自动配对 |
| 关键字补全 | 打 `pu` → 弹出 `public` |
| 类型补全 | 打 `Vec` → 弹出 `Vector3` 等类型名 |
| 成员补全 | 打 `Console.` → 列出 `WriteLine / Write / ReadLine / ReadKey / Clear` |
| 上下文补全（L2） | 先写 `StringBuilder sb = new StringBuilder();`，再打 `sb.` → 列出 StringBuilder 的成员 |
| 继承成员补全 | 类声明为 `: MonoBehaviour` 后，打 `Sta` → 第一候选就是 `StartCoroutine` |
| 悬停签名 | 鼠标停在 `WriteLine` 上 → 浮窗列出全部重载 + 说明；触摸屏长按 450ms 也能触发 |
| 底部签名栏 | 光标停在任何标识符上，底栏显示它的签名和说明 |
| 一键运行 | 点「运行」或按 `Ctrl+Enter`，编译并在右侧显示输出 |
| 发给搭档 | 一键把当前代码复制到剪贴板，切到 AI 粘贴即可（快捷键 `Ctrl+Shift+C`） |
| 自动分屏 | 点「搭子」把 AI 应用放到相邻窗口；列表来自设备真实安装的应用，带真实图标 |
| 文件管理 | 「文件」按钮（`Ctrl+S`）：新建、命名保存、打开、删除；保存时连 C#/Unity 模式一起记录 |
| 导入 .cs | 文件面板的「导入 .cs」：从设备里选 .cs / .txt 文本文件，自动去 BOM、猜模式、进文件列表 |
| 导入 .cs | 「导入 .cs」**支持多选**：长按第一个文件后勾选多个，一次全部导入 |
| 导入文件夹 | 「导入文件夹」：进到目标文件夹后**必须按屏幕底部的「使用此文件夹」**才会生效（Android 目录选择器的固定交互，点文件夹本身只是进入）；递归收所有 .cs，上限 60 个/单文件 200KB |
| GitHub 拉取 | 文件面板「GitHub」：支持仓库/目录/文件三种链接，目录会自动收 .cs（上限 30 个）；公开仓库、需联网 |
| 导出 | 列表每行的 `↓`：APK 写到 `下载/MiCCode/`（重名自动加 (1)），浏览器直接下载 |
| 草稿保护 | 未命名内容自动存 localStorage；已保存的文件编辑时自动同步 |

符号表规模：**13764 条引擎/基础库 API（含 218 条手写 BCL 补充），共 1339 个类型**。

### 两种模式的区别

| | C# 脚本 | Unity 脚本 |
|---|---|---|
| 补全用的 API | 只有基础类库（`Console` `String` `Math` `List` … 11 个类型） | 加上 13000+ 条 UnityEngine API |
| 候选列表 | 干净，打 `p` 只出 4 个关键字 | 打 `p` 会带上 `ParticleSystem` 等 |
| 能不能运行 | 能 | **不能**，只用来写和查签名 |

切换模式时如果编辑器里还是原模板，会自动换成对应模板；如果你已经改了代码，它不会动你的内容。

---

## 怎么跑

### 方式 A：PC 上跑，平板浏览器连（最快，5 分钟）

需要 PC 和平板在同一个 WiFi 下。

```bash
# PC 上，在本目录执行
python server.py --host 0.0.0.0
```

终端会打印类似：

```
地址    http://0.0.0.0:8080
编译器  csc  (C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe)
```

把 `0.0.0.0` 换成 PC 的局域网 IP（`ipconfig` 里 IPv4 地址，一般是 `192.168.x.x`），在平板浏览器里打开：

```
http://192.168.1.100:8080
```

> 编译在 PC 上执行，平板只是显示器。PC 关机/断网就不能用。

### 方式 B：平板本地跑（离线，半小时）

平板装 Termux（**从 F-Droid 或 GitHub Releases 装，别用应用商店的旧版**）：

```bash
pkg update && pkg install python mono -y

# 把整个 miccode 目录传进平板（USB 拷贝 / 或者 PC 上 python -m http.server 让平板下载）

cd ~/miccode
termux-wake-lock          # 关键：不加这个，切出去几分钟服务就被系统杀了
python server.py --no-browser
```

平板浏览器打开 `http://127.0.0.1:8080`。

Termux 里第一次启动会提示找编译器，`mcs` 找到就说明没问题：

```
编译器  mcs  (/data/data/com.termux/files/usr/bin/mcs)
运行器  /data/data/com.termux/files/usr/bin/mono
```

**加个桌面图标**：浏览器里「添加到主屏幕」，点开就是全屏，和 App 没区别。

---

## 崩溃会不会丢代码？

不会全丢，但要分清三种情况：

| 场景 | 结果 |
|---|---|
| App 闪退 / 被系统杀 / 手滑划掉 | **最多丢最后 0.4 秒**的输入（现在切后台会立即落盘，几乎为 0） |
| 卸载 App | **全部丢失**（草稿和文件都存在应用私有存储里） |
| 系统设置里「清除数据」 | **全部丢失** |
| 换设备 / 换浏览器 | 不互通，需要「导出」再导入 |

所以：**日常写练习不用手动保存**；重要代码建议存成文件（进文件列表）并定期「导出」到 `下载/MiCCode/`。

退出时：已存成文件的会静默落盘直接退出；只有**未命名草稿**会弹一次询问（去保存 / 直接退出 / 取消）——因为草稿虽然会自动保存，但不在文件列表里，容易被忽略。

---

## 快速连接 Termux（4 个粘贴块）

在 Termux 里**逐块粘贴**执行（Termux 支持长按粘贴）。已装过 Termux 的从第 1 块开始重复执行也无害。

**块 1 —— 换清华源 + 装包**（解决 `No mirror selected`）：

```bash
echo "deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main" > $PREFIX/etc/apt/sources.list
```

然后**用 apt 而不是 pkg**（重要）：

```bash
apt update && apt install -y python mono unzip
```

> 为什么不接 `pkg`：新版 Termux 的 `pkg` 有自己的镜像配置，**不读 sources.list**。
> 你在 sources.list 里写了清华源，`pkg` 依然会报 `No mirror or mirror group selected`
> 并开始测速（列表全是海外源，很慢）。`apt` 直接读 sources.list，反而一步到位。
>
> 想用 `pkg` 也可以：先 `termux-change-repo` 在图形界面里选清华/中科大，之后 `pkg` 就正常了。

**块 2 —— 开外部调用权限 + 存储授权 + 防杀后台**（弹窗点允许）：

```bash
mkdir -p ~/.termux && echo "allow-external-apps=true" >> ~/.termux/termux.properties && termux-setup-storage && termux-wake-lock
```

**块 3 —— 把 `miccode.zip` 传到平板「下载」目录后**，解压并验证 mono：

```bash
cp ~/storage/downloads/miccode.zip ~/ && cd ~ && unzip -o miccode.zip && cd miccode && echo 'class P{static void Main(){System.Console.WriteLine("OK");}}' > t.cs && mcs t.cs && mono t.exe
```

判据：输出 `OK`。

**块 4 —— 启动服务**：

```bash
python server.py --no-browser
```

判据：横幅里「编译器」一行是 **mcs**。然后打开 MiCCode，右上角徽标会从「离线 · 只能编辑」变成 `mcs · C#7`，「运行」按钮激活。

**系统设置（一次性）**：设置 → 应用 → MiCCode → 权限 → 其他权限 → 打开「在 Termux 环境中运行命令」。这是 APK 点图标自动拉起服务的前提，网页方式用不到。

**ColorOS 防杀后台**：设置 → 电池 → 电池优化 → Termux 设为「不优化」。

---

## 发给搭档 / 自动分屏

输出栏上方有两个按钮：

**「发给搭档」** —— 一键把当前代码复制到剪贴板，切到 DeepSeek / 豆包粘过去就行。

- **快捷键 `Ctrl+Shift+C`**（外接键盘用；软键盘上直接点按钮）
- 复制的是**编辑器全文**，不是选中部分

**「选搭子」→ 绑定后变成应用名 ▾** —— 点一下，让那个应用在相邻窗口打开（左边写代码、右边问 AI）。

- **点按钮主体**：直接分屏到旁边
- **点右侧 `▾`**：弹出换搭子列表 —— 这个入口永远可靠，不依赖长按
- **长按按钮**：同样弹列表（备用入口）。已带位移容差，手指轻微滑动不会打断
- 列表来自设备上**真实安装的应用**（带真实图标，支持搜索），选中即记住
- 每行右侧的 `＋` 可以给它换一张自定义图标
- 绑定的应用被卸载后，点分屏会提示失效并自动清掉绑定

### 关于分屏的左右位置

分屏请求的是「搭子放右/下半，MiCCode 留左/上半」（`WINDOWING_MODE_SPLIT_SCREEN_SECONDARY`）。

但要知道：**原生 Android 7~11 按请求执行；Android 12L 以后分屏窗口管理被厂商接管**（ColorOS 尤其如此），位置可能被系统重新安排。如果你的设备上搭子出现在左边，用**分屏中间分隔条上的交换按钮**（两条竖线图标）对调一下即可，一次设置系统会记住。

### 为什么这件事只有 APK 能做

1. **列应用**：网页没有 `PackageManager`。APK 在 manifest 里声明了 `<queries>` 的 MAIN/LAUNCHER，Android 11+ 才允许 `queryIntentActivities` 看到全部桌面应用。
2. **取图标**：靠系统的 `loadIcon()` 解析，**不需要读 `/data/app` 下的 APK 文件**（那里被 SELinux 锁着，Termux 也读不到）。
3. **真分屏**：`FLAG_ACTIVITY_LAUNCH_ADJACENT` 必须由**正在全屏的那个 Activity 自己** `startActivity` 发出。用 Termux 的 `am start` 发起时，发起方是 shell，shell 不在任何任务栈里，系统找不到「当前全屏应用」这个上下文，只会把对方开成悬浮窗。

> 所以：**自动分屏不需要 Termux。** Termux 只负责编译，和分屏无关。
>
> 前提是点按钮时 MiCCode 自己是全屏的。如果你把它开成了小窗，系统没有可分割的容器，对方也会变悬浮窗。

---

## 打包成 APK

`apk/MiCCode.apk` 是已经打好签名的安装包（718 KB，v1.5 / versionCode 6）。

### 界面在 APK 里，编译在 Termux 里

**不装 Termux 也能用这个 App。** 界面、符号表、补全逻辑全部打包在 APK 内部：

| 没有 Termux | 有 Termux |
|---|---|
| 能写代码、能补全（含继承成员）、能悬停看签名、能切 Unity / C# 模式、草稿自动保存 | 以上全部 + 能编译运行 |
| 点「运行」会告诉你为什么跑不了、怎么才能跑 | 「运行」100ms 出结果 |

实现方式：页面从虚拟域名 `http://miccode.local/` 加载，这个域名被 WebView 的 `shouldInterceptRequest` 拦截，直接从 APK 的 `assets/www/` 读文件——不经过任何网络。只有 `/api/*` 请求才走 `127.0.0.1:8080`，那时才需要 Termux。

### 为什么不能把 Termux 整个打包进去

这条路查证过，是堵死的。Termux 官方 FAQ 原话：

> All binaries have some Termux-specific paths hardcoded. If your project is going to use a different application package name, you will have to recompile all necessary packages and their dependencies.

更具体地说，Termux 每个二进制都把安装前缀**编译进了三个地方**：ELF interpreter、rpath、以及每个脚本的 shebang。上游包都是按 `/data/data/com.termux/files/usr` 构建的，换个包名就全解析不到。社区做法（如 `tobiterm-bootstrap`）是**用 `TERMUX_APP__PACKAGE_NAME` 重新构建整个工具链**——包括 mono，那是几个 GB 的编译工程。

所以在「APK 自动起服务」和「不装 Termux」之间，只能选前者；但界面本身不需要服务，这部分已经做到完全独立。

### 它会做什么

启动顺序：

1. **立刻加载界面**（从 assets，无需任何服务）
2. 后台探测 `127.0.0.1:8080/api/info`
3. 不通 → 用 Termux 官方的 **RUN_COMMAND Intent** 让 Termux 执行 `cd ~/miccode && python server.py --no-browser`
4. 前端每 5 秒重试一次，最多 1 分钟——服务起来后自动从「离线」变成「可运行」

也就是说：**装好后第一次可能要等一下，之后点图标就自动进**。

### 首次配置（只有一次，三步）

1. 装 Termux（F-Droid / GitHub Releases），然后：
   ```bash
   pkg install python mono -y
   ```
2. 把 `miccode` 文件夹放到 Termux 家目录，再打开外部调用权限：
   ```bash
   mkdir -p ~/.termux
   echo "allow-external-apps=true" >> ~/.termux/termux.properties
   ```
3. 系统设置 → 应用 → **MiCCode** → 权限 → 其他权限 → 打开「**在 Termux 环境中运行命令**」

完成后点 MiCCode 图标，它会自己把服务拉起来。

> 第 2、3 步是 Termux 的强制安全设计，绕不过去：一个 App 想在你的终端里执行命令，必须你亲自点过同意。

### 装不上 / 连不上的排查

| 现象 | 原因 |
|---|---|
| 点图标一直停在引导页 | Termux 没装、`allow-external-apps` 没配、或权限没授予 |
| 昨天能用今天不行 | Termux 被系统杀了。去电池优化里把 Termux 和 MiCCode 都设为「不受限制」 |
| 打开是白屏不是引导页 | Termux 服务在跑但页面加载失败，往下拉看是否 8080 被占用 |

### 重新构建

```bash
cd apk && bash build.sh
```

脚本直接调 `aapt2` / `javac` / `d8` / `zipalign` / `apksigner`，**完全不需要 Gradle**。用到的工具都是你已装的 Android Studio 自带的：

| 用途 | 路径 |
|---|---|
| JDK 21 | `C:\Program Files\Android\Android Studio\jbr` |
| build-tools | `D:\AndroidStudio\build-tools\34.0.0`（打包）+ `37.0.0`（d8） |
| platform | `D:\AndroidStudio\platforms\android-34` |

> 为什么 d8 要用 37.0.0：build-tools 34 的 d8 在 JDK 21 上会抛 `NullPointerException`，换新版就好。

改包名、minSdk、图标替换都在 `build.sh` 顶部和 `res/mipmap-*` 里。

### 签名密钥

首次构建会生成 `apk/miccode.keystore`（口令 `miccode2026`）。

**这个文件务必留着。** 以后要升级这个 App，必须用同一个密钥签名；换了密钥，安装时会报「签名不一致」，只能先卸载旧版（本地数据会一起丢）。

---

## 需要知道的限制

### 0. AI 能替你审代码，但替不了跑代码

「发给搭档」按钮会把当前代码复制到剪贴板，方便你粘给 DeepSeek / 豆包问它。但请记住一件事：**AI 是在推测运行结果，不是真的执行。**

几个它常错的地方：

| 代码 | 真实输出 | AI 常答 |
|---|---|---|
| `Math.Round(2.5)` | `2`（银行家舍入） | 3 |
| `0.1 + 0.2 == 0.3` | `false` | true |
| `int.MaxValue + 1` | `-2147483648`（回绕） | 2147483648 |
| `for(int i=0;i<10;i++){i++;}` | 循环 5 次 | 10 次 |

而且它猜错时**不会告诉你它不确定**，语气一样笃定。

所以：**AI 用来审（语法、思路），真跑用来验（输出、边界）**。前者能省一半时间，后者省不掉。

### 1. 编译器版本不同

| 环境 | 编译器 | 支持的 C# 版本 | 能写 `$"…"` 插值吗 |
|---|---|---|---|
| 平板（Termux） | mcs (Mono) | C# 7 | 能 |
| PC | csc (.NET Framework 4.0) | C# 5 | 不能 |

右上角会显示当前用的是哪个编译器。PC 上写插值字符串会报 `CS1056`，程序会自动提示你改用 `string.Format` 或字符串拼接。

### 2. 不能编译 Unity 脚本

没有 `UnityEngine.dll` 的运行时，`using UnityEngine;` 会编译失败。但**补全和签名照常可用**——符号表里有 13000+ 条 Unity API，写 `Time.` `Vector3.` `Mathf.` 都有提示，只是跑不起来。

### 3. 补全的边界

成员补全靠"局部变量表"：只解析当前文件里写过的 `Foo x = ...` 和 `var x = new Foo(...)`。

```csharp
StringBuilder sb = new StringBuilder();
sb.          // ✅ 能列出 Append / AppendLine / ToString ...

var list = new List<int>();
list.        // ✅ 能列出 Add / Remove / Count ...

foo.         // ❌ 如果 foo 的类型不是在上面那种写法里声明的，推断不出来
```

跨文件、方法返回值类型、泛型推断都解析不了——那是 Roslyn 的活，安卓上做不到。

---

## 文件说明

```
miccode/
├── index.html        编辑器界面（CodeMirror 5 + 补全 + 悬停 + 搭子分屏）
├── server.py         本地服务（静态文件 + 编译执行 + 分屏），零依赖
├── symbols.json      符号表（13000+ Unity + 218 BCL，含类型→命名空间映射）
├── build_symbols.py  从 Unity 的 XML 文档重新生成符号表
├── bcl_symbols.py    手写的基础类库符号（Console / String / Math / List ...）
├── manifest.json     PWA 配置（添加到主屏时的名称、图标、全屏模式）
├── icon-192.png      桌面图标 192×192
├── icon-512.png      桌面图标 512×512
├── favicon-32.png    浏览器标签页图标
└── vendor/           CodeMirror 资源，已本地化，断网可用
```

### 更新符号表

Unity 升级或换版本后，重新生成：

```bash
python build_symbols.py "D:/unity/2022.3.48t7/Editor/Data/Managed/UnityEngine"
```

想收录更多模块（比如 UI、XR），改 `build_symbols.py` 顶部的 `MODULES` 列表。
想收录 `UnityEditor.*`（编辑器扩展开发用），把 `INCLUDE_EDITOR` 改成 `True`。

### 扩充基础类库

`bcl_symbols.py` 里目前手写了 11 个类型。缺什么就往对应的列表里加一条：

```python
STRING = [
    ("Length", [""], "字符串长度（int）"),
    ("你的方法", ["(参数类型 参数名)"], "说明"),
    ...
]
```

改完重跑 `build_symbols.py` 即可。
