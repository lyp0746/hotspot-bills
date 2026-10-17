# -*- coding: utf-8 -*-
"""make_tables.py —— 生成附录用的季度头部话题表（HTML 行），真实数据。"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(HERE, "data", "year_zhihu.json"), encoding="utf-8"))

Q = [("Q1（2025-10-16 ~ 2026-01-15）", "2025-10-16", "2026-01-15"),
     ("Q2（2026-01-16 ~ 2026-04-15）", "2026-01-16", "2026-04-15"),
     ("Q3（2026-04-16 ~ 2026-07-15）", "2026-04-16", "2026-07-15"),
     ("Q4（2026-07-16 ~ 2026-10-16，缺日）", "2026-07-16", "2026-10-16")]

out = []
for name, a, b in Q:
    days = [k for k in d if a <= k <= b]
    c = Counter()
    for k in days:
        for item in d[k]:
            c[item[0]] += 1
    out.append('<h3 id="sec10-%s">10.%s　%s（%d 天）</h3>' % (name[1], name[1], name, len(days)))
    out.append('<table class="nat">')
    out.append('<tr><th class="l">名次</th><th class="l">话题</th><th class="l">上榜天数</th><th class="l">占本季天数</th></tr>')
    for i, (t, n) in enumerate(c.most_common(30), 1):
        out.append('<tr><td class="l">%d</td><td class="l">%s</td><td class="l">%d</td><td class="l">%.0f%%</td></tr>'
                   % (i, t, n, 100.0 * n / len(days)))
    out.append('</table>')

open(os.path.join(HERE, "data", "quarter_tables.html"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
