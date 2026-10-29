# 热点的账单 · 

> 用六个核心，诊断过去一年的热搜与争论
>
> **DOI**：10.5281/zenodo.23637708　·　概念 DOI：10.5281/zenodo.23440911　·　127 页 / 5 部分 / 19 章

热搜为什么总让人越看越看不懂？本书用同一个研究系列提炼出的六个核心（看见、记住、跟上、选择、讲述、临界），把过去一年知乎与 X 上被反复讨论的事件，逐一变成一张张“诊断卡”。它不是对事件的判决，而是对“争论为什么会吵成这样、它让出了什么”的结构诊断。前 26 张卡的案例来自真实数据：知乎热榜每日存档（2025-10-16 ~ 2026-10-16，338 天、2875 个话题）与 X 按国家按日期的历史趋势存档（美/英/日，81 个“国家—日”采样）；另附三张未接入存档计数的结构补卡（社保新规、骗婚、司法公信）。每张卡都标注证据等级与可反驳条件——结论强度不超过证据强度。全书另设季度复盘、方法自检、十个反例与一个可以自己动手的晚间工作坊。卷首《总纲　现实中不存在无限》给诊断加了一条总问：争论常常假设了一种无限；账单就是假设到期的那一刻。 第十九章把 2026 年 10 月的法国骚乱、选举碎片化与主权债务放在同一张账单上，诊断民主的边界与欧盟的困境：三种立场各自让出同一三角的一角，换政府不等于换配置。

---

## 结构

| 部分 | 标题 | 章数 | 起 → 止 |
|---|---|---:|---|
| 1 | 第一部分　方法与数据、注意力与制度 | 5 | 六核诊断法：六把尺子，量一个热点 → 制度、信任与边界 |
| 2 | 第二部分　诊断与自检 | 3 | 季度复盘：四个季度，四种形状 → 十个反例：什么情况下这张卡是错的 |
| 3 | 第三部分　案例：从一个人到一座城 | 5 | 自己动手：一个晚上做完一次完整诊断 → 身体、城市与代际 |
| 4 | 第四部分　复盘：长卡、追问与自检 | 3 | 五张长卡：一次完整的推演 → 十二句话：这一年的账单 |
| 5 | 第五部分　账单与执行 | 3 | 如果你想自己抓一份数据 → 法国的账单：当三种立场都不能单独执政 |

每章八段：主提问 → 场景开篇 → 导论 → 机制 → 表/图 → 反例 → 本章小结 → 一句话带走。
每个部分有满栏插图扉页（`assets/svg/part-NN.svg`）、一段部分导语与一段部分小结。

## 证据与自检

- 结论标注 **A/B/C** 证据等级与甲/乙/丙概念等级；结论强度不超过证据强度。
- 可证伪登记簿：`docs/preregistration/checkups.csv`（append-only）。
- 结构校阅：系列 lint 24 条规则，本书 **error 0 / warn 0**（见 `_series/lint/REPORT.md`）。

## 文件

| 路径 | 是什么 |
|---|---|
| `source/` | **唯一正文来源**（HTML）；`book.json` 元数据、`parts.json` 结构 |
| `analysis/` | 图表、统计、抓取脚本（可重跑） |
| `assets/` | 封面、SVG 图、CSS |
| `scripts/build.sh` | audit → 印刷 PDF → 电子版 → EPUB → Markdown |
| `docs/` | 方法、数据来源、缺口与登记簿 |

产物（`output/`、`release/`）不入库，可由 `source/` 重建。

## 引用

```
热点的账单：用六个核心，诊断过去一年的热搜与争论。李毅芃，2026。10.5281/zenodo.23637708
```

## 系列（九本书）

| 书 | 仓库 |
|---|---|
| 只能选两样 | [knowledge-tradeoffs](https://github.com/lyp0746/knowledge-tradeoffs) |
| 区分的语法 | [distinction-evolution](https://github.com/lyp0746/distinction-evolution) |
| 遗忘的边界 | [capacity-cascade](https://github.com/lyp0746/capacity-cascade) |
| 错位的时间 | [entropy-spiral](https://github.com/lyp0746/entropy-spiral) |
| 选择的代价 | [impossibility-triangle](https://github.com/lyp0746/impossibility-triangle) |
| 诠释的权衡 | [interpretation-tradeoff](https://github.com/lyp0746/interpretation-tradeoff) |
| 涌现的临界 | [emergence-critical](https://github.com/lyp0746/emergence-critical) |
| 心灵的分岔 | [mind-forks](https://github.com/lyp0746/mind-forks) |

十四篇工作论文与全部条目的 DOI 见 [series-workspace](https://github.com/lyp0746/series-workspace)。

## 许可

正文与图件 CC BY 4.0；脚本 MIT。
