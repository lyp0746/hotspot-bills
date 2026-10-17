# -*- coding: utf-8 -*-
"""make_figures.py —《热点的账单》插图（确定性生成）→ assets/svg/fig-*.svg"""
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "svg")
INK = "#1a1a1a"; GRY = "#666"; BLU = "#2f6db0"; GRN = "#2e7d32"
ORG = "#ef6c00"; RED = "#c62828"; GLD = "#b8862f"; PNK = "#8e5a9c"
FONT = "Microsoft YaHei, PingFang SC, SimHei, sans-serif"


def head(w, h, title, sub=None):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">',
         f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
         f'<text x="{w/2:.0f}" y="38" text-anchor="middle" font-size="22" font-weight="bold" fill="{INK}">{title}</text>']
    if sub:
        s.append(f'<text x="{w/2:.0f}" y="62" text-anchor="middle" font-size="14" fill="{GRY}">{sub}</text>')
    return s


def box(x, y, w, h, fill, stroke, rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'


def txt(x, y, t, size=14, fill=INK, anchor="middle", weight="normal"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" font-weight="{weight}">{t}</text>'


def save(name, parts):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts + ["</svg>"]))
    print("wrote", name + ".svg")


def fig_lenses():
    W, H = 960, 560
    s = head(W, H, "六核诊断法：六把尺子，量一个热点", "每一把都不问“谁对”，只问“卡在哪”")
    items = [("看见", "区分", "在划什么线？", BLU),
             ("记住", "容量 / 遗忘", "丢了什么？", GRN),
             ("跟上", "时间错配 τ", "差多少？", ORG),
             ("选择", "C-A-T 三角", "让出哪一样？", GLD),
             ("讲述", "置信度分配", "在哪一层？", PNK),
             ("临界", "相变 / 门槛", "还是它吗？", RED)]
    x0, y0, cw, ch, gap = 30, 100, 146, 380, 8
    for i, (name, role, q, col) in enumerate(items):
        x = x0 + i * (cw + gap)
        s.append(box(x, y0, cw, ch, "#fbfcfe", col))
        s.append(f'<rect x="{x}" y="{y0}" width="{cw}" height="64" rx="8" fill="{col}" opacity="0.15"/>')
        s.append(txt(x + cw / 2, y0 + 42, name, 24, col, weight="bold"))
        s.append(txt(x + cw / 2, y0 + 100, role, 14, GRY))
        # 尺子图形
        s.append(f'<line x1="{x+cw/2:.0f}" y1="{y0+140}" x2="{x+cw/2:.0f}" y2="{y0+300}" stroke="{col}" stroke-width="4"/>')
        for k in range(6):
            yy = y0 + 150 + k * 28
            s.append(f'<line x1="{x+cw/2-14}" y1="{yy}" x2="{x+cw/2+14}" y2="{yy}" stroke="{col}" stroke-width="2"/>')
        s.append(f'<text x="{x+cw/2}" y="{y0+345}" text-anchor="middle" font-size="14" fill="{INK}">{q}</text>')
    s.append(txt(W / 2, H - 24, "六个问题问完，一个热点就变成一张有结构的图。", 14, GRY))
    save("fig-five-lens", s)


def fig_card():
    W, H = 900, 620
    s = head(W, H, "一张诊断卡：把五个问题合起来", "每个热点，填一张这样的卡")
    fields = [("事件 / 时间 / 平台", "一句话", GRY),
              ("① 看见", "关键分界线；被划入 / 划出的人", BLU),
              ("② 记住", "被压缩成的标签；丢掉的条件", GRN),
              ("③ 跟上", "快钟 / 慢钟；τ 的粗略量级", ORG),
              ("④ 选择", "各方要的两样；让出的一样", GLD),
              ("⑤ 讲述", "争吵所在层；位置冲突 or 事实冲突", PNK)]
    x, y, w, h, gap = 170, 96, 560, 58, 12
    for i, (k, v, col) in enumerate(fields):
        yy = y + i * (h + gap)
        s.append(box(x, yy, w, h, "#fbfcfe", col))
        s.append(f'<rect x="{x}" y="{yy}" width="150" height="{h}" rx="8" fill="{col}" opacity="0.14"/>')
        s.append(txt(x + 75, yy + 36, k, 16, col, weight="bold"))
        s.append(txt(x + 170, yy + 36, v, 14, INK, anchor="start"))
    yb = y + len(fields) * (h + gap) + 6
    s.append(box(x, yb, w, 54, "#fff8e1", GLD))
    s.append(txt(x + 20, yb + 34, "诊断结论 ＋ 证据等级（A/B/C）＋ 可反驳条件", 15, GLD, anchor="start", weight="bold"))
    save("fig-diagnosis-card", s)


def fig_clocks():
    W, H = 900, 480
    s = head(W, H, "“跟上”：事情变快的速度 ÷ 你回应的速度", "τ = 需要的时间 ÷ 你有的时间；τ 越大，越只能说方向")
    rows = [("事件传播 / 情绪", "分钟 → 小时", 0.15, RED),
            ("平台 / 市场", "小时 → 天", 0.3, ORG),
            ("机构回应", "周 → 月", 0.6, GRN),
            ("调查 / 司法 / 政策", "月 → 年", 0.85, BLU),
            ("气候 / 人口 / 产业", "十年 → 百年", 1.0, PNK)]
    x0, y0, bw, bh, gap = 240, 100, 560, 46, 22
    for i, (name, sc, v, col) in enumerate(rows):
        y = y0 + i * (bh + gap)
        s.append(txt(x0 - 16, y + 30, name, 15, INK, anchor="end"))
        s.append(box(x0, y, bw * v, bh, col, col, rx=6))
        s.append(txt(x0 + bw * v + 12, y + 30, sc, 13, GRY, anchor="start"))
    s.append(txt(x0 + 120, 88, "快钟", 15, RED, anchor="start", weight="bold"))
    s.append(txt(x0 + 470, 88, "慢钟", 15, BLU, anchor="start", weight="bold"))
    s.append(txt(W / 2, H - 22, "冲击常来自快钟，而回应落在慢钟——这就是错位。", 14, GRY))
    save("fig-hotspot-clocks", s)


def fig_zhihu_vs_x():
    W, H = 920, 520
    s = head(W, H, "同一个世界，两个平台定义了两件不同的“大事”", "过去一年采样对比")
    # 左：知乎
    s.append(box(60, 96, 380, 360, "#eef4fb", BLU))
    s.append(txt(250, 134, "知乎：持续发酵的公共焦虑", 18, BLU, weight="bold"))
    zh = ["低成本爱好（122 天）", "人在什么情况下成长最快（77）", "黄金什么时候会大跌（58）",
          "中东危局（53）", "A 股（38）", "松弛感的孩子（43）"]
    for i, t in enumerate(zh):
        s.append(txt(84, 180 + i * 40, "· " + t, 14, INK, anchor="start"))
    s.append(txt(250, 430, "恒久的人生问题 + 持续数周的事件", 13, GRY))
    # 右：X
    s.append(box(480, 96, 380, 360, "#fff4e6", ORG))
    s.append(txt(670, 134, "X：快速更替的注意力流", 18, ORG, weight="bold"))
    xx = ["#AEWDynamite（9 次采样）", "Good Thursday（7）", "#Survivor50（5）",
          "Darby（4）", "Powell（3）", "Arsenal（3）"]
    for i, t in enumerate(xx):
        s.append(txt(504, 180 + i * 40, "· " + t, 14, INK, anchor="start"))
    s.append(txt(670, 430, "体育与娱乐 + 间歇的政治/金融", 13, GRY))
    s.append(txt(W / 2, H - 22, "平台替你划了线；不同的平台，划的是不同的线。", 14, GRY))
    save("fig-zhihu-vs-x", s)


def fig_quarters():
    W, H = 960, 470
    s = head(W, H, "四个季度：碎片化上升，集中度反复",
             "左：不同话题数（分散度）；右：前五名占比（集中度）。数据：知乎热榜存档")
    Q = [("Q1", 487, 10.1), ("Q2", 572, 8.0), ("Q3", 1091, 9.4), ("Q4", 993, 4.0)]
    # left panel
    ox, oy, w, h = 90, 360, 380, 240
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{ox+w}" y2="{oy}" stroke="#333" stroke-width="1.6"/>')
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-h}" stroke="#333" stroke-width="1.6"/>')
    s.append(txt(ox + w / 2, oy + 34, "不同话题数", 13, GRY))
    for i, (q, n, sh) in enumerate(Q):
        bx = ox + 30 + i * 88
        bh = n / 1200.0 * h
        s.append(f'<rect x="{bx}" y="{oy-bh:.0f}" width="46" height="{bh:.0f}" fill="{BLU}" opacity="0.8"/>')
        s.append(txt(bx + 23, oy - bh - 8, str(n), 12, BLU, weight="bold"))
        s.append(txt(bx + 23, oy + 20, q, 13, INK))
    # right panel
    ox2 = 560
    s.append(f'<line x1="{ox2}" y1="{oy}" x2="{ox2+w}" y2="{oy}" stroke="#333" stroke-width="1.6"/>')
    s.append(f'<line x1="{ox2}" y1="{oy}" x2="{ox2}" y2="{oy-h}" stroke="#333" stroke-width="1.6"/>')
    s.append(txt(ox2 + w / 2, oy + 34, "前五名占本季天数", 13, GRY))
    for i, (q, n, sh) in enumerate(Q):
        bx = ox2 + 30 + i * 88
        bh = sh / 12.0 * h
        s.append(f'<rect x="{bx}" y="{oy-bh:.0f}" width="46" height="{bh:.0f}" fill="{ORG}" opacity="0.85"/>')
        s.append(txt(bx + 23, oy - bh - 8, f"{sh}%", 12, ORG, weight="bold"))
        s.append(txt(bx + 23, oy + 20, q, 13, INK))
    s.append(txt(W / 2, H - 22, "Q4 存档只有 70 天，因此它的低占比不能直接读成“更分散”。", 13, RED))
    save("fig-quarters", s)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in [fig_lenses, fig_card, fig_clocks, fig_zhihu_vs_x, fig_quarters]:
        f()
    print("done")


if __name__ == "__main__":
    main()
