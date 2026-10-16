# -*- coding: utf-8 -*-
"""collect_x_history.py — 抓取过去一年 X（Twitter）按国家、按日期的趋势存档。

数据源：twtdata.com 的免费历史趋势存档
    https://twtdata.com/twitter-trends/<country>/<MM-DD-YYYY>/
该站有 Cloudflare 保护，需用无头 Chrome 取页面并执行 htmx 加载表格。

策略（对站点友好）：低频、串行、带缓存；按固定间隔采样，不逐日轰炸。
输出：data/year_x.json（{country: {date: [trends]}}）
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(DATA, "tmp", "x")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
COUNTRIES = ["usa", "united-kingdom", "japan"]
STEP_DAYS = 14  # 采样间隔

TREND_RE = re.compile(
    r'<a href="https://x\.com/search\?q=[^"]+"[^>]*class="font-medium[^"]*">([^<]+)</a>')


def chrome_dom(url, budget=9000):
    try:
        p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                            f"--virtual-time-budget={budget}", "--dump-dom", url],
                           capture_output=True, timeout=60)
        return p.stdout.decode("utf-8", "ignore")
    except Exception as e:
        print("   chrome err", str(e)[:80])
        return ""


def fetch_day(country, d):
    os.makedirs(CACHE, exist_ok=True)
    key = f"{country}_{d.strftime('%m-%d-%Y')}"
    fp = os.path.join(CACHE, key + ".html")
    if os.path.exists(fp) and os.path.getsize(fp) > 2000:
        html = open(fp, encoding="utf-8", errors="ignore").read()
    else:
        url = f"https://twtdata.com/twitter-trends/{country}/{d.strftime('%m-%d-%Y')}/"
        html = chrome_dom(url)
        if html:
            open(fp, "w", encoding="utf-8").write(html)
    trends = []
    for m in TREND_RE.finditer(html):
        t = m.group(1).strip()
        if t and t not in trends:
            trends.append(t)
    if not trends:
        m = re.search(r'<meta name="description" content="[^:]*:\s*([^."]+)', html)
        if m:
            trends = [x.strip() for x in m.group(1).split(",") if x.strip()]
    return trends[:50]


def daterange(start, end, step):
    d = start
    while d <= end:
        yield d
        d += dt.timedelta(days=step)


def main():
    end = dt.date(2026, 10, 16)
    start = dt.date(2025, 10, 16)
    out = {}
    for country in COUNTRIES:
        out[country] = {}
        days = list(daterange(start, end, STEP_DAYS))
        for i, d in enumerate(days, 1):
            tr = fetch_day(country, d)
            if tr:
                out[country][d.isoformat()] = tr
            print(f"  [{country}] {i}/{len(days)} {d} -> {len(tr)} trends", flush=True)
            time.sleep(0.8)
        with open(os.path.join(DATA, "year_x.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"  [saved] {country}", flush=True)
    with open(os.path.join(DATA, "year_x.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # 频次聚合
    lines = ["# 过去一年 X 趋势排行（按采样上榜次数）\n"]
    for country, days in out.items():
        freq = {}
        for iso, trs in days.items():
            for t in trs:
                freq.setdefault(t, []).append(iso)
        ranked = sorted(freq.items(), key=lambda kv: len(kv[1]), reverse=True)
        lines.append(f"\n## {country}（采样 {len(days)} 天，前 80）\n")
        for t, dd in ranked[:80]:
            lines.append(f"- **{t}** — {len(dd)} 次（{min(dd)} ~ {max(dd)}）")
    with open(os.path.join(DATA, "year_x_events.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote data/year_x.json and data/year_x_events.md")


if __name__ == "__main__":
    main()
