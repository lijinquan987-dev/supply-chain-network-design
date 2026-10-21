#!/usr/bin/env python3
"""生成 docs/19plus2-framework.svg —— 19+2 城市群框架长图（上下结构，官方地图版）
上：空间骨架 —— 嵌入《国家综合立体交通网骨干网示意图》（官方地图，base64 内嵌，自包含可离线渲染）
中：三层关系链（337 ⊃ 19+2 ⊃ 15 ⊃ 9）
下：候选仓映射明细 + 选仓逻辑
"""
import base64
from pathlib import Path

W = 1240
FONT = "'Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif"
MAP_PATH = "/home/user/.doubao/agent_mode/workspace/.sessions/38448286510269698/attachments/810c2288cd30bd72a1866cae297b67c1.png"

parts = []
def add(s): parts.append(s)

def text(x, y, s, size=14, fill="#0f172a", weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')

def rect(x, y, w, h, fill, rx=8, stroke="none", sw=0):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

# ============ 文档头（总高 1770） ============
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="1770" viewBox="0 0 {W} 1770" style="background:#f8fafc;">')

# ============ 标题 ============
rect(0, 0, W, 92, "#0f172a", rx=0)
text(W/2, 38, "19+2 城市群框架：从全国需求到仓网骨架", 24, "#ffffff", "bold", "middle")
text(W/2, 66, "依据《国家综合立体交通网规划纲要》(2021) · 4极 / 8组群 / 9组团 = 21 个空间单元 · 6轴 / 7廊 / 8通道", 13, "#cbd5e1", "normal", "middle")

# ============ 第 1 区：空间骨架 = 官方骨干网地图 ============
rect(24, 112, W-48, 908, "#ffffff", 12, "#e2e8f0", 1)
text(44, 148, "① 空间骨架：国家综合立体交通网骨干网示意图（官方地图）", 17, "#0f172a", "bold")

# 官方地图 base64 内嵌（1108×774，宽 1112 → 高 777）
b64 = base64.b64encode(Path(MAP_PATH).read_bytes()).decode("ascii")
add(f'<image x="64" y="172" width="1112" height="777" href="data:image/png;base64,{b64}" preserveAspectRatio="xMidYMid meet"/>')

# 地图下方图例（两行，SVG 元素绘制）
text(64, 968, "图例：", 13.5, "#334155", "bold")
lx = 130
add(f'<circle cx="{lx+6}" cy="963" r="5.5" fill="#ef4444"/>')
text(lx+18, 968, "4 极（红点）", 13, "#334155")
lx += 128
add(f'<circle cx="{lx+6}" cy="963" r="6" fill="none" stroke="#3b82f6" stroke-width="2"/>')
add(f'<circle cx="{lx+6}" cy="963" r="2.5" fill="#3b82f6"/>')
text(lx+18, 968, "8 组群（蓝双圈）", 13, "#334155")
lx += 150
add(f'<circle cx="{lx+6}" cy="963" r="5.5" fill="#f59e0b"/>')
text(lx+18, 968, "9 组团（黄橙渐变圆点）", 13, "#334155")
lx += 172
add(f'<line x1="{lx}" y1="963" x2="{lx+26}" y2="963" stroke="#f472b6" stroke-width="3"/>')
text(lx+32, 968, "6 轴（粉）", 13, "#334155")
lx += 108
add(f'<line x1="{lx}" y1="963" x2="{lx+26}" y2="963" stroke="#3b82f6" stroke-width="3"/>')
text(lx+32, 968, "7 廊（蓝）", 13, "#334155")
lx += 108
add(f'<line x1="{lx}" y1="963" x2="{lx+26}" y2="963" stroke="#facc15" stroke-width="3"/>')
text(lx+32, 968, "8 通道（黄）", 13, "#334155")

text(64, 996, "地图中红点标注四极位置，线条为国家级交通骨干；下方为政策目标口径。", 12.5, "#94a3b8")

# ============ 第 2 区：三层关系链 ============
rect(24, 1040, W-48, 250, "#ffffff", 12, "#e2e8f0", 1)
text(44, 1076, "② 三层关系：337 需求点 ⊃ 19+2 城市群 ⊃ 15 候选仓 ⊃ 9 仓方案", 17, "#0f172a", "bold")

chain = [
    ("337 需求点", "333 地级行政区 + 4 直辖市\n= 全国地级行政区划全集", "#0ea5e9"),
    ("19+2 城市群", "4极 + 8组群 + 9组团\n= 21 个空间单元（国家骨架）", "#ef4444"),
    ("15 候选仓", "4极全覆盖 + 8组群全覆盖\n+ 9组团选1（太原）", "#f59e0b"),
    ("9 仓方案", "模型最优解（甜点区）\n= 最终决策输出", "#22c55e"),
]
bw, bh = 268, 128
gap = 26
x0 = (W - (bw*4 + gap*3)) / 2
y0 = 1118
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
rect(24, 1310, W-48, 436, "#ffffff", 12, "#e2e8f0", 1)
text(44, 1346, "③ 候选仓映射明细：15 候选仓如何从 19+2 框架中筛出", 17, "#0f172a", "bold")

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
ty0 = 1378
for k, (title, hc, bg, tc, rows) in enumerate(tables):
    x = tx0[k]; w = tw[k]
    rect(x, ty0, w, 40, hc, 8)
    text(x+w/2, ty0+26, title, 14.5, "#ffffff", "bold", "middle")
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
print(f"[ok] {out} ({len(parts)} elements, {out.stat().st_size/1024:.0f} KB)")
