# -*- coding: utf-8 -*-
"""collect_zhihu.py — 低频抓取知乎热榜 / 关键词搜索结果。

设计原则
--------
* 只访问公开接口，不绕过风控；
* 低频（默认每 3 秒一次）、带缓存、失败即停；
* 输出到 data/zhihu_raw.json，供 cluster_events.py 使用。

用法
----
    python analysis/collect_zhihu.py --hot                 # 只抓热榜
    python analysis/collect_zhihu.py --query "新能源"       # 关键词（需登录态）
    python analysis/collect_zhihu.py --hot --limit 50

登录态（可选）：把浏览器 Cookie 写入 data/zhihu_cookie.txt（整行）。
无 Cookie 时，热榜通常仍可读取；搜索接口多半会返回 403。
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _get(url, cookie=None):
    headers = {"User-Agent": UA, "Accept": "application/json, text/plain, */*",
               "Referer": "https://www.zhihu.com/hot"}
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def fetch_hot(limit=50):
    url = ("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
           f"?limit={limit}&desktop=true")
    j = _get(url)
    out = []
    for it in j.get("data", []):
        t = it.get("target", {})
        out.append({
            "title": t.get("title") or (t.get("question") or {}).get("title", ""),
            "excerpt": t.get("excerpt", ""),
            "url": (t.get("link") or {}).get("url", ""),
            "hot": (it.get("detail_text") or ""),
        })
    return out


def fetch_query(q, cookie=None):
    url = ("https://www.zhihu.com/api/v4/search_v3?t=general&q="
           + urllib.parse.quote(q) + "&correction=1&offset=0&limit=20&filter_fields=")
    j = _get(url, cookie)
    out = []
    for it in j.get("data", []):
        obj = it.get("object", {})
        out.append({
            "title": obj.get("title") or obj.get("question", {}).get("title", ""),
            "excerpt": obj.get("excerpt", ""),
            "url": obj.get("url", ""),
            "author": (obj.get("author") or {}).get("name", ""),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hot", action="store_true")
    ap.add_argument("--query", action="append", default=[])
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--sleep", type=float, default=3.0)
    args = ap.parse_args()

    os.makedirs(DATA, exist_ok=True)
    ck = os.path.join(DATA, "zhihu_cookie.txt")
    cookie = open(ck, encoding="utf-8").read().strip() if os.path.exists(ck) else None

    result = {"hot": [], "queries": {}}
    if args.hot or not args.query:
        try:
            result["hot"] = fetch_hot(args.limit)
            print(f"[hot] {len(result['hot'])} items")
        except Exception as e:
            print("[hot] failed:", str(e)[:120])
        time.sleep(args.sleep)
    for q in args.query:
        try:
            result["queries"][q] = fetch_query(q, cookie)
            print(f"[query] {q}: {len(result['queries'][q])} items")
        except Exception as e:
            print(f"[query] {q} failed:", str(e)[:120])
        time.sleep(args.sleep)

    out = os.path.join(DATA, "zhihu_raw.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main()
