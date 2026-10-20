"""
结果可视化（Result Visualization）
==================================
生成作品集两张核心图：
  1) results/coverage_map_9hubs.png       9 仓覆盖图（337 需求点 + 仓址 + 覆盖连线）
  2) results/cost_service_tradeoff.png    成本—时效比选图（P=1..15 边际分析）

用法: python src/plot_results.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

from config import PROCESSED_DIR, RESULTS_DIR, ROOT_DIR

# 中文字体
_fonts = {f.name for f in fm.fontManager.ttflist}
for cand in ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "SimHei", "Microsoft YaHei"]:
    if cand in _fonts:
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False


def load_excel_assignment() -> dict:
    """读取 9 仓方案的分配（data/processed/assignment_9hubs.csv，与 Excel 口径一致）。"""
    df = pd.read_csv(PROCESSED_DIR / "assignment_9hubs.csv")
    return dict(zip(df["需求点ID"], df["候选仓ID"]))


def plot_coverage() -> None:
    cities = pd.read_csv(PROCESSED_DIR / "raw/cities.csv") if (PROCESSED_DIR / "raw/cities.csv").exists() \
        else pd.read_csv(ROOT_DIR / "data/raw/cities.csv")
    demand = cities[cities["位置类型"] == "需求点"]
    hubs = cities[cities["位置类型"] == "候选仓"]

    assign = load_excel_assignment()
    hub_city = dict(zip(hubs["位置ID"], hubs["城市名称"]))
    assign_city = {i: hub_city[j] for i, j in assign.items()}

    colors = plt.cm.tab10.colors
    hub_list = sorted(set(assign.values()), key=lambda h: int(h[2:]))
    color_of = {h: colors[k % 10] for k, h in enumerate(hub_list)}
    coord = dict(zip(cities["位置ID"], list(zip(cities["经度"], cities["纬度"]))))

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.scatter(demand["经度"], demand["纬度"], s=8, c="#cbd5e1", alpha=0.7, label="需求点（337）", zorder=2)

    for i, j in assign.items():
        x1, y1 = coord[i]
        x2, y2 = coord[j]
        ax.plot([x1, x2], [y1, y2], color=color_of[j], lw=0.5, alpha=0.35, zorder=1)

    for h in hub_list:
        hx, hy = coord[h]
        ax.scatter([hx], [hy], s=260, c=[color_of[h]], marker="*", edgecolors="white", linewidths=1.2, zorder=4)
        ax.annotate(hub_city[h], (hx, hy), textcoords="offset points", xytext=(8, 6),
                    fontsize=10, fontweight="bold", zorder=5)

    ax.set_title("仓网覆盖方案 · 9 仓（337 地级行政区需求点）", fontsize=15, fontweight="bold")
    ax.set_xlabel("经度（Longitude）"); ax.set_ylabel("纬度（Latitude）")
    ax.set_xlim(72, 138); ax.set_ylim(16, 55)
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out = RESULTS_DIR / "coverage_map_9hubs.png"
    fig.savefig(out, dpi=150)
    print(f"[ok] {out}")


def plot_tradeoff() -> None:
    df = pd.read_csv(RESULTS_DIR / "sweep_p1_15.csv")
    df = df[df["status"] == "optimal"]
    fig, ax1 = plt.subplots(figsize=(11, 6.5))
    ax1.bar(df["p"], df["总成本_元每日"] / 10000, width=0.6, color="#94a3b8", alpha=0.75, label="总成本（万元/日）")
    ax1.set_xlabel("仓数 P（Number of Hubs）", fontsize=12)
    ax1.set_ylabel("总成本（万元/日）", fontsize=12)
    ax1.set_ylim(0, 90)
    ax1.grid(axis="y", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df["p"], df["D+1达成率"] * 100, "o-", color="#ef4444", lw=2.2, ms=6, label="D+1 达成率（%）")
    ax2.set_ylabel("D+1 次日达达成率（%）", fontsize=12, color="#ef4444")
    ax2.tick_params(axis="y", labelcolor="#ef4444")
    ax2.set_ylim(0, 100)
    ax2.axvspan(8.5, 9.5, color="#fef3c7", alpha=0.5, zorder=0)
    ax2.annotate("9 仓 = 甜点区\n边际收益衰减起点", xy=(9, 81), xytext=(10.5, 62),
                 fontsize=10, color="#b45309",
                 arrowprops=dict(arrowstyle="->", color="#b45309"))

    ax1.set_title("仓数边际分析：总成本 vs D+1 达成率（P=1..15）", fontsize=14, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)
    fig.tight_layout()
    out = RESULTS_DIR / "cost_service_tradeoff.png"
    fig.savefig(out, dpi=150)
    print(f"[ok] {out}")


if __name__ == "__main__":
    plot_coverage()
    plot_tradeoff()
