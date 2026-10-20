#!/usr/bin/env python3
"""生成 docs/19plus2-framework.svg —— 19+2 城市群框架长图（上下结构）
上：交通骨干骨架示意（四极菱形 + 6轴7廊8通道）
中：三层关系链（337 ⊃ 19+2 ⊃ 15 ⊃ 9）
下：候选仓映射明细 + 选仓逻辑
"""
from pathlib import Path

W = 1240
FONT = "'Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif"

parts = []
def add(s): parts.append(s)

def text(x, y, s, size=14, fill="#0f172a", weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')

def rect(x, y, w, h, fill, rx=8, stroke="none", sw=0):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

# ============ 文档头 ============
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="1470" viewBox="0 0 {W} 1470" style="background:#f8fafc;">')

# ============ 标题 ============
rect(0, 0, W, 92, "#0f172a", rx=0)
text(W/2, 38, "19+2 城市群框架：从全国需求到仓网骨架", 24, "#ffffff", "bold", "middle")
text(W/2, 66, "依据《国家综合立体交通网规划纲要》(2021) · 4极 / 8组群 / 9组团 = 21 个空间单元 · 6轴 / 7廊 / 8通道", 13, "#cbd5e1", "normal", "middle")

# ============ 第 1 区：交通骨干骨架示意 ============
rect(24, 112, W-48, 470, "#ffffff", 12, "#e2e8f0", 1)
text(44, 148, "① 空间骨架：4 极菱形结构 + 6 轴 / 7 廊 / 8 通道交通骨干（示意，非精确地图）", 17, "#0f172a", "bold")

# 四极菱形示意（左侧）
cx, cy = 250, 430
p = {"京津冀": (cx, cy-170), "成渝": (cx-150, cy+40), "粤港澳": (cx-40, cy+150), "长三角": (cx+160, cy-10)}
# 菱形连线
add(f'<line x1="{p["京津冀"][0]}" y1="{p["京津冀"][1]}" x2="{p["成渝"][0]}" y2="{p["成渝"][1]}" stroke="#ef4444" stroke-width="3" stroke-dasharray="7,5"/>')
add(f'<line x1="{p["京津冀"][0]}" y1="{p["京津冀"][1]}" x2="{p["长三角"][0]}" y2="{p["长三角"][1]}" stroke="#ef4444" stroke-width="3" stroke-dasharray="7,5"/>')
add(f'<line x1="{p["长三角"][0]}" y1="{p["长三角"][1]}" x2="{p["粤港澳"][0]}" y2="{p["粤港澳"][1]}" stroke="#ef4444" stroke-width="3" stroke-dasharray="7,5"/>')
add(f'<line x1="{p["成渝"][0]}" y1="{p["成渝"][1]}" x2="{p["粤港澳"][0]}" y2="{p["粤港澳"][1]}" stroke="#ef4444" stroke-width="3" stroke-dasharray="7,5"/>')
# 交叉轴
add(f'<line x1="{p["京津冀"][0]}" y1="{p["京津冀"][1]}" x2="{p["粤港澳"][0]}" y2="{p["粤港澳"][1]}" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4,4"/>')
add(f'<line x1="{p["成渝"][0]}" y1="{p["成渝"][1]}" x2="{p["长三角"][0]}" y2="{p["长三角"][1]}" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4,4"/>')
# 极核圆点
colors = {"京津冀": "#ef4444", "长三角": "#3b82f6", "粤港澳": "#10b981", "成渝": "#8b5cf6"}
for name, (x, y) in p.items():
    add(f'<circle cx="{x}" cy="{y}" r="26" fill="{colors[name]}" opacity="0.9"/>')
    text(x, y-34, name, 14, colors[name], "bold", "middle")
    add(f'<text x="{x}" y="{y+5}" font-family="{FONT}" font-size="13" fill="#ffffff" text-anchor="middle" font-weight="bold">极</text>')
# 标注
text(cx, cy+215, "6 轴（菱形主骨架）· 7 廊（区域走廊）· 8 通道（跨境/沿边）", 13.5, "#334155", "bold", "middle")

# 右侧：8 组群 + 9 组团
rx0, ry0 = 560, 178
rect(rx0, ry0-28, 320, 178, "#fff7ed", 10, "#fdba74", 1)
text(rx0+16, ry0, "8 组群（区域增长极）", 15, "#c2410c", "bold")
groups8 = "长江中游 · 山东半岛 · 海峡西岸 · 中原\n哈长 · 辽中南 · 北部湾 · 关中平原"
for i, line in enumerate(groups8.split("\n")):
    text(rx0+16, ry0+30+i*22, line, 13, "#431407")

rect(rx0, ry0+166, 320, 218, "#f5f3ff", 10, "#c4b5fd", 1)
text(rx0+16, ry0+194, "9 组团（补充培育）", 15, "#6d28d9", "bold")
groups9 = "呼包鄂榆 · 黔中 · 滇中 · 山西中部\n天山北坡 · 兰西 · 宁夏沿黄 · 拉萨 · 喀什"
for i, line in enumerate(groups9.split("\n")):
    text(rx0+16, ry0+224+i*22, line, 13, "#2e1065")

# 右上：道路要素
rect(rx0+340, ry0-28, 310, 344, "#eff6ff", 10, "#93c5fd", 1)
text(rx0+356, ry0, "交通骨干要素", 15, "#1d4ed8", "bold")
els = [("6 轴", "京哈—京港澳 · 陆桥 · 沿江\n沪昆 · 成渝昆 · 广昆", "#3b82f6"),
       ("7 廊", "绥满 · 京延 · 沿边 · 京藏\n大陆桥 · 川藏 · 广昆走廊", "#f59e0b"),
       ("8 通道", "额济纳 · 二连 · 满洲里 · 丹东\n沪昆 · 广昆 · 滇藏 · 南北沿边", "#8b5cf6")]
y = ry0+34
for name, desc, c in els:
    add(f'<circle cx="{rx0+366}" cy="{y+6}" r="6" fill="{c}"/>')
    text(rx0+380, y+10, name, 14, c, "bold")
    for j, line in enumerate(desc.split("\n")):
        text(rx0+396, y+30+j*19, line, 11.5, "#334155")
    y += 86

# ============ 第 2 区：三层关系链 ============
rect(24, 602, W-48, 250, "#ffffff", 12, "#e2e8f0", 1)
text(44, 638, "② 三层关系：337 需求点 ⊃ 19+2 城市群 ⊃ 15 候选仓 ⊃ 9 仓方案", 17, "#0f172a", "bold")

chain = [
    ("337 需求点", "333 地级行政区 + 4 直辖市\n= 全国地级行政区划全集", "#0ea5e9"),
    ("19+2 城市群", "4极 + 8组群 + 9组团\n= 21 个空间单元（国家骨架）", "#ef4444"),
    ("15 候选仓", "4极全覆盖 + 8组群全覆盖\n+ 9组团选1（太原）", "#f59e0b"),
    ("9 仓方案", "模型最优解（甜点区）\n= 最终决策输出", "#22c55e"),
]
bw, bh = 268, 128
gap = 26
x0 = (W - (bw*4 + gap*3)) / 2
y0 = 676
for i, (t, d, c) in enumerate(chain):
    x = x0 + i*(bw+gap)
    rect(x, y0, bw, bh, c, 12)
    text(x+bw/2, y0+44, t, 18, "#ffffff", "bold", "middle")
    for j, line in enumerate(d.split("\n")):
        text(x+bw/2, y0+74+j*20, line, 12.5, "#ffffff", "normal", "middle")
    if i < 3:
        ax = x + bw + 2
        add(f'<text x="{ax+10}" y="{y0+66}" font-family="{FONT}" font-size="26" fill="#94a3b8" text-anchor="middle">⊃</text>')
text(W/2, y0+bh+34, "从「全国地图」到「国家骨架」再到「候选据点」，最后模型挑出「最优据点」", 14, "#64748b", "normal", "middle")

# ============ 第 3 区：候选仓映射明细 ============
rect(24, 882, W-48, 980, "#ffffff", 12, "#e2e8f0", 1)
text(44, 918, "③ 候选仓映射明细：15 候选仓如何从 19+2 框架中筛出", 17, "#0f172a", "bold")

# 三列表
tables = [
    ("① 4 极（消费主引擎）· 全覆盖", "#ef4444", "#fef2f2", "#991b1b",
     [("京津冀", "北京 · 保定（2仓）"), ("长三角", "无锡"), ("粤港澳大湾区", "广州"), ("成渝双城经济圈", "成都")]),
    ("② 8 组群（区域增长极）· 全覆盖", "#f59e0b", "#fffbeb", "#92400e",
     [("长江中游", "长沙"), ("中原", "郑州"), ("关中平原", "西安"), ("海峡西岸", "厦门"),
      ("辽中南", "沈阳"), ("山东半岛", "潍坊"), ("哈长", "长春 · 哈尔滨（2仓）"), ("北部湾", "南宁")]),
    ("③ 9 组团 · 选 1", "#8b5cf6", "#f5f3ff", "#5b21b6",
     [("山西中部", "太原 ✓"), ("呼包鄂榆 / 黔中 / 滇中", "—"), ("天山北坡 / 兰西 / 宁夏沿黄", "—"), ("拉萨 / 喀什", "—")]),
]
tw = [360, 360, 360]
tx0 = [48, 424, 800]
ty0 = 950
for k, (title, hc, bg, tc, rows) in enumerate(tables):
    x = tx0[k]; w = tw[k]
    rect(x, ty0, w, 40, hc, 8)
    text(x+w/2, ty0+26, title, 14.5, "#ffffff", "bold", "middle")
    # 表头
    rect(x, ty0+40, w/2, 30, bg, 0)
    rect(x+w/2, ty0+40, w/2, 30, bg, 0)
    text(x+16, ty0+60, "城市群", 13, tc, "bold")
    text(x+w/2+16, ty0+60, "候选仓", 13, tc, "bold")
    add(f'<line x1="{x+w/2}" y1="{ty0+40}" x2="{x+w/2}" y2="{ty0+40+30*len(rows)}" stroke="#e2e8f0" stroke-width="1"/>')
    for i, (g, c) in enumerate(rows):
        yy = ty0+70+i*30
        if i % 2 == 0:
            rect(x, yy, w, 30, "#ffffff", 0)
        else:
            rect(x, yy, w, 30, "#f8fafc", 0)
        gcol = "#64748b" if c == "—" else "#0f172a"
        ccol = "#94a3b8" if c == "—" else "#16a34a"
        cwt = "normal" if c == "—" else "bold"
        text(x+16, yy+20, g, 12.5, gcol)
        text(x+w/2+16, yy+20, c, 12.5, ccol, cwt)

# 选仓逻辑
ly = ty0 + 70 + max(len(t[3]) for t in tables) * 30 + 26
rect(48, ly, W-96, 96, "#eff6ff", 10, "#bfdbfe", 1)
text(72, ly+30, "选仓逻辑", 14.5, "#1e40af", "bold")
text(72, ly+56, "4 极全覆盖（消费主引擎）+ 8 组群全覆盖（区域增长极）+ 9 组团选太原（六轴交汇枢纽：京昆/陆桥通道）；", 13, "#1e40af")
text(72, ly+78, "京津冀与哈长因体量/纵深各设 2 仓 → 15 个候选仓 × 337 需求点 = 5055 条运距矩阵", 13, "#1e40af")

# 来源
text(48, ly+132, "来源：中共中央、国务院《国家综合立体交通网规划纲要》(2021) · 到 2035 年建成「全国 123 出行交通圈」「全球 123 快货物流圈」", 12.5, "#64748b")

add('</svg>')

out = Path("/home/user/Doubao/chats/38448286510269698/supply-chain-network-design/docs/19plus2-framework.svg")
out.write_text("\n".join(parts), encoding="utf-8")
print(f"[ok] {out} ({len(parts)} elements)")
