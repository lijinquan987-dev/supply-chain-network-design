"""
成本—时效比选分析（Cost & Service-Level Trade-off Analysis）
===========================================================
在 P-中值选址结果之上，把「运输成本」扩展为「全成本（仓储+补货+配送）」，
并计算次日达达成率（Next-day Delivery Achievement Rate），
输出不同 P 值下的 成本—时效比选表，支撑「增减仓的边际成本 vs 时效收益」结论。

用法:
    python src/cost_timing_analysis.py --p 1 2 3 5 7 10 --output results/tradeoff.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from config import PARAMS_DIR, PROCESSED_DIR, RESULTS_DIR
from pmedian_model import load_inputs, build_model, extract_solution


def load_params() -> dict:
    """成本/时效参数（待材料归位后按实际口径填充）。"""
    params = {
        # 单位成本（元）
        "warehouse_fixed_cost": 0.0,      # 单仓固定成本/期（待填）
        "replenish_cost_per_km": 0.0,     # 干线补货单位成本 元/km·吨（待填）
        "last_mile_cost_per_km": 0.0,     # 末端配送单位成本 元/km·件（待填）
        "weight_to_ton": 1e-3,            # 权重->吨 换算（待填）
        # 时效
        "next_day_hours": 24,             # 次日达阈值（小时）
        "time_col": "duration_min",       # 距离矩阵中的耗时字段
    }
    return params


def compute_tradeoff(
    p_values: list[int],
    demand: pd.DataFrame,
    candidates: pd.DataFrame,
    dist: pd.DataFrame,
) -> list[dict]:
    params = load_params()
    rows = []
    for p in p_values:
        prob, x, y = build_model(demand, candidates, dist, p)
        sol = extract_solution(prob, x, y)
        if sol["status"] != "Optimal":
            rows.append({"p": p, "status": sol["status"], "objective": sol["objective"]})
            continue

        # 次日达达成率：被分配仓与需求点的耗时 <= 阈值 的加权比例
        dur = {}
        for _, r in dist.iterrows():
            dur[(r["origin"], r["dest"])] = r.get(params["time_col"], 1e9)
        weight = dict(zip(demand["city"], demand["weight"]))
        total_w = sum(weight.values())
        next_day_w = sum(
            weight[i]
            for i, j in sol["assignment"].items()
            if dur.get((j, i), 1e9) <= params["next_day_hours"] * 60
        )
        rows.append({
            "p": p,
            "status": sol["status"],
            "weighted_transport_cost": round(sol["objective"], 2),
            "next_day_achievement": round(next_day_w / total_w * 100, 2) if total_w else None,
            "opened": "|".join(sol["opened"]),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="成本—时效比选分析")
    parser.add_argument("--p", type=int, nargs="+", default=[1, 2, 3, 5, 7, 10],
                        help="待比选的仓数 P 列表")
    parser.add_argument("--output", default=None, help="输出 CSV 路径")
    args = parser.parse_args()

    demand, candidates, dist = load_inputs()
    rows = compute_tradeoff(args.p, demand, candidates, dist)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = args.output or RESULTS_DIR / "cost_timing_tradeoff.csv"
    with Path(out).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"[ok] 比选结果已写入: {out}")


if __name__ == "__main__":
    main()
