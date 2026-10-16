# -*- coding: utf-8 -*-
"""cluster_events.py — 把采集结果去重、聚类为"事件"，产出 data/events.json。

输入（存在哪个用哪个）：data/zhihu_raw.json、data/x_raw.json
输出：data/events.json —— 事件库（本书构建与诊断卡的数据源）

事件条目字段
------------
    title        事件标题
    sources      来源列表 [{"platform","url","title"}]
    heat         热度（粗排，仅用于排序）
    diagnosed    bool：是否已填写诊断卡
    evidence     证据等级 A/B/C
    refutable    可反驳条件
    card         诊断卡（五个字段；缺省为待填）
"""
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

PUNCT = re.compile(r"[\s，。！？、,.!?~～“”\"'（）()【】\[\]:：;；-]+")


def norm(s):
    return PUNCT.sub("", (s or "")).lower()


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def cluster():
    events = []
    seen = set()

    z = load("zhihu_raw.json")
    if z:
        for it in z.get("hot", []):
            key = norm(it.get("title"))
            if not key or key in seen:
                continue
            seen.add(key)
            events.append({
                "title": it.get("title", ""),
                "sources": [{"platform": "zhihu", "url": it.get("url", ""),
                             "title": it.get("title", "")}],
                "heat": it.get("hot", ""),
                "diagnosed": False, "evidence": "C", "refutable": "",
                "card": {"see": "", "remember": "", "keepup": "",
                         "choose": "", "tell": ""},
            })

    x = load("x_raw.json")
    if x:
        for q, res in x.items():
            for t in (res.get("data", []) if isinstance(res, dict) else []):
                txt = t.get("text", "")
                key = norm(txt)[:40]
                if not key or key in seen:
                    continue
                seen.add(key)
                m = t.get("public_metrics", {}) or {}
                events.append({
                    "title": txt[:60],
                    "sources": [{"platform": "x", "url": f"https://x.com/i/status/{t.get('id','')}",
                                 "title": txt[:60]}],
                    "heat": f"likes={m.get('like_count',0)}, rt={m.get('retweet_count',0)}",
                    "diagnosed": False, "evidence": "C", "refutable": "",
                    "card": {"see": "", "remember": "", "keepup": "",
                             "choose": "", "tell": ""},
                })

    # 粗略按"数字型热度"降序
    def hkey(e):
        nums = re.findall(r"\d+", str(e.get("heat", "")))
        return int(nums[0]) if nums else 0
    events.sort(key=hkey, reverse=True)

    out = os.path.join(DATA, "events.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"wrote {out}: {len(events)} events")


if __name__ == "__main__":
    cluster()
