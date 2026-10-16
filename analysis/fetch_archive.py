# -*- coding: utf-8 -*-
"""fetch_archive.py — 抓取过去一年的每日热榜存档（知乎 / 微博），做频次聚合。

数据源：github.com/lonnyzhang423/{zhihu,weibo}-hot-hub 的 archives/YYYY-MM-DD.md
输出：data/year_zhihu.json、data/year_weibo.json、data/year_events.md（排行）
"""
import datetime as dt
import json
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"
REPOS = {"zhihu": "zhihu-hot-hub", "weibo": "weibo-hot-hub"}
TITLE_RE = re.compile(r"^\s*\d+\.\s*\[([^\]]+)\]\(([^)]+)\)", re.M)


def fetch_day(repo, day):
    url = f"https://raw.githubusercontent.com/lonnyzhang423/{repo}/main/archives/{day}.md"
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode("utf-8", "ignore")
            return [(m.group(1).strip(), m.group(2).strip()) for m in TITLE_RE.finditer(txt)]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
        except Exception:
            time.sleep(2)
    return []


def daterange(start, end):
    d = start
    while d <= end:
        yield d.isoformat()
        d += dt.timedelta(days=1)


def collect(platform, repo, start, end):
    days = list(daterange(start, end))
    out = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_day, repo, d): d for d in days}
        for i, f in enumerate(as_completed(futs), 1):
            d = futs[f]
            try:
                items = f.result()
            except Exception:
                items = []
            if items:
                out[d] = items
            if i % 40 == 0:
                print(f"  [{platform}] {i}/{len(days)} days fetched")
    return out


def main():
    end = dt.date(2026, 10, 16)
    start = dt.date(2025, 10, 16)
    os.makedirs(DATA, exist_ok=True)
    summary = {}
    for platform, repo in REPOS.items():
        print(f"== fetching {platform} ({repo}) ==")
        data = collect(platform, repo, start, end)
        with open(os.path.join(DATA, f"year_{platform}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # 频次聚合
        freq = {}
        for day, items in data.items():
            seen = set()
            for title, url in items:
                key = re.sub(r"\s+", "", title)
                if key in seen:
                    continue
                seen.add(key)
                e = freq.setdefault(key, {"title": title, "url": url, "days": []})
                e["days"].append(day)
        ranked = sorted(freq.values(), key=lambda e: len(e["days"]), reverse=True)
        summary[platform] = ranked
        print(f"  {platform}: {len(data)} days, {len(ranked)} distinct titles")
    # 汇总可读排行
    lines = ["# 过去一年热榜排行（按上榜天数）\n"]
    for platform, ranked in summary.items():
        lines.append(f"\n## {platform}（前 120）\n")
        for i, e in enumerate(ranked[:120], 1):
            d0, d1 = min(e["days"]), max(e["days"])
            lines.append(f"{i}. **{e['title']}** — 上榜 {len(e['days'])} 天（{d0} ~ {d1}）")
    with open(os.path.join(DATA, "year_events.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote data/year_events.md")


if __name__ == "__main__":
    main()
