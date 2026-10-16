# -*- coding: utf-8 -*-
"""
md2book.py — 把 book-src/*.md 转换为 knowledge-tradeoffs 的 source/*.html。

支持的 Markdown 子集（刻意为本书稿定制）：
  # / ## / ### / ####   标题（## 自动加 secX-Y 锚点）
  > ...                 提示框（按【…】自动分类）
  | a | b |             表格
  - item                无序列表
  [[FIG:name|caption]]  插图
  **粗体**、`code`
  ---                   分隔线（忽略）
"""
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "book-src")
OUT = os.path.join(HERE, "source")

# book-src 文件 -> (输出文件, 顶层标题覆盖, 锚点)
FILES = [
    ("00_前言.md", "front_intro.html", "前言　为什么热搜需要一张账单", None),
    ("01_方法.md", "ch01.html", None, "ch1"),
    ("02_数据与伦理.md", "ch02.html", None, "ch2"),
    ("03_案例.md", "ch03.html", None, "ch3"),
    ("04_结语.md", "back_epilogue.html", None, "epilogue"),
    ("05_附录.md", "appendix_a.html", None, "apxA"),
]


def inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def box_class(text):
    if "多想一层" in text:
        return "box box-more1"
    if "再想一层" in text:
        return "box box-more2"
    if "给专家的注" in text:
        return "box box-expert"
    if "动手试试" in text:
        return "box box-do"
    if "一句话带走" in text:
        return "box box-takeaway"
    return "box"


def heading(level, text):
    text = inline(text)
    if level == 1:
        return f'<h2 class="chapter">{text}</h2>'
    if level == 2:
        m = re.match(r"\s*(\d+)\.(\d+)", re.sub(r"<[^>]+>", "", text))
        if m:
            return f'<h3 id="sec{m.group(1)}-{m.group(2)}">{text}</h3>'
        return f"<h3>{text}</h3>"
    if level == 3:
        return f"<h4>{text}</h4>"
    return f"<h5>{text}</h5>"


def parse_table(rows):
    # rows: list of raw '| ... |' strings; rows[1] is separator
    def cells(r):
        r = r.strip().strip("|")
        return [c.strip() for c in r.split("|")]
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    out = ['<table class="nat">']
    out.append("<tr>" + "".join(f'<th class="l">{inline(c)}</th>' for c in head) + "</tr>")
    for r in body:
        out.append("<tr>" + "".join(f'<td class="l">{inline(c)}</td>' for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def parse_blocks(lines):
    out = []
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i].rstrip()
        s = raw.strip()
        if not s:
            i += 1
            continue
        # 分隔线
        if re.fullmatch(r"[-*_]{3,}", s):
            i += 1
            continue
        # 图
        m = re.match(r"\[\[FIG:([^|\]]+)(?:\|([^\]]*))?\]\]", s)
        if m:
            name = m.group(1).strip()
            cap = (m.group(2) or "").strip()
            cap_html = f'<div class="cap"><b>{cap}</b></div>' if cap else ""
            out.append(
                f'<img class="fig" src="assets/svg/{name}.svg" alt="{cap}">{cap_html}'
            )
            i += 1
            continue
        # 标题
        m = re.match(r"(#{1,4})\s+(.*)", s)
        if m:
            out.append(heading(len(m.group(1)), m.group(2)))
            i += 1
            continue
        # 引用框
        if s.startswith(">"):
            blk = []
            first = s
            while i < n and lines[i].strip().startswith(">"):
                blk.append(re.sub(r"^\s*>\s?", "", lines[i]).rstrip())
                i += 1
            inner = parse_blocks(blk)
            cls = box_class(first + " " + " ".join(blk[:2]))
            out.append(f'<div class="{cls}">{inner}</div>')
            continue
        # 表格
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(parse_table(rows))
            continue
        # 列表
        if re.match(r"\s*[-*]\s+", raw):
            items = []
            while i < n and re.match(r"\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).rstrip())
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        # 有序列表
        if re.match(r"\s*\d+\.\s+", raw):
            items = []
            while i < n and re.match(r"\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).rstrip())
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        # 段落
        para = [s]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", ">", "|", "[[FIG"))
                    or re.fullmatch(r"[-*_]{3,}", nxt)
                    or re.match(r"\s*[-*]\s+", lines[i])):
                break
            para.append(nxt)
            i += 1
        out.append(_wrap_para(inline(" ".join(para))))
    return "\n".join(out)


def _wrap_para(para_text):
    """把以【…】开头的段子自动包成提示框。"""
    m = re.match(r"(?:<strong>)?【(.+?)】(?:</strong>)?", para_text)
    if m:
        tag = m.group(1)
        if any(k in tag for k in ("多想一层", "再想一层", "给专家的注", "动手试试", "一句话带走")):
            return f'<div class="{box_class(tag)}"><p>{para_text}</p></div>'
    return f"<p>{para_text}</p>"


def main():
    os.makedirs(OUT, exist_ok=True)
    for fname, outname, title_override, anchor in FILES:
        p = os.path.join(SRC, fname)
        with open(p, encoding="utf-8") as f:
            text = f.read()
        lines = text.split("\n")
        # 若首行是一级标题且提供了覆盖，则替换
        if title_override and lines and lines[0].startswith("# "):
            lines = lines[1:]
            lines.insert(0, "# " + title_override)
        html = parse_blocks(lines)
        with open(os.path.join(OUT, outname), "w", encoding="utf-8") as f:
            f.write(html + "\n")
        print("wrote", outname, len(html), "bytes")


if __name__ == "__main__":
    main()
