# -*- coding: utf-8 -*-
"""collect.py — 真实采集多个公开热榜，规范化到 data/events.json。

来源：知乎热榜、今日头条热榜、百度热搜、抖音热榜、B 站热门、
      X 趋势（trends24 / getdaytrends）、GitHub 近期热门。
只读公开接口，低频、带缓存、失败即停。
"""
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def get(url, as_json=True, referer=None):
    h = {"User-Agent": UA, "Accept": "*/*",
         "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
         "Accept-Encoding": "identity"}
    if referer:
        h["Referer"] = referer
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=40) as r:
                chunks = []
                while True:
                    c = r.read(65536)
                    if not c:
                        break
                    chunks.append(c)
                b = b"".join(chunks)
            return json.loads(b.decode("utf-8", "ignore")) if as_json else b.decode("utf-8", "ignore")
        except Exception as e:
            last = e
            time.sleep(2 + attempt * 2)
    raise last


def zhihu():
    j = get("https://api.zhihu.com/topstory/hot-list?limit=50")
    out = []
    for it in j.get("data", []):
        t = it.get("target", {})
        title = t.get("title") or (t.get("question") or {}).get("title", "")
        if title:
            out.append({"title": title, "url": (t.get("link") or {}).get("url", ""),
                        "heat": (it.get("detail_text") or "")})
    return out


def toutiao():
    j = get("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    return [{"title": d.get("Title", ""), "url": d.get("Url", ""),
             "heat": str(d.get("HotValue", ""))} for d in j.get("data", []) if d.get("Title")]


def baidu():
    j = get("https://top.baidu.com/api/board?platform=wise&tab=realtime")
    out = []
    for card in j.get("data", {}).get("cards", []):
        for it in card.get("content", []):
            w = it.get("word") or it.get("query") or ""
            if w:
                out.append({"title": w, "url": it.get("url", ""),
                            "heat": str(it.get("hotScore", ""))})
    return out


def douyin():
    try:
        j = get("https://www.douyin.com/aweme/v1/web/hot/search/list/")
        lst = (j.get("data") or {}).get("word_list", [])
        return [{"title": d.get("word", ""), "url": "", "heat": str(d.get("hot_value", ""))}
                for d in lst if d.get("word")]
    except Exception as e:
        print("  [douyin]", str(e)[:80]); return []


def bilibili():
    j = get("https://api.bilibili.com/x/web-interface/popular?ps=30&pn=1")
    out = []
    for d in j.get("data", {}).get("list", []):
        out.append({"title": d.get("title", ""),
                    "url": d.get("short_link_v2") or d.get("bvid", ""),
                    "heat": str(d.get("stat", {}).get("view", ""))})
    return out


def x_trends():
    txt = get("https://trends24.in/", as_json=False)
    trends = re.findall(r'<a[^>]*class="trend-link"[^>]*>([^<]+)</a>', txt)
    if not trends:
        trends = re.findall(r'data-trend="([^"]+)"', txt)
    out = []
    seen = set()
    for t in trends:
        t = html.unescape(t).strip()
        if t and t not in seen:
            seen.add(t)
            out.append({"title": t, "url": "", "heat": ""})
    return out


def main():
    os.makedirs(DATA, exist_ok=True)
    srcs = [("zhihu", zhihu), ("toutiao", toutiao), ("baidu", baidu),
            ("douyin", douyin), ("bilibili", bilibili), ("x_trends", x_trends)]
    raw = {}
    for name, fn in srcs:
        try:
            raw[name] = fn()
            print(f"[{name}] {len(raw[name])} items")
        except Exception as e:
            raw[name] = []
            print(f"[{name}] FAILED: {str(e)[:100]}")
        time.sleep(1.5)
    with open(os.path.join(DATA, "hotlists.json"), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print("wrote data/hotlists.json")


if __name__ == "__main__":
    main()
