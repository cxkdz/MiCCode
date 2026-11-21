#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_symbols.py — 从 Unity 的 XML API 文档生成符号表 symbols.json

用法：
    python build_symbols.py "D:/unity/2022.3.48t7/Editor/Data/Managed/UnityEngine"
    python build_symbols.py <xml目录> -o symbols.json

符号表结构（扁平化，前端 O(1) 查表）：
{
  "meta": {"source": "...", "modules": [...], "members": 16500, "built": "..."},
  "t":    ["Vector3", "Debug", "MonoBehaviour", ...],          // 类型名，用于补全
  "s": {                                                        // 符号表
      "Debug.Log": [{"s": "(object message)", "d": "Logs a message..."}],
      "Vector3.x": [{"s": "", "d": "X component of the vector."}]
  }
}
"""

import xml.etree.ElementTree as ET
import json
import os
import re
import sys
import time

# 只解析练习会用到的模块，避免把 CoreModule 之外的冷门模块全塞进来
MODULES = [
    "UnityEngine.CoreModule.xml",
    "UnityEngine.PhysicsModule.xml",
    "UnityEngine.Physics2DModule.xml",
    "UnityEngine.AnimationModule.xml",
    "UnityEngine.AudioModule.xml",
    "UnityEngine.InputLegacyModule.xml",
    "UnityEngine.ParticleSystemModule.xml",
    "UnityEngine.AIModule.xml",
    "UnityEngine.TilemapModule.xml",
    "UnityEngine.TextRenderingModule.xml",
    "UnityEngine.UIModule.xml",            # Canvas / CanvasGroup / CanvasRenderer
    "UnityEngine.UnityWebRequestModule.xml",  # UnityWebRequest
    "UnityEngine.AssetBundleModule.xml",   # AssetBundle
    "UnityEngine.VideoModule.xml",         # VideoPlayer
    "UnityEngine.GridModule.xml",          # 2D 网格
    "UnityEngine.JSONSerializeModule.xml", # JsonUtility
]

DOC_LIMIT = 160          # 摘要截断长度，控制 JSON 体积
INCLUDE_EDITOR = False   # 是否也收录 UnityEditor.*（练习用不到，默认关）

# System 类型名 → C# 关键字别名，让签名读起来像 C# 而不是 IL
CS_ALIAS = {
    "Object": "object", "String": "string", "Boolean": "bool",
    "Int32": "int", "Int64": "long", "Int16": "short",
    "UInt32": "uint", "UInt64": "ulong", "UInt16": "ushort",
    "Single": "float", "Double": "double", "Decimal": "decimal",
    "Byte": "byte", "SByte": "sbyte", "Char": "char",
    "Void": "void",
}


def short_name(full):
    """UnityEngine.Vector3 -> Vector3；List`1[System.String] -> List<String>"""
    t = full.strip()
    # 处理数组
    arr = ""
    while t.endswith("[]"):
        t = t[:-2]
        arr += "[]"
    # 处理泛型实例：Type`1[Arg1,Arg2]
    m = re.match(r"^(.*?)`\d+\[(.*)\]$", t)
    if m:
        base = short_name(m.group(1))
        args = ", ".join(short_name(a) for a in split_top(m.group(2)))
        return "%s<%s>%s" % (base, args, arr)
    # 普通类型：去掉命名空间与泛型元数
    t = re.sub(r"`\d+", "", t)
    base = t.split(".")[-1]
    return CS_ALIAS.get(base, base) + arr


def split_top(s):
    """按顶层逗号切分，忽略 <> 和 [] 内部的逗号"""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "<[":
            depth += 1
        elif ch in ">]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return [x.strip() for x in out if x.strip()]


def clean_doc(el):
    if el is None:
        return ""
    text = re.sub(r"\s+", " ", "".join(el.itertext())).strip()
    if len(text) > DOC_LIMIT:
        text = text[:DOC_LIMIT].rstrip() + "…"
    return text


def parse_method(full, node):
    """
    full:  UnityEngine.Debug.Log(System.Object)
    -> (owner_short, method_short, signature_string)
    """
    if "(" not in full:
        return None
    head, raw_params = full.split("(", 1)
    raw_params = raw_params.rstrip(")")
    if "." not in head:
        return None
    owner = short_name(head.rsplit(".", 1)[0])
    meth = head.rsplit(".", 1)[-1]
    if meth in ("#ctor", ".ctor"):
        meth = "new"

    types = split_top(raw_params)
    # XML 的 <param name="x"> 提供参数名，顺序与签名一致
    names = [p.get("name") for p in node.findall("param")] if node is not None else []
    parts = []
    for i, t in enumerate(types):
        st = short_name(t)
        if i < len(names) and names[i] and names[i] not in ("", None):
            parts.append("%s %s" % (st, names[i]))
        else:
            parts.append(st)
    sig = "(" + ", ".join(parts) + ")"
    return owner, meth, sig


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    out_path = "symbols.json"
    if "-o" in sys.argv:
        out_path = sys.argv[sys.argv.index("-o") + 1]

    symbols = {}
    types = set()
    ns_map = {}     # 类型短名 -> 命名空间，前端自动补 using 用
    module_stats = {}

    for mod in MODULES:
        path = os.path.join(src, mod)
        if not os.path.exists(path):
            continue
        try:
            root = ET.parse(path).getroot()
        except Exception as e:
            print("  跳过 %s：%s" % (mod, e))
            continue

        n = 0
        for node in root.iter("member"):
            name = node.get("name") or ""
            if not name or len(name) < 3 or name[1] != ":":
                continue
            kind, full = name[0], name[2:]

            # 过滤编译器生成的成员
            if "<" in full or full.startswith("_") or "#" in full.split("(")[0].replace("#ctor", ""):
                continue
            # 是否收录 UnityEditor
            if not INCLUDE_EDITOR and (full.startswith("UnityEditor.") or full.startswith("TuanjieEditor.")):
                continue
            # 引擎内部 PlayerLoop 阶段枚举：对练习纯噪声，还会占用 Update/Start
            # 这些高频名字的类型位（悬停和补全都会被它们抢走）
            if full.startswith("UnityEngine.PlayerLoop."):
                continue

            doc = clean_doc(node.find("summary"))

            if kind == "T":
                st = short_name(full)
                types.add(st)
                symbols.setdefault(st, [{"s": "", "d": doc, "k": "type"}])
                if "." in full:
                    ns = full.rsplit(".", 1)[0]
                    ns_map.setdefault(st, ns)
                    ns_map.setdefault(st.split("<")[0], ns)
                n += 1
                continue

            if kind in ("P", "F", "E"):
                if "." not in full:
                    continue
                ofull = full.rsplit(".", 1)[0]
                owner = short_name(ofull)
                mem = full.rsplit(".", 1)[-1]
                key = "%s.%s" % (owner, mem)
                symbols.setdefault(key, []).append({"s": "", "d": doc, "k": kind})
                if "." in ofull:
                    ns_map.setdefault(owner, ofull.rsplit(".", 1)[0])
                n += 1
                continue

            if kind == "M":
                if "(" in full:
                    parsed = parse_method(full, node)
                    if not parsed:
                        continue
                    owner, meth, sig = parsed
                    ofull = full.split("(", 1)[0].rsplit(".", 1)[0]
                else:
                    # Unity 的 XML 里无参方法不带括号（SceneManager.GetActiveScene、
                    # PlayerPrefs.Save、VideoPlayer.Play 全是这种），缺这个分支会
                    # 静默丢掉所有无参 API
                    if "." not in full:
                        continue
                    ofull = full.rsplit(".", 1)[0]
                    owner = short_name(ofull)
                    meth = full.rsplit(".", 1)[-1]
                    if meth in ("#ctor",):
                        meth = "new"
                    if "<" in meth or meth.startswith("_"):
                        continue
                    sig = "()"
                symbols.setdefault("%s.%s" % (owner, meth), []).append({"s": sig, "d": doc, "k": "M"})
                if "." in ofull:
                    ns_map.setdefault(owner, ofull.rsplit(".", 1)[0])
                n += 1

        module_stats[mod] = n
        print("  %-46s %6d 条" % (mod, n))

    # 合并手写的基础类库符号（Console / String / Math / List ...）
    bcl_count = 0
    bcl_owners = []
    try:
        import bcl_symbols
        for key, display, _members, _is in bcl_symbols.BCL:
            # key 是符号 owner；display 是用户输入的类型名，二者都需纳入模式过滤。
            for owner in (key, display):
                bare = owner.split("<", 1)[0]
                if bare not in bcl_owners:
                    bcl_owners.append(bare)
        for key, items in bcl_symbols.entries():
            if key == "__type__":
                types.add(items)
                continue
            if not items:
                continue
            bucket = symbols.setdefault(key, [])
            if any(e.get("k") == "type" for e in bucket):
                bucket = [e for e in bucket if e.get("k") != "type"]
                symbols[key] = bucket
            bucket.extend(items)
            bcl_count += 1
        print("  %-46s %6d 条" % ("<BCL 手写补充>", bcl_count))
        if hasattr(bcl_symbols, "BCL_NS"):
            ns_map.update(bcl_symbols.BCL_NS)
        # UGUI / TextMesh Pro 来自独立 Package，不在 UnityEngine XML 白名单中。
        if hasattr(bcl_symbols, "PACKAGE_NS"):
            ns_map.update(bcl_symbols.PACKAGE_NS)
    except ImportError:
        print("  (未找到 bcl_symbols.py，跳过基础类库)")

    xml_members = sum(module_stats.values())
    total_members = xml_members + bcl_count
    data = {
        "meta": {
            "source": src,
            "modules": list(module_stats.keys()),
            "members": total_members,
            "xmlMembers": xml_members,
            "supplementalMembers": bcl_count,
            "types": len(types),
            "built": time.strftime("%Y-%m-%d %H:%M"),
        },
        "bcl": bcl_owners,
        "ns": ns_map,
        "t": sorted(types),
        "s": symbols,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(out_path) / 1024.0
    print("\n总计 %d 条索引项（XML %d + 手写补充 %d）/ %d 个类型" %
          (total_members, xml_members, bcl_count, len(types)))
    print("输出 %s（%.0f KB）" % (out_path, size))


if __name__ == "__main__":
    main()
