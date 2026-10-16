# -*- coding: utf-8 -*-
"""collect_x.py — 调用 X (Twitter) API v2 做关键词检索。

前置
----
* 需要一个 X API 的 Bearer Token，写入 data/x_token.txt（整行）；
* 注意：v2 的 `recent search` 只覆盖最近 7 天。要覆盖"过去一年"，
  需（a）更高的 API 访问等级，或（b）分关键词、分阶段多次采集并归档。

用法
----
    python analysis/collect_x.py --query "AI jobs" --max 100
    python analysis/collect_x.py --query "新能源" --query "房价" --max 100

输出：data/x_raw.json
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")


def _get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "User-Agent": "hotspot-bills/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:300]}


def search(query, token, max_results=100):
    url = ("https://api.twitter.com/2/tweets/search/recent"
           "?query=" + urllib.parse.quote(query)
           + f"&max_results={max(10, min(100, max_results))}"
           + "&tweet.fields=public_metrics,created_at,lang")
    return _get(url, token)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", action="append", default=[])
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()
    if not args.query:
        print("请提供 --query")
        return

    tf = os.path.join(DATA, "x_token.txt")
    if not os.path.exists(tf):
        print(f"缺少 {tf}（一行 Bearer Token）。请先创建。")
        return
    token = open(tf, encoding="utf-8").read().strip()

    out = {}
    for q in args.query:
        out[q] = search(q, token, args.max)
        n = len(out[q].get("data", [])) if isinstance(out[q], dict) else 0
        print(f"[x] {q}: {n} tweets" + (f" (error {out[q].get('_error')})"
                                        if isinstance(out[q], dict) and "_error" in out[q] else ""))
        time.sleep(args.sleep)
    p = os.path.join(DATA, "x_raw.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("wrote", p)


if __name__ == "__main__":
    main()
