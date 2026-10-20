"""
仓数边际比选扫描（Marginal Cost & Service Trade-off Sweep）
===========================================================
对 P = 1..15 逐一求解全成本选址模型（无时效硬过滤，成本最优），
统计每个方案的：
  - 总成本（仓储+补货+配送，元/日）
  - D+1 / D+2 / D+3 / D+4 达成率（按单量加权，SLA ≤ 24/48/72/96h）
  - 边际成本（相对上一档 P-1 的成本变化）
输出 results/sweep_p1_15.csv，支撑「增减仓的边际成本 vs 时效收益」结论。

用法: python src/sweep_p.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pulp

from config import PROCESSED_DIR, RESULTS_DIR
from model_full import load_all, build_cost


def sla_achievement(assign: dict, dist: pd.DataFrame, threshold_h: int) -> float:
    """按单量加权统计 SLA <= threshold 的达成率。"""
    w = dict(zip(dist["需求点ID"], dist["需求城市"]))
    sla = {}
    for _, row in dist.iterrows():
        sla[(row["需求点ID"], row["候选仓ID"])] = row["快递运距时效SLA_h"]
    demand = pd.read_csv(PROCESSED_DIR / "demand.csv")
    wt = dict(zip(demand["需求点ID"], demand["日均单量_单"]))
    total = sum(wt[i] for i in assign)
    hit = sum(wt[i] for i, j in assign.items() if sla.get((i, j), 1e9) <= threshold_h)
    return hit / total if total else 0.0


def solve_p(p: int, demand, candidates, cost) -> tuple[list, dict, float, dict]:
    demand_ids = demand["需求点ID"].tolist()
    cand_ids = candidates["候选仓ID"].tolist()
    prob = pulp.LpProblem(f"p_{p}", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", [(i, j) for i in demand_ids for j in cand_ids], cat="Binary")
    y = pulp.LpVariable.dicts("y", cand_ids, cat="Binary")
    prob += pulp.lpSum(cost[(i, j)]["total"] * x[(i, j)] for i in demand_ids for j in cand_ids)
    for i in demand_ids:
        prob += pulp.lpSum(x[(i, j)] for j in cand_ids) == 1
    for i in demand_ids:
        for j in cand_ids:
            prob += x[(i, j)] <= y[j]
    prob += pulp.lpSum(y[j] for j in cand_ids) == p
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=600))

    if pulp.LpStatus[prob.status] != "Optimal":
        return [], {}, 0.0, {}

    opened = sorted(j for j, v in y.items() if v.varValue and v.varValue > 0.5)
    assign = {i: j for (i, j), v in x.items() if v.varValue and v.varValue > 0.5}
    wh = rep = dlv = 0.0
    for (i, j), v in x.items():
        if v.varValue and v.varValue > 0.5:
            wh += cost[(i, j)]["warehouse"]
            rep += cost[(i, j)]["replenish"]
            dlv += cost[(i, j)]["delivery"]
    return opened, assign, wh + rep + dlv, {"wh": wh, "rep": rep, "dlv": dlv}


def main() -> None:
    demand, candidates, repl, dist = load_all()
    cost, _ = build_cost(demand, candidates, repl, dist)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    prev_total = None
    for p in range(1, 16):
        opened, assign, total, parts = solve_p(p, demand, candidates, cost)
        if not assign:
            rows.append({"p": p, "status": "infeasible"})
            continue
        marginal = (total - prev_total) if prev_total is not None else None
        d1 = sla_achievement(assign, dist, 24)
        d2 = sla_achievement(assign, dist, 48)
        d3 = sla_achievement(assign, dist, 72)
        rows.append({
            "p": p, "status": "optimal",
            "总成本_元每日": round(total, 0),
            "仓储成本_元每日": round(parts["wh"], 0),
            "补货成本_元每日": round(parts["rep"], 0),
            "配送成本_元每日": round(parts["dlv"], 0),
            "D+1达成率": round(d1, 4), "D+2达成率": round(d2, 4),
            "D+3达成率": round(d3, 4),
            "边际成本_元每日": round(marginal, 0) if marginal is not None else "",
            "开设仓": "|".join(opened),
        })
        prev_total = total
        print(f"P={p:>2}: 成本 {total:>12,.0f}  D+1 {d1*100:5.1f}%  D+2 {d2*100:5.1f}%  "
              f"仓 {len(opened)}  {'边际 ' + f'{marginal:+,.0f}' if marginal is not None else ''}")

    with (RESULTS_DIR / "sweep_p1_15.csv").open("w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"\n[ok] 比选结果: {RESULTS_DIR / 'sweep_p1_15.csv'}")


if __name__ == "__main__":
    main()
