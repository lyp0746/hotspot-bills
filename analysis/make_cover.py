# -*- coding: utf-8 -*-
"""make_cover.py — 生成《热点的账单》满版封面 SVG（A4 1000×1414）。"""
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "svg", "cover.svg")


def build():
    W, H = 1000, 1414
    ink = "#e8e6df"
    dim = "#9aa0a6"
    gold = "#b8862f"
    layers = []

    # 母题：一条热搜的起伏曲线 + 六个“镜头”圆
    cx, base = 500, 760
    pts = []
    for i in range(0, 101):
        t = i / 100
        x = 120 + t * 760
        y = base - 180 * math.exp(-((t - 0.25) ** 2) / 0.02) - 250 * math.exp(-((t - 0.62) ** 2) / 0.012)
        pts.append(f"{x:.0f},{y:.0f}")
    layers.append('<polyline points="' + " ".join(pts) + '" fill="none" stroke="#5b6b7d" stroke-width="2"/>')
    # 六个镜头（六核）
    labels = ["看见", "记住", "跟上", "选择", "讲述", "临界"]
    for i in range(6):
        x = 180 + i * 128
        y = base + 70
        layers.append(f'<circle cx="{x}" cy="{y}" r="24" fill="none" stroke="{gold}" stroke-width="1.6" opacity="0.8"/>')
        layers.append(f'<line x1="{x-9}" y1="{y+9}" x2="{x-22}" y2="{y+22}" stroke="{gold}" stroke-width="2" opacity="0.7"/>')
        layers.append(f'<text x="{x}" y="{y+54}" text-anchor="middle" class="sm">{labels[i]}</text>')
    # 底部“账单”线
    layers.append(f'<line x1="120" y1="{base+150}" x2="880" y2="{base+150}" stroke="#7d8a99" stroke-width="1" opacity="0.5"/>')
    layers.append(f'<text x="500" y="{base+190}" text-anchor="middle" class="mid">看点，不如看账单</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#0e1117"/><stop offset="0.55" stop-color="#151a23"/>
<stop offset="1" stop-color="#0b0e14"/>
</linearGradient>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<rect x="0" y="0" width="{W}" height="8" fill="{gold}" opacity="0.85"/>
{chr(10).join(layers)}
<style>
text{{font-family:'Microsoft YaHei','SimHei',Arial,sans-serif;}}
.ttl{{font-size:112px;font-weight:700;letter-spacing:14px;fill:{ink};}}
.sub{{font-size:28px;fill:{dim};letter-spacing:2px;}}
.eng{{font-size:20px;fill:{dim};letter-spacing:1px;}}
.au{{font-size:30px;fill:{ink};letter-spacing:2px;}}
.rule{{stroke:{dim};stroke-width:1;opacity:0.6;}}
.mid{{font-size:30px;fill:{gold};letter-spacing:6px;font-weight:700;}}
.sm{{font-size:20px;fill:#cfd6de;letter-spacing:1px;}}
</style>
<text x="80" y="176" class="eng">THE BILL OF THE HOT LIST</text>
<text x="80" y="300" class="ttl">热点的账单</text>
<line x1="84" y1="344" x2="720" y2="344" class="rule"/>
<text x="84" y="396" class="sub">用六个核心，</text>
<text x="84" y="440" class="sub">诊断过去一年的热搜与争论</text>
<text x="80" y="1230" class="au">李毅芃　著</text>
<text x="80" y="1282" class="eng">Six Lenses on a Year of Hot Debates</text>
<text x="80" y="1324" class="eng">通俗诊断读本 · 2026</text>
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
