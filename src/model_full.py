"""
全成本仓网选址模型（Total-cost Facility Location Model）
========================================================
在 P-中值（P-Median）基础上扩展为业务全成本口径，Python 复现 Excel + OpenSolver 对照版：

    目标  min  Σᵢⱼ xᵢⱼ · (仓储成本ᵢⱼ + 补货成本ᵢⱼ + 配送成本ᵢⱼ)

        仓储成本 = 需求点单量ᵢ × 候选仓单均固有成本分摊ⱼ
        补货成本 = 需求点日均货量ᵢ(kg) × 候选仓补货单价ⱼ(元/kg，按总仓-分仓距离区间定价)
        配送成本 = 需求点单量ᵢ × 快递单均配送成本ᵢⱼ（按城间运距）

    约束
        Σⱼ xᵢⱼ = 1                     每个需求点恰好被一个仓覆盖
        xᵢⱼ ≤ matchᵢⱼ                   时效匹配（候选仓 SLA ≤ 城市目标时效半径，可选）
        xᵢⱼ ∈ {0,1}

用法:
    python src/model_full.py                      # 无时效约束的全成本最优
    python src/model_full.py --time-filter        # 仅允许时效匹配的组合
    python src/model_full.py --time-filter --p 9  # 恰好 9 仓（与 Excel 方案对比）
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

try:
    import pulp
except ImportError:
    raise SystemExit("缺少依赖 pulp，请先执行: pip install pulp==2.7.0")

from config import PROCESSED_DIR, RESULTS_DIR


def load_all():
    demand = pd.read_csv(PROCESSED_DIR / "demand.csv")
    candidates = pd.read_csv(PROCESSED_DIR / "candidates.csv")
    repl = pd.read_csv(PROCESSED_DIR / "replenish.csv")
    dist = pd.read_csv(PROCESSED_DIR / "distance_cost.csv")
    return demand, candidates, repl, dist


def build_cost(demand, candidates, repl, dist) -> dict:
    """构造 (需求点, 候选仓) -> {仓储/补货/配送/总成本} 全成本字典。
    口径与 Excel OpenSolver 模型一致（0_总表 M/S/T/U 列）：
      仓储 = 单量 × (单均固有分摊 + 单均操作成本)
      补货 = 单量 × 单均重量(0.35 kg/单) × 补货运距单价(元/kg)
      配送 = 单量 × 单均快递成本
    """
    w = dict(zip(demand["需求点ID"], demand["日均单量_单"]))
    wh_fixed = dict(zip(candidates["候选仓ID"], candidates["单均固有成本分摊_元每单"]))
    wh_oper = dict(zip(candidates["候选仓ID"], candidates["单均操作费_元每单"]))
    rep_p = dict(zip(repl["候选仓ID"], repl["补货运距单价_元每kg"]))
    AVG_KG = 0.35  # 订单平均重量（kg/单），与 Excel 模型 0_总表 N 列一致

    # 配送成本/时效匹配 按 (需求点ID, 候选仓ID)
    d_cost = {}
    d_sla = {}
    d_match = {}
    for _, row in dist.iterrows():
        key = (row["需求点ID"], row["候选仓ID"])
        d_cost[key] = row["单均配送成本_元"]
        d_sla[key] = row["快递运距时效SLA_h"]
        d_match[key] = row["SLA与目标匹配"]

    cost = {}
    for (i, j) in d_cost:
        wh_c = w[i] * (wh_fixed[j] + wh_oper[j])   # 仓储 = 单量 × (分摊+操作)
        rep_c = w[i] * AVG_KG * rep_p[j]           # 补货 = 单量 × 均重 × 单价
        dlv_c = w[i] * d_cost[(i, j)]              # 配送 = 单量 × 单均快递成本
        cost[(i, j)] = {"warehouse": wh_c, "replenish": rep_c, "delivery": dlv_c,
                        "total": wh_c + rep_c + dlv_c}
    return cost, d_match


def solve(demand, candidates, cost, d_match, time_filter: bool, p: int | None):
    demand_ids = demand["需求点ID"].tolist()
    cand_ids = candidates["候选仓ID"].tolist()

    prob = pulp.LpProblem("total_cost_network", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", [(i, j) for i in demand_ids for j in cand_ids], cat="Binary")
    y = pulp.LpVariable.dicts("y", cand_ids, cat="Binary")

    prob += pulp.lpSum(cost[(i, j)]["total"] * x[(i, j)] for i in demand_ids for j in cand_ids)

    for i in demand_ids:
        prob += pulp.lpSum(x[(i, j)] for j in cand_ids) == 1, f"once_{i}"
    for i in demand_ids:
        for j in cand_ids:
            prob += x[(i, j)] <= y[j], f"link_{i}_{j}"
            if time_filter and d_match.get((i, j), 0) != 1:
                prob += x[(i, j)] == 0, f"time_{i}_{j}"
    if p is not None:
        prob += pulp.lpSum(y[j] for j in cand_ids) == p, f"p_{p}"

    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=600))
    return prob, x, y


def main():
    parser = argparse.ArgumentParser(description="全成本仓网选址模型（Python 复现 OpenSolver）")
    parser.add_argument("--time-filter", action="store_true", help="仅允许时效匹配组合")
    parser.add_argument("--p", type=int, default=None, help="固定仓数（不传则开放仓数）")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    demand, candidates, repl, dist = load_all()
    cost, d_match = build_cost(demand, candidates, repl, dist)
    prob, x, y = solve(demand, candidates, cost, d_match, args.time_filter, args.p)

    opened = sorted(j for j, v in y.items() if v.varValue and v.varValue > 0.5)
    assign = {i: j for (i, j), v in x.items() if v.varValue and v.varValue > 0.5}

    # 汇总
    wh = rep = dlv = 0
    for (i, j), v in x.items():
        if v.varValue and v.varValue > 0.5:
            wh += cost[(i, j)]["warehouse"]
            rep += cost[(i, j)]["replenish"]
            dlv += cost[(i, j)]["delivery"]
    total = wh + rep + dlv

    print(f"状态: {pulp.LpStatus[prob.status]}  | 仓数: {len(opened)}  | 仓: {opened}")
    print(f"成本(元/日): 仓储 {wh:,.0f} + 补货 {rep:,.0f} + 配送 {dlv:,.0f} = {total:,.0f}")
    print(f"模式: {'时效匹配过滤' if args.time_filter else '无时效过滤'} / P={args.p or '开放'}")

    if args.output:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with Path(args.output).open("w", newline="", encoding="utf-8-sig") as f:
            wr = csv.writer(f)
            wr.writerow(["需求点ID", "候选仓ID"])
            wr.writerows(sorted(assign.items()))
        print(f"[ok] 分配方案已写入: {args.output}")


if __name__ == "__main__":
    main()
