# -*- coding: utf-8 -*-
"""quarter.py —— 从 data/year_zhihu.json 统计四个季度的头部话题（真实数据）。"""
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(HERE, "data", "year_zhihu.json"), encoding="utf-8"))

Q = {
    "Q1（2025-10-16 ~ 2026-01-15）": ("2025-10-16", "2026-01-15"),
    "Q2（2026-01-16 ~ 2026-04-15）": ("2026-01-16", "2026-04-15"),
    "Q3（2026-04-16 ~ 2026-07-15）": ("2026-04-16", "2026-07-15"),
    "Q4（2026-07-16 ~ 2026-10-16）": ("2026-07-16", "2026-10-16"),
}

lines = []
for name, (a, b) in Q.items():
    days = [k for k in d if a <= k <= b]
    c = Counter()
    for k in days:
        for item in d[k]:
            c[item[0]] += 1
    lines.append("## %s　共 %d 天\n" % (name, len(days)))
    for t, n in c.most_common(15):
        lines.append("| %s | %d |" % (t, n))
    lines.append("")

open(os.path.join(HERE, "data", "quarter_topics.md"), "w", encoding="utf-8").write("\n".join(lines))
print("ok", sum(len(v) for v in d.values()))
