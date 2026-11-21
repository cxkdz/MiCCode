#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bcl_symbols.py — .NET 基础类库（BCL）核心符号表

为什么手写：Unity 的 XML 文档只覆盖 UnityEngine，不含 System.*。
为什么够用：练习场景里 90% 的 BCL 调用集中在下面这些类型上。

以后可以在平板用 mono 反射导出完整版替换本文件（见 gen_bcl.cs）。
"""

# 每条：(成员名, [重载签名], 说明)
# 签名用 C# 写法，空签名表示属性/字段

CONSOLE = [
    ("WriteLine", ["()", "(string value)", "(int value)", "(float value)",
                   "(double value)", "(bool value)", "(char value)", "(object value)",
                   "(string format, params object[] args)"],
     "把内容写到标准输出并换行"),
    ("Write", ["(string value)", "(int value)", "(object value)"], "写到标准输出，不换行"),
    ("ReadLine", ["()"], "读一行输入，返回 string（无输入时为 null）"),
    ("ReadKey", ["()"], "读一个按键，返回值有 KeyChar 属性"),
    ("Clear", ["()"], "清屏"),
    ("WriteLine", ["(string format, object arg0)"], "格式化输出：Console.WriteLine(\"x={0}\", x)"),
]

STRING = [
    ("Length", [""], "字符串长度（int）"),
    ("Substring", ["(int startIndex)", "(int startIndex, int length)"], "取子串"),
    ("IndexOf", ["(string value)", "(char value)"], "查找位置，找不到返回 -1"),
    ("LastIndexOf", ["(string value)", "(char value)"], "从后往前找"),
    ("Replace", ["(string oldValue, string newValue)"], "替换（旧版 .NET 里返回新字符串，不改自己）"),
    ("Split", ["(params char[] separator)", "(char separator)"], "按分隔符切成 string[]"),
    ("ToUpper", ["()"], "转大写"),
    ("ToLower", ["()"], "转小写"),
    ("Trim", ["()"], "去掉首尾空白"),
    ("Contains", ["(string value)"], "是否包含子串"),
    ("IsNullOrWhiteSpace", ["(string value)"], "静态：null、空串或全空白都返回 true"),
    ("StartsWith", ["(string value)"], "是否以某串开头"),
    ("EndsWith", ["(string value)"], "是否以某串结尾"),
    ("ToString", ["()"], "转成字符串"),
    ("ToCharArray", ["()"], "转成 char[]"),
    ("PadLeft", ["(int totalWidth)", "(int totalWidth, char paddingChar)"], "左补位"),
    ("PadRight", ["(int totalWidth)", "(int totalWidth, char paddingChar)"], "右补位"),
    ("Insert", ["(int startIndex, string value)"], "插入"),
    ("Remove", ["(int startIndex)", "(int startIndex, int count)"], "删除"),
    ("Equals", ["(string value)"], "比较内容"),
    ("CompareTo", ["(string strB)"], "按字典序比较"),
]

STRING_STATIC = [
    ("Format", ["(string format, object arg0)", "(string format, params object[] args)"],
     "静态：按 {0} {1} 占位符拼字符串"),
    ("IsNullOrEmpty", ["(string value)"], "静态：null 或空串都返回 true"),
    ("Join", ["(string separator, string[] value)", "(string separator, params string[] values)"],
     "静态：把数组拼成一个串"),
    ("Concat", ["(string str0, string str1)", "(params string[] values)"], "静态：拼接"),
]

MATH = [
    ("Abs", ["(float value)", "(int value)"], "绝对值"),
    ("Max", ["(float a, float b)", "(int a, int b)"], "较大值"),
    ("Min", ["(float a, float b)", "(int a, int b)"], "较小值"),
    ("Sqrt", ["(float d)"], "平方根"),
    ("Pow", ["(float x, float y)"], "x 的 y 次方"),
    ("Round", ["(float f)", "(float f, int digits)"], "四舍五入（注意：.5 取偶）"),
    ("Floor", ["(float f)"], "向下取整"),
    ("Ceiling", ["(float f)"], "向上取整"),
    ("Sign", ["(float value)"], "符号：-1 / 0 / 1"),
    ("Clamp", ["(float value, float min, float max)"], "夹取到区间内"),
    ("Lerp", ["(float a, float b, float t)"], "线性插值"),
    ("Sin", ["(float f)"], "正弦（弧度）"),
    ("Cos", ["(float f)"], "余弦（弧度）"),
    ("PI", [""], "圆周率常量"),
    ("Deg2Rad", [""], "角度转弧度的系数"),
    ("Rad2Deg", [""], "弧度转角度的系数"),
]

LIST = [
    ("Add", ["(T item)"], "末尾添加"),
    ("AddRange", ["(IEnumerable<T> collection)"], "批量添加"),
    ("Insert", ["(int index, T item)"], "在指定位置插入"),
    ("Remove", ["(T item)"], "删除第一个匹配项，返回 bool"),
    ("RemoveAt", ["(int index)"], "按索引删除"),
    ("Clear", ["()"], "清空"),
    ("Contains", ["(T item)"], "是否包含"),
    ("IndexOf", ["(T item)"], "找索引，找不到 -1"),
    ("Sort", ["()"], "排序（元素需可比较）"),
    ("Reverse", ["()"], "反序"),
    ("ToArray", ["()"], "转成数组"),
    ("ForEach", ["(Action<T> action)"], "对每个元素执行动作"),
    ("GetEnumerator", ["()"], "返回迭代器（foreach 底层用的就是它）"),
    ("Count", [""], "元素个数"),
    ("Capacity", [""], "内部容量"),
    ("new", ["()", "(int capacity)", "(IEnumerable<T> collection)"], "构造"),
]

DICT = [
    ("Add", ["(TKey key, TValue value)"], "添加，键已存在会抛异常"),
    ("TryGetValue", ["(TKey key, out TValue value)"], "安全取值，返回 bool"),
    ("ContainsKey", ["(TKey key)"], "是否含键"),
    ("ContainsValue", ["(TValue value)"], "是否含值"),
    ("Remove", ["(TKey key)"], "按键删除"),
    ("Clear", ["()"], "清空"),
    ("Count", [""], "键值对数量"),
    ("Keys", [""], "所有键"),
    ("Values", [""], "所有值"),
    ("new", ["()"], "构造"),
]

STRINGBUILDER = [
    ("Append", ["(string value)", "(int value)", "(object value)", "(char value)"], "追加"),
    ("AppendLine", ["()", "(string value)"], "追加并换行"),
    ("AppendFormat", ["(string format, params object[] args)"], "格式化追加"),
    ("ToString", ["()"], "转成 string"),
    ("Clear", ["()"], "清空"),
    ("Insert", ["(int index, string value)"], "插入"),
    ("Remove", ["(int startIndex, int length)"], "删除"),
    ("Replace", ["(string oldValue, string newValue)"], "替换（这个是真的改自己）"),
    ("Length", [""], "当前长度"),
    ("new", ["()", "(int capacity)", "(string value)"], "构造"),
]

ARRAY = [
    ("Length", [""], "元素个数"),
    ("GetLength", ["(int dimension)"], "指定维度的长度"),
    ("Clone", ["()"], "浅拷贝"),
    ("Sort", ["(T[] array)"], "静态：原地排序"),
    ("Reverse", ["(T[] array)"], "静态：原地反序"),
    ("IndexOf", ["(T[] array, T value)"], "静态：查找索引"),
    ("Resize", ["(ref T[] array, int newSize)"], "静态：改大小（会新建数组）"),
    ("Copy", ["(T[] sourceArray, T[] destinationArray, int length)"], "静态：复制"),
]

RANDOM = [
    ("Next", ["()", "(int maxValue)", "(int minValue, int maxValue)"], "随机整数，上界不含"),
    ("NextDouble", ["()"], "0.0 ~ 1.0 之间的随机小数"),
    ("NextBytes", ["(byte[] buffer)"], "填充随机字节"),
    ("new", ["()", "(int seed)"], "构造（seed 相同则序列相同）"),
]

CONVERT = [
    ("ToInt32", ["(string value)", "(float value)"], "静态：转 int"),
    ("ToDouble", ["(string value)"], "静态：转 double"),
    ("ToString", ["(int value)", "(float value)"], "静态：转字符串"),
    ("ToBoolean", ["(string value)"], "静态：转 bool"),
]

INT_MEMBERS = [
    ("Parse", ["(string s)"], "静态：字符串转 int，失败抛异常"),
    ("TryParse", ["(string s, out int result)"], "静态：安全转换，返回 bool"),
    ("ToString", ["()", "(string format)"], "转字符串"),
    ("MaxValue", [""], "int 最大值 2147483647"),
    ("MinValue", [""], "int 最小值"),
]

FLOAT_MEMBERS = [
    ("Parse", ["(string s)"], "静态：字符串转 float"),
    ("TryParse", ["(string s, out float result)"], "静态：安全转换"),
    ("ToString", ["()", "(string format)"], "转字符串，如 f2 保留两位"),
]

# ── 迭代器接口（协程的返回类型就是它，System.Collections 命名空间）──
IENUMERATOR = [
    ("MoveNext", ["()"], "前进到下一个元素，返回 bool。协程就是被 Unity 每帧调用 MoveNext 驱动的"),
    ("Reset", ["()"], "重置到初始位置（协程里几乎不用）"),
    ("Current", [""], "当前元素（object 类型）"),
]

IENUMERABLE = [
    ("GetEnumerator", ["()"], "返回一个迭代器，foreach 底层调的就是它"),
]

IDISPOSABLE = [
    ("Dispose", ["()"], "释放资源，using 语句块结束时自动调用"),
]

# ── 线程（System.Threading）──
# 注意：Unity 的 API 几乎全部只能在主线程调用，子线程只能做纯计算
THREAD = [
    ("Start", ["()"], "启动线程。注意：Unity API 只有主线程能调，子线程只能做纯计算"),
    ("Join", ["()", "(int millisecondsTimeout)"], "等这个线程跑完再继续"),
    ("Sleep", ["(int millisecondsTimeout)"], "静态：当前线程暂停指定毫秒（Unity 里别在主线程用，会卡死画面）"),
    ("IsAlive", [""], "是否还在运行"),
    ("IsBackground", [""], "true = 后台线程，主程序退出时会被直接终止"),
    ("Name", [""], "线程名，调试时好认"),
    ("CurrentThread", [""], "静态：当前正在跑的这个线程"),
    ("Priority", [""], "调度优先级"),
]

OBJECT = [
    ("ToString", ["()"], "转成字符串，子类常重写它"),
    ("Equals", ["(object obj)"], "相等判断（string 重写成了内容比较）"),
    ("GetHashCode", ["()"], "哈希码，Dictionary/HashSet 靠它定位"),
    ("GetType", ["()"], "运行时类型信息，.Name 取类型名"),
]

ACTION = [
    ("Invoke", ["()", "(T arg)"], "调用它指向的方法（Action 无返回值）"),
]

FUNC = [
    ("Invoke", ["(T arg)"], "调用它指向的方法，返回 TResult"),
]

EXCEPTION = [
    ("Message", [""], "错误信息"),
    ("StackTrace", [""], "出错位置的调用栈"),
    ("InnerException", [""], "包裹在里面的那个异常"),
    ("ToString", ["()"], "含类型名和 Message 的描述"),
    ("new", ["(string message)"], "构造"),
]

DATETIME = [
    ("Now", [""], "静态：当前本地时间"),
    ("UtcNow", [""], "静态：当前 UTC 时间"),
    ("Today", [""], "静态：今天 0 点"),
    ("Year", [""], "年"),
    ("Month", [""], "月"),
    ("Day", [""], "日"),
    ("Hour", [""], "时"),
    ("Minute", [""], "分"),
    ("Second", [""], "秒"),
    ("DayOfWeek", [""], "星期几（枚举）"),
    ("AddDays", ["(double value)"], "加几天，负数就是往前"),
    ("AddMonths", ["(int months)"], "加几个月"),
    ("AddMinutes", ["(double value)"], "加几分钟"),
    ("ToString", ["()", "(string format)"], "格式化，如 yyyy-MM-dd HH:mm:ss"),
    ("Parse", ["(string s)"], "静态：字符串转时间"),
]

TIMESPAN = [
    ("Days", [""], "天部分"),
    ("Hours", [""], "时部分"),
    ("Minutes", [""], "分部分"),
    ("Seconds", [""], "秒部分"),
    ("TotalDays", [""], "总长折算成天（double）"),
    ("TotalHours", [""], "总长折算成小时"),
    ("TotalMinutes", [""], "总长折算成分钟"),
    ("TotalSeconds", [""], "总长折算成秒（计时常用）"),
    ("TotalMilliseconds", [""], "总长折算成毫秒"),
    ("FromSeconds", ["(double value)"], "静态：由秒构造"),
    ("FromMilliseconds", ["(double value)"], "静态：由毫秒构造"),
    ("ToString", ["()"], "如 00:01:30"),
]

QUEUE = [
    ("Enqueue", ["(T item)"], "入队（排到队尾）"),
    ("Dequeue", ["()"], "出队（取队首并移除，空队会抛异常）"),
    ("Peek", ["()"], "看队首但不移除"),
    ("Contains", ["(T item)"], "是否包含"),
    ("Clear", ["()"], "清空"),
    ("ToArray", ["()"], "转成数组"),
    ("Count", [""], "元素个数"),
]

STACK = [
    ("Push", ["(T item)"], "压栈"),
    ("Pop", ["()"], "弹栈（取栈顶并移除，空栈会抛异常）"),
    ("Peek", ["()"], "看栈顶但不移除"),
    ("Contains", ["(T item)"], "是否包含"),
    ("Clear", ["()"], "清空"),
    ("ToArray", ["()"], "转成数组"),
    ("Count", [""], "元素个数"),
]

HASHSET = [
    ("Add", ["(T item)"], "添加，已存在时返回 false 不重复"),
    ("Remove", ["(T item)"], "删除"),
    ("Contains", ["(T item)"], "是否包含（比 List 快）"),
    ("Clear", ["()"], "清空"),
    ("ToArray", ["()"], "转成数组"),
    ("Count", [""], "元素个数"),
]

KEYVALUEPAIR = [
    ("Key", [""], "键"),
    ("Value", [""], "值"),
    ("ToString", ["()"], "如 [a, 1]"),
]

DOUBLE_MEMBERS = [
    ("Parse", ["(string s)"], "静态：字符串转 double"),
    ("TryParse", ["(string s, out double result)"], "静态：安全转换"),
    ("ToString", ["()", "(string format)"], "转字符串，如 f2 保留两位"),
    ("MaxValue", [""], "double 最大值"),
    ("MinValue", [""], "double 最小值"),
    ("IsNaN", ["(double d)"], "静态：是不是 NaN（NaN != NaN，判断要用它）"),
]

LONG_MEMBERS = [
    ("Parse", ["(string s)"], "静态：字符串转 long"),
    ("TryParse", ["(string s, out long result)"], "静态：安全转换"),
    ("ToString", ["()"], "转字符串"),
    ("MaxValue", [""], "long 最大值 9223372036854775807"),
    ("MinValue", [""], "long 最小值"),
]

CHAR_MEMBERS = [
    ("IsDigit", ["(char c)"], "静态：是不是数字字符"),
    ("IsLetter", ["(char c)"], "静态：是不是字母"),
    ("IsWhiteSpace", ["(char c)"], "静态：是不是空白"),
    ("ToUpper", ["(char c)"], "静态：转大写"),
    ("ToLower", ["(char c)"], "静态：转小写"),
    ("ToString", ["()"], "转成 string"),
]

BOOL_MEMBERS = [
    ("Parse", ["(string s)"], "静态：\"True\"/\"False\" 转 bool"),
    ("TryParse", ["(string s, out bool result)"], "静态：安全转换"),
    ("ToString", ["()"], "转成 \"True\"/\"False\""),
]

PATH_MEMBERS = [
    ("Combine", ["(string path1, string path2)", "(params string[] paths)"], "静态：安全拼接路径"),
    ("GetFileName", ["(string path)"], "静态：取文件名"),
    ("GetFileNameWithoutExtension", ["(string path)"], "静态：取不含扩展名的文件名"),
    ("GetDirectoryName", ["(string path)"], "静态：取目录部分"),
    ("GetExtension", ["(string path)"], "静态：取扩展名，包含点号"),
    ("ChangeExtension", ["(string path, string extension)"], "静态：替换扩展名"),
    ("GetFullPath", ["(string path)"], "静态：转成绝对路径"),
    ("GetTempPath", ["()"], "静态：取临时目录"),
    ("GetTempFileName", ["()"], "静态：创建临时文件并返回路径"),
    ("DirectorySeparatorChar", [""], "目录分隔符"),
    ("AltDirectorySeparatorChar", [""], "备用目录分隔符"),
]

FILE_MEMBERS = [
    ("Exists", ["(string path)"], "静态：文件是否存在"),
    ("ReadAllText", ["(string path)", "(string path, Encoding encoding)"], "静态：读取整个文本文件"),
    ("WriteAllText", ["(string path, string contents)", "(string path, string contents, Encoding encoding)"], "静态：写入整个文本文件"),
    ("AppendAllText", ["(string path, string contents)"], "静态：追加文本到文件"),
    ("ReadAllLines", ["(string path)"], "静态：逐行读取，返回 string[]"),
    ("WriteAllLines", ["(string path, string[] contents)"], "静态：逐行写入"),
    ("AppendAllLines", ["(string path, IEnumerable<string> contents)"], "静态：逐行追加"),
    ("ReadAllBytes", ["(string path)"], "静态：读取全部字节"),
    ("WriteAllBytes", ["(string path, byte[] bytes)"], "静态：写入全部字节"),
    ("Copy", ["(string sourceFileName, string destFileName)", "(string sourceFileName, string destFileName, bool overwrite)"], "静态：复制文件"),
    ("Move", ["(string sourceFileName, string destFileName)"], "静态：移动或重命名文件"),
    ("Delete", ["(string path)"], "静态：删除文件；文件不存在时不抛异常"),
    ("OpenRead", ["(string path)"], "静态：以只读方式打开文件流"),
    ("OpenWrite", ["(string path)"], "静态：打开文件用于写入"),
]

DIRECTORY_MEMBERS = [
    ("Exists", ["(string path)"], "静态：目录是否存在"),
    ("CreateDirectory", ["(string path)"], "静态：创建目录及缺失的父目录"),
    ("Delete", ["(string path)", "(string path, bool recursive)"], "静态：删除目录，可递归删除"),
    ("GetFiles", ["(string path)", "(string path, string searchPattern)"], "静态：枚举文件路径"),
    ("GetDirectories", ["(string path)", "(string path, string searchPattern)"], "静态：枚举子目录路径"),
    ("GetFileSystemEntries", ["(string path)"], "静态：枚举文件和目录"),
    ("GetCurrentDirectory", ["()"], "静态：获取当前工作目录"),
    ("SetCurrentDirectory", ["(string path)"], "静态：设置当前工作目录"),
    ("GetParent", ["(string path)"], "静态：获取父目录"),
    ("Move", ["(string sourceDirName, string destDirName)"], "静态：移动目录"),
]

STREAM_READER = [
    ("ReadLine", ["()"], "读一行；到末尾时返回 null"),
    ("ReadToEnd", ["()"], "读完剩余内容"),
    ("Read", ["()", "(char[] buffer, int index, int count)"], "读取字符"),
    ("Peek", ["()"], "查看下一个字符但不消费"),
    ("Close", ["()"], "关闭读取器"),
    ("Dispose", ["()"], "释放读取器"),
    ("new", ["(string path)", "(string path, Encoding encoding)"], "构造：从文件读取文本"),
]

STREAM_WRITER = [
    ("Write", ["(string value)", "(char value)", "(object value)"], "写入内容"),
    ("WriteLine", ["()", "(string value)"], "写入内容并换行"),
    ("Flush", ["()"], "立即写出缓冲内容"),
    ("Close", ["()"], "关闭写入器"),
    ("Dispose", ["()"], "释放写入器"),
    ("new", ["(string path)", "(string path, bool append)"], "构造：写入文件，可选择追加"),
]

MEMORY_STREAM = [
    ("ToArray", ["()"], "返回流内容的副本"),
    ("GetBuffer", ["()"], "返回内部缓冲区"),
    ("Read", ["(byte[] buffer, int offset, int count)"], "读取字节"),
    ("Write", ["(byte[] buffer, int offset, int count)"], "写入字节"),
    ("Seek", ["(long offset, SeekOrigin origin)"], "移动读写位置"),
    ("SetLength", ["(long value)"], "修改流长度"),
    ("Flush", ["()"], "刷新缓冲区"),
    ("Position", [""], "当前读写位置"),
    ("Length", [""], "流长度"),
    ("new", ["()", "(int capacity)", "(byte[] buffer)"], "构造内存流"),
]

TASK = [
    ("IsCompleted", [""], "任务是否已完成"),
    ("IsCanceled", [""], "任务是否已取消"),
    ("IsFaulted", [""], "任务是否以异常结束"),
    ("Status", [""], "当前任务状态"),
    ("Wait", ["()", "(int millisecondsTimeout)"], "等待任务完成"),
    ("Run", ["(Action action)", "(Func<Task> function)"], "静态：在线程池执行任务"),
    ("Delay", ["(int millisecondsDelay)"], "静态：异步等待指定毫秒"),
    ("WhenAll", ["(params Task[] tasks)"], "静态：等待所有任务完成"),
    ("WhenAny", ["(params Task[] tasks)"], "静态：等待任一任务完成"),
]

REGEX = [
    ("IsMatch", ["(string input, string pattern)"], "静态：判断是否匹配正则"),
    ("Match", ["(string input, string pattern)"], "静态：查找第一个匹配"),
    ("Matches", ["(string input, string pattern)"], "静态：查找全部匹配"),
    ("Replace", ["(string input, string pattern, string replacement)"], "静态：替换匹配内容"),
    ("Split", ["(string input, string pattern)"], "静态：按正则拆分"),
    ("Escape", ["(string input)"], "静态：转义正则特殊字符"),
    ("new", ["(string pattern)", "(string pattern, RegexOptions options)"], "构造正则"),
]

GUID = [
    ("NewGuid", ["()"], "静态：创建新的 GUID"),
    ("Parse", ["(string input)"], "静态：解析 GUID，失败时抛异常"),
    ("TryParse", ["(string input, out Guid result)"], "静态：安全解析 GUID"),
    ("ToString", ["()", "(string format)"], "格式化 GUID"),
    ("Empty", [""], "全零 GUID"),
]

# ── 常用 Unity UI 包 API（package XML 通常不随 Editor 一起安装，手写补全）──
SELECTABLE = [
    ("interactable", [""], "是否允许交互"),
    ("IsInteractable", ["()"], "当前是否可交互（也检查父级 CanvasGroup）"),
    ("Select", ["()"], "选中此 UI 控件"),
    ("OnSelect", ["(BaseEventData eventData)"], "控件被选中时调用"),
    ("OnDeselect", ["(BaseEventData eventData)"], "控件取消选中时调用"),
    ("OnPointerClick", ["(PointerEventData eventData)"], "收到鼠标或触摸点击时调用"),
    ("OnSubmit", ["(BaseEventData eventData)"], "收到键盘/手柄确认时调用"),
    ("IsPressed", ["()"], "当前是否处于按下状态"),
]

GRAPHIC = [
    ("color", [""], "UI 图形颜色"),
    ("raycastTarget", [""], "是否接收 UI 射线检测"),
    ("enabled", [""], "是否启用该组件"),
]

BUTTON = [
    ("onClick", [""], "点击事件；用 onClick.AddListener(...) 注册回调"),
]

IMAGE = [
    ("sprite", [""], "显示的精灵图片"),
    ("overrideSprite", [""], "临时覆盖显示的精灵"),
    ("type", [""], "图片类型：Simple / Sliced / Tiled / Filled"),
    ("preserveAspect", [""], "是否保持图片宽高比"),
    ("fillAmount", [""], "Filled 类型的填充比例（0 到 1）"),
    ("fillMethod", [""], "填充方向类型"),
    ("SetNativeSize", ["()"], "按精灵原始尺寸设置 RectTransform"),
]

RAW_IMAGE = [
    ("texture", [""], "显示的纹理"),
    ("uvRect", [""], "纹理 UV 区域"),
    ("SetNativeSize", ["()"], "按纹理原始尺寸设置 RectTransform"),
]

TEXT = [
    ("text", [""], "显示文本"),
    ("font", [""], "使用的字体"),
    ("fontSize", [""], "字号"),
    ("fontStyle", [""], "字体样式"),
    ("alignment", [""], "文本对齐方式"),
    ("horizontalOverflow", [""], "水平溢出处理"),
    ("verticalOverflow", [""], "垂直溢出处理"),
    ("supportRichText", [""], "是否解析富文本标签"),
    ("resizeTextForBestFit", [""], "是否自动调整字号以适应区域"),
]

TOGGLE = [
    ("isOn", [""], "当前是否勾选"),
    ("onValueChanged", [""], "勾选状态变化事件"),
    ("SetIsOnWithoutNotify", ["(bool value)"], "设置状态但不触发事件"),
]

SLIDER = [
    ("value", [""], "当前数值"),
    ("minValue", [""], "最小值"),
    ("maxValue", [""], "最大值"),
    ("wholeNumbers", [""], "是否限制为整数"),
    ("onValueChanged", [""], "数值变化事件"),
    ("SetValueWithoutNotify", ["(float input)"], "设置数值但不触发事件"),
]

INPUT_FIELD = [
    ("text", [""], "输入框当前文本"),
    ("placeholder", [""], "占位文本组件"),
    ("characterLimit", [""], "允许输入的最大字符数"),
    ("contentType", [""], "输入内容类型"),
    ("onValueChanged", [""], "文本变化事件"),
    ("onEndEdit", [""], "结束编辑事件"),
    ("SetTextWithoutNotify", ["(string input)"], "设置文本但不触发事件"),
    ("ActivateInputField", ["()"], "激活输入并打开软键盘"),
]

DROPDOWN = [
    ("options", [""], "下拉选项列表"),
    ("value", [""], "当前选中索引"),
    ("onValueChanged", [""], "选项变化事件"),
    ("ClearOptions", ["()"], "清空选项"),
    ("AddOptions", ["(List<string> options)"], "添加文本选项"),
    ("SetValueWithoutNotify", ["(int input)"], "设置选项但不触发事件"),
]

SCROLL_RECT = [
    ("content", [""], "可滚动内容的 RectTransform"),
    ("horizontal", [""], "是否允许水平滚动"),
    ("vertical", [""], "是否允许垂直滚动"),
    ("normalizedPosition", [""], "归一化滚动位置"),
    ("verticalNormalizedPosition", [""], "垂直滚动位置（1 顶部，0 底部）"),
    ("horizontalNormalizedPosition", [""], "水平滚动位置"),
    ("onValueChanged", [""], "滚动位置变化事件"),
]

EVENT_SYSTEM = [
    ("current", [""], "当前活动的 EventSystem"),
    ("currentInputModule", [""], "当前输入模块"),
    ("IsPointerOverGameObject", ["()", "(int pointerId)"], "判断指针是否位于 UI 上"),
    ("SetSelectedGameObject", ["(GameObject selected)"], "设置当前选中的 UI 对象"),
]

BASE_EVENT_DATA = [
    ("selectedObject", [""], "当前选中的游戏对象"),
    ("currentInputModule", [""], "触发事件的输入模块"),
    ("Use", ["()"], "标记事件已处理"),
]

POINTER_EVENT_DATA = [
    ("position", [""], "屏幕指针位置"),
    ("delta", [""], "本次移动量"),
    ("pressPosition", [""], "按下时的屏幕位置"),
    ("pointerPress", [""], "按下的游戏对象"),
    ("pointerEnter", [""], "指针当前进入的游戏对象"),
    ("pointerId", [""], "指针 ID；鼠标左键通常为 -1"),
    ("button", [""], "鼠标按键类型"),
]

TMP_TEXT = [
    ("text", [""], "显示文本"),
    ("font", [""], "TextMesh Pro 字体资源"),
    ("fontSize", [""], "字号"),
    ("color", [""], "文本颜色"),
    ("alignment", [""], "文本对齐方式"),
    ("enableWordWrapping", [""], "是否自动换行"),
    ("overflowMode", [""], "文本溢出处理"),
    ("SetText", ["(string text)", "(string text, float arg0)"], "设置文本，可用格式占位符"),
    ("ForceMeshUpdate", ["()"], "立即重建文本网格"),
]

TMP_INPUT_FIELD = [
    ("text", [""], "输入框当前文本"),
    ("placeholder", [""], "占位文本组件"),
    ("characterLimit", [""], "允许输入的最大字符数"),
    ("onValueChanged", [""], "文本变化事件"),
    ("onEndEdit", [""], "结束编辑事件"),
    ("SetTextWithoutNotify", ["(string input)"], "设置文本但不触发事件"),
    ("ActivateInputField", ["()"], "激活输入并打开软键盘"),
]

UNITY_PACKAGE_TYPES = [
    ("UnityEngine.UI.Selectable", "Selectable", SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.Graphic", "Graphic", GRAPHIC, "UnityEngine.UI"),
    ("UnityEngine.UI.Button", "Button", BUTTON + SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.Image", "Image", IMAGE + GRAPHIC, "UnityEngine.UI"),
    ("UnityEngine.UI.RawImage", "RawImage", RAW_IMAGE + GRAPHIC, "UnityEngine.UI"),
    ("UnityEngine.UI.Text", "Text", TEXT + GRAPHIC, "UnityEngine.UI"),
    ("UnityEngine.UI.Toggle", "Toggle", TOGGLE + SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.Slider", "Slider", SLIDER + SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.InputField", "InputField", INPUT_FIELD + SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.Dropdown", "Dropdown", DROPDOWN + SELECTABLE, "UnityEngine.UI"),
    ("UnityEngine.UI.ScrollRect", "ScrollRect", SCROLL_RECT, "UnityEngine.UI"),
    ("UnityEngine.UI.CanvasScaler", "CanvasScaler",
     [("uiScaleMode", [""], "UI 缩放模式"), ("referenceResolution", [""], "参考分辨率"),
      ("matchWidthOrHeight", [""], "宽高匹配比例")], "UnityEngine.UI"),
    ("UnityEngine.UI.GraphicRaycaster", "GraphicRaycaster",
     [("eventCamera", [""], "用于 UI 射线检测的相机"), ("ignoreReversedGraphics", [""], "是否忽略反向图形")],
     "UnityEngine.UI"),
    ("UnityEngine.EventSystems.EventSystem", "EventSystem", EVENT_SYSTEM, "UnityEngine.EventSystems"),
    ("UnityEngine.EventSystems.EventTrigger", "EventTrigger",
     [("triggers", [""], "事件触发条目列表"),
      ("OnPointerClick", ["(PointerEventData eventData)"], "指针点击回调"),
      ("OnPointerDown", ["(PointerEventData eventData)"], "指针按下回调"),
      ("OnPointerUp", ["(PointerEventData eventData)"], "指针抬起回调"),
      ("OnPointerEnter", ["(PointerEventData eventData)"], "指针进入回调"),
      ("OnPointerExit", ["(PointerEventData eventData)"], "指针离开回调"),
      ("OnBeginDrag", ["(PointerEventData eventData)"], "开始拖动回调"),
      ("OnDrag", ["(PointerEventData eventData)"], "拖动中回调"),
      ("OnEndDrag", ["(PointerEventData eventData)"], "结束拖动回调"),
      ("OnDrop", ["(PointerEventData eventData)"], "放下对象时调用"),
      ("OnScroll", ["(PointerEventData eventData)"], "滚轮滚动回调")],
     "UnityEngine.EventSystems"),
    ("UnityEngine.EventSystems.BaseEventData", "BaseEventData", BASE_EVENT_DATA, "UnityEngine.EventSystems"),
    ("UnityEngine.EventSystems.PointerEventData", "PointerEventData",
     POINTER_EVENT_DATA, "UnityEngine.EventSystems"),
    ("TMPro.TMP_Text", "TMP_Text", TMP_TEXT, "TMPro"),
    ("TMPro.TextMeshProUGUI", "TextMeshProUGUI", TMP_TEXT, "TMPro"),
    ("TMPro.TextMeshPro", "TextMeshPro", TMP_TEXT, "TMPro"),
    ("TMPro.TMP_InputField", "TMP_InputField", TMP_INPUT_FIELD, "TMPro"),
    ("TMPro.TMP_Dropdown", "TMP_Dropdown", DROPDOWN, "TMPro"),
]

# 表名 -> (类型显示名, 成员, 是否是类型)
BCL = [
    ("Console", "Console", CONSOLE, False),
    ("String", "string", STRING + STRING_STATIC, False),
    ("StringBuilder", "StringBuilder", STRINGBUILDER, False),
    ("Math", "Math", MATH, False),
    ("List", "List<T>", LIST, False),
    ("Dictionary", "Dictionary<K,V>", DICT, False),
    ("Queue", "Queue<T>", QUEUE, False),
    ("Stack", "Stack<T>", STACK, False),
    ("HashSet", "HashSet<T>", HASHSET, False),
    ("KeyValuePair", "KeyValuePair<K,V>", KEYVALUEPAIR, False),
    ("Array", "Array", ARRAY, False),
    # 与 UnityEngine.Random 同名；单独存一份，前端按 C#/Unity 模式解析。
    ("SystemRandom", "Random", RANDOM, False),
    ("Convert", "Convert", CONVERT, False),
    ("IEnumerator", "IEnumerator", IENUMERATOR, False),
    ("IEnumerable", "IEnumerable", IENUMERABLE, False),
    ("IDisposable", "IDisposable", IDISPOSABLE, False),
    ("Thread", "Thread", THREAD, False),
    ("Object", "object", OBJECT, False),
    ("Action", "Action", ACTION, False),
    ("Func", "Func<T,TResult>", FUNC, False),
    ("Exception", "Exception", EXCEPTION, False),
    ("DateTime", "DateTime", DATETIME, False),
    ("TimeSpan", "TimeSpan", TIMESPAN, False),
    ("Path", "Path", PATH_MEMBERS, False),
    ("SystemFile", "File", FILE_MEMBERS, False),
    ("SystemDirectory", "Directory", DIRECTORY_MEMBERS, False),
    ("StreamReader", "StreamReader", STREAM_READER, False),
    ("StreamWriter", "StreamWriter", STREAM_WRITER, False),
    ("MemoryStream", "MemoryStream", MEMORY_STREAM, False),
    ("Task", "Task", TASK, False),
    ("Regex", "Regex", REGEX, False),
    ("Guid", "Guid", GUID, False),
    ("int", "int", INT_MEMBERS, True),
    ("float", "float", FLOAT_MEMBERS, True),
    ("double", "double", DOUBLE_MEMBERS, True),
    ("long", "long", LONG_MEMBERS, True),
    ("char", "char", CHAR_MEMBERS, True),
    ("bool", "bool", BOOL_MEMBERS, True),
]


# 类型 → 命名空间。自动 using 用：选中补全时发现文件头没有对应 using 就自动补一条
# 基础类型（int/float 等）是关键字，不需要 using，故意不在表里
BCL_NS = {
    "IEnumerator":   "System.Collections",
    "IEnumerable":   "System.Collections",
    "List":          "System.Collections.Generic",
    "Dictionary":    "System.Collections.Generic",
    "Queue":         "System.Collections.Generic",
    "Stack":         "System.Collections.Generic",
    "HashSet":       "System.Collections.Generic",
    "KeyValuePair":  "System.Collections.Generic",
    "StringBuilder": "System.Text",
    "Thread":        "System.Threading",
    "Console":       "System",
    "String":        "System",
    "Math":          "System",
    "Array":         "System",
    "SystemRandom":  "System",
    "Convert":       "System",
    "Object":        "System",
    "Action":        "System",
    "Func":          "System",
    "Exception":     "System",
    "DateTime":      "System",
    "TimeSpan":      "System",
    "Path":          "System.IO",
    "SystemFile":    "System.IO",
    "SystemDirectory": "System.IO",
    "StreamReader":  "System.IO",
    "StreamWriter":  "System.IO",
    "MemoryStream":  "System.IO",
    "Task":          "System.Threading.Tasks",
    "Regex":         "System.Text.RegularExpressions",
    "Guid":          "System",
}


# ── MonoBehaviour 生命周期（protected 方法，Unity 的 XML 不收录，只能手写）──
# 这些是 Unity 初学最高频的 API，缺了它们连 Update 都悬停不出来
MONO_LIFECYCLE = [
    ("Awake", ["()"], "对象加载时立即调用（先于 Start），引用初始化放这里"),
    ("Start", ["()"], "第一次 Update 前调一次，初始化逻辑放这里"),
    ("Update", ["()"], "每帧调用一次；输入读取、非物理移动放这里"),
    ("FixedUpdate", ["()"], "固定时间步调用（默认每 0.02s）；物理相关放这里"),
    ("LateUpdate", ["()"], "所有 Update 之后调用；相机跟随放这里"),
    ("OnEnable", ["()"], "对象被启用时调用"),
    ("OnDisable", ["()"], "对象被禁用时调用"),
    ("OnDestroy", ["()"], "对象销毁前调用"),
    ("OnTriggerEnter", ["(Collider other)"], "进入触发器（至少一方勾 Is Trigger）"),
    ("OnTriggerStay", ["(Collider other)"], "停留在触发器期间每帧调用"),
    ("OnTriggerExit", ["(Collider other)"], "离开触发器时调用"),
    ("OnTriggerEnter2D", ["(Collider2D other)"], "2D：进入触发器时调用"),
    ("OnTriggerStay2D", ["(Collider2D other)"], "2D：停留在触发器期间调用"),
    ("OnTriggerExit2D", ["(Collider2D other)"], "2D：离开触发器时调用"),
    ("OnCollisionEnter", ["(Collision other)"], "发生碰撞时调用（双方都不是 Trigger）"),
    ("OnCollisionStay", ["(Collision other)"], "碰撞接触期间每帧调用"),
    ("OnCollisionExit", ["(Collision other)"], "碰撞分离时调用"),
    ("OnCollisionEnter2D", ["(Collision2D collision)"], "2D：发生碰撞时调用"),
    ("OnCollisionStay2D", ["(Collision2D collision)"], "2D：碰撞接触期间调用"),
    ("OnCollisionExit2D", ["(Collision2D collision)"], "2D：碰撞分离时调用"),
    ("OnMouseDown", ["()"], "鼠标点中本对象的 Collider 时调用"),
    ("OnMouseUp", ["()"], "鼠标在 Collider 上松开时调用"),
    ("OnApplicationQuit", ["()"], "应用退出前调用"),
    ("OnApplicationFocus", ["(bool hasFocus)"], "应用获得或失去焦点时调用"),
    ("OnApplicationPause", ["(bool pauseStatus)"], "应用暂停或恢复时调用"),
    ("OnGUI", ["()"], "IMGUI 每帧绘制时调用"),
    ("OnValidate", ["()"], "Inspector 中字段变化时在编辑器调用"),
    ("Reset", ["()"], "组件首次添加或 Inspector 点 Reset 时调用"),
    ("OnDrawGizmos", ["()"], "编辑器中持续绘制 Gizmos"),
    ("OnDrawGizmosSelected", ["()"], "编辑器中仅选中对象时绘制 Gizmos"),
    ("OnBecameVisible", ["()"], "进入任意相机视野时调用"),
    ("OnBecameInvisible", ["()"], "离开所有相机视野时调用"),
]

# 不新建类型的补充成员，直接挂到已有类型下（key = 类型短名）
EXTRA = {
    "MonoBehaviour": MONO_LIFECYCLE,
}

PACKAGE_NS = {
    display: namespace
    for _qualified, display, _members, namespace in UNITY_PACKAGE_TYPES
}


def entries():
    """产出 (key, [{"s","d","k"}...]) 供 build_symbols 合并"""
    for key, display, members, is_type in BCL:
        # 类型本身也进类型表
        yield ("__type__", display)
        grouped = {}
        for name, sigs, doc in members:
            for sig in sigs:
                grouped.setdefault(name, []).append({"s": sig, "d": doc, "k": "M"})
        for name, items in grouped.items():
            yield ("%s.%s" % (key, name), items)
    # 生命周期等补充成员：不进类型表，只挂成员
    for owner, members in EXTRA.items():
        grouped = {}
        for name, sigs, doc in members:
            for sig in sigs:
                grouped.setdefault(name, []).append({"s": sig, "d": doc, "k": "M"})
        for name, items in grouped.items():
            yield ("%s.%s" % (owner, name), items)
    # UGUI / TextMesh Pro 是独立包，不在 UnityEngine.* 的 XML 列表中。
    # 这里仅维护常用类型，保证不会被标记为 C# 基础库。
    for qualified, display, members, _namespace in UNITY_PACKAGE_TYPES:
        description = "常用 Unity UI / TextMesh Pro API"
        yield ("__type__", display)
        yield (display, [{"s": "", "d": description, "k": "type"}])
        grouped = {}
        for name, sigs, doc in members:
            for sig in sigs:
                grouped.setdefault(name, []).append({"s": sig, "d": doc, "k": "M"})
        for name, items in grouped.items():
            yield ("%s.%s" % (display, name), items)
