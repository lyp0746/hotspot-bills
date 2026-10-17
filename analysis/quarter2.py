# -*- coding: utf-8 -*-
"""quarter2.py —— 季度结构指标（真实数据，供正文引用）。"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(HERE, "data", "year_zhihu.json"), encoding="utf-8"))

Q = [("Q1", "2025-10-16", "2026-01-15"),
     ("Q2", "2026-01-16", "2026-04-15"),
     ("Q3", "2026-04-16", "2026-07-15"),
     ("Q4", "2026-07-16", "2026-10-16")]

rows = []
for name, a, b in Q:
    days = [k for k in d if a <= k <= b]
    c = Counter()
    total = 0
    for k in days:
        total += len(d[k])
        for item in d[k]:
            c[item[0]] += 1
    top5 = sum(n for _, n in c.most_common(5))
    rows.append((name, len(days), total, len(c), c.most_common(1)[0][1], top5, round(100.0 * top5 / total, 1)))

out = ["| 季度 | 存档天数 | 话题日总数 | 不同话题 | 头名上榜天数 | 前五名合计 | 前五占比 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    out.append("| %s | %d | %d | %d | %d | %d | %.1f%% |" % r)
open(os.path.join(HERE, "data", "quarter_stats.md"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
