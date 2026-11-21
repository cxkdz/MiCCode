# MiCCode

MiCCode 是一款面向 Android 平板和手机的 C# / Unity 脚本编辑器。编辑、补全和 API 查询可离线使用；如需编译运行，可连接 Termux 或 PC 上的本地服务。

**当前源码版本：v2.10（Android versionCode 21）**

## 获取

APK 发布包请从 [GitHub Releases](https://github.com/cxkdz/MiCCode/releases) 下载。仓库保存源码和符号索引，不跟踪 APK 二进制。

## 功能

| 功能 | 说明 |
|---|---|
| C# / Unity 补全 | 关键字、类型、成员、继承成员及局部变量类型推断 |
| API 查询 | 悬停或移动光标查看签名与说明 |
| Unity API | 协程、常用生命周期回调、UGUI、TextMesh Pro |
| 自动模式识别 | 检测到 MonoBehaviour、Coroutine、UnityEngine 或 TMP 等脚本特征时切换 Unity 补全；可手动切换 |
| 整理缩进 | 整理全文或选中行；快捷键 Alt+Shift+F |
| 文件管理 | 新建、保存、打开、删除、草稿自动保存 |
| 导入与导出 | .cs / .txt、多选、文件夹、GitHub 公开仓库及本地导出 |
| 控制台输入 | 为 Console.ReadLine() 提供逐行输入 |
| 运行代码 | 通过 Termux Mono 或局域网 PC 服务编译并运行纯 C# 程序 |

基本快捷键：Ctrl+S 打开文件面板，Ctrl+Enter 运行代码。

## 两种补全模式

| 模式 | 补全范围 | 是否可运行 |
|---|---|---|
| C# | 常用基础类库与 .NET API | 连接编译服务后可运行 |
| Unity | Unity API、协程、UGUI 与 TextMesh Pro 常用符号 | 不能在 MiCCode 内运行 Unity 脚本 |

Unity 脚本需要 Unity 引擎和 UnityEngine 程序集。MiCCode 提供离线编辑和 API 查询，脚本需拷回 Unity 工程编译。

## 运行编译服务

### Android / Termux

在 Termux 安装依赖并获取仓库：

~~~bash
pkg install git python mono
git clone https://github.com/cxkdz/MiCCode.git ~/MiCCode
cd ~/MiCCode/miccode
python server.py --no-browser
~~~

然后打开 MiCCode。服务默认监听本机 127.0.0.1:8080。若要让 APK 自动启动 Termux 服务，还需启用 Termux 外部命令权限，并把项目目录放在 $HOME/miccode。可用链接指向仓库目录：

~~~bash
ln -s "$HOME/MiCCode/miccode" "$HOME/miccode"
mkdir -p ~/.termux
echo "allow-external-apps=true" >> ~/.termux/termux.properties
termux-wake-lock
~~~

首次使用时，在 Android 设置中允许 MiCCode 在 Termux 环境中运行命令。

### PC / 局域网

在 PC 的 miccode 目录运行：

~~~bash
python server.py --host 0.0.0.0
~~~

在同一局域网的平板浏览器打开 http://PC的局域网IP:8080。请仅在可信网络中使用，不要把服务端口转发到公网。编译服务会执行提交的代码，且不提供用户登录认证；网络上的直接客户端应视为可信用户。

## 索引与补全的边界

当前符号表由 16 个 Unity 模块 XML 与手写补充生成，包含 14,277 条生成器统计索引项和 1,368 个类型。统计项包括 Unity XML 成员及基础类库、生命周期、UGUI / TextMesh Pro 补充。

补全使用离线符号表和轻量语法推断，不是 Roslyn 语言服务器。因此它不会完整解析跨文件引用、泛型约束或重载解析；成员推断主要适用于当前文件中可识别的变量声明。短类型名对应的命名空间也可能存在冲突，自动补 using 后请检查结果。

## 数据与隐私

- 编辑、补全和本地文件管理可离线使用。
- 草稿和文件存放在 WebView 本地存储中。卸载应用或清除应用数据会删除这些内容，重要代码请导出备份。
- 点击运行时，源码会发送到你配置的本机或局域网编译服务执行。
- GitHub 导入访问公开仓库和 GitHub API；不会使用 GitHub 登录凭据。
- 编译服务默认只监听本机。指定 --host 0.0.0.0 后，局域网设备可访问它。

## 构建 APK

构建脚本位于 miccode/apk/build.sh，不使用 Gradle：

~~~bash
cd miccode/apk
bash build.sh
~~~

脚本需要 JDK 21、Android SDK build-tools 34.0.0 和 37.0.0，以及 android-34 platform。脚本开头的 SDK 路径需要按本机环境调整。网页和 symbols.json 会被打包进 APK；修改后需重新构建。

签名密钥在首次构建时生成并被 Git 忽略。保留同一个密钥才能覆盖安装同签名的旧版本；更换密钥后需要先卸载旧 APK。

## 重建符号表

在 miccode 目录运行：

~~~bash
python build_symbols.py "D:/Unity/Editor/Data/Managed/UnityEngine" -o symbols.json
~~~

- build_symbols.py 从 Unity XML 生成类型、成员与命名空间索引。
- bcl_symbols.py 补充常用基础类库、Unity 生命周期函数、UGUI 和 TextMesh Pro 符号。
- 更多 Unity XML 模块可加入 build_symbols.py 顶部的模块列表。

## 许可

仓库目前没有指定开源许可证。使用或再分发前，请联系作者确认许可。
