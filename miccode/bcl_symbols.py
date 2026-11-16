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
    ("Random", "Random", RANDOM, False),
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
    "Random":        "System",
    "Convert":       "System",
    "Object":        "System",
    "Action":        "System",
    "Func":          "System",
    "Exception":     "System",
    "DateTime":      "System",
    "TimeSpan":      "System",
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
    ("OnCollisionEnter", ["(Collision other)"], "发生碰撞时调用（双方都不是 Trigger）"),
    ("OnCollisionStay", ["(Collision other)"], "碰撞接触期间每帧调用"),
    ("OnCollisionExit", ["(Collision other)"], "碰撞分离时调用"),
    ("OnMouseDown", ["()"], "鼠标点中本对象的 Collider 时调用"),
    ("OnMouseUp", ["()"], "鼠标在 Collider 上松开时调用"),
    ("OnApplicationQuit", ["()"], "应用退出前调用"),
    ("OnBecameVisible", ["()"], "进入任意相机视野时调用"),
    ("OnBecameInvisible", ["()"], "离开所有相机视野时调用"),
]

# 不新建类型的补充成员，直接挂到已有类型下（key = 类型短名）
EXTRA = {
    "MonoBehaviour": MONO_LIFECYCLE,
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
