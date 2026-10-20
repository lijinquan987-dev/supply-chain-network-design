"""
P-中值选址模型（P-Median Facility Location Model）
===================================================
用 Python（pulp 混合整数规划）复现「Excel + OpenSolver」对照版，
回答：给定 P 个仓，选在哪、覆盖谁，使加权运输成本最小。

模型（Model Formulation）:
    minimize   Σᵢ Σⱼ dᵢⱼ · wᵢ · xᵢⱼ
    s.t.
        Σⱼ xᵢⱼ = 1                  ∀ i    每个需求点被且仅被一个仓覆盖
        xᵢⱼ ≤ yⱼ                     ∀ i,j 只能分配给已开设的仓
        Σⱼ yⱼ = P                          恰好开设 P 个仓
        Σᵢ wᵢ · xᵢⱼ ≤ Capⱼ          ∀ j    容量约束（可选）
        xᵢⱼ, yⱼ ∈ {0, 1}

用法:
    python src/pmedian_model.py --p 3
    python src/pmedian_model.py --p 3 --p 5 --p 7 --output results/comparison.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import pulp
except ImportError:
    raise SystemExit("缺少依赖 pulp，请先执行: pip install pulp")

from config import PROCESSED_DIR, RESULTS_DIR


def load_inputs(
    demand_file: str | None = None,
    candidate_file: str | None = None,
    distance_file: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    加载模型输入：
      demand.csv        需求点：city, weight(需求量/权重), [time_target_hours]
      candidates.csv    候选仓：city, [capacity]
      distance_matrix.csv 城间距离/成本：origin, dest, cost(或 distance_km)
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    demand = pd.read_csv(demand_file or PROCESSED_DIR / "demand.csv")
    candidates = pd.read_csv(candidate_file or PROCESSED_DIR / "candidates.csv")
    dist = pd.read_csv(distance_file or PROCESSED_DIR / "distance_matrix.csv")
    return demand, candidates, dist


def build_model(
    demand: pd.DataFrame,
    candidates: pd.DataFrame,
    dist: pd.DataFrame,
    p: int,
    use_capacity: bool = False,
    time_limit_s: int = 300,
) -> tuple[pulp.LpProblem, dict, dict]:
    """
    构建 P-中值模型。
    dist 中成本字段统一取 'cost'（可由距离×单位成本系数换算，见 cost_timing_analysis）。
    """
    demand_ids = demand["city"].tolist()
    cand_ids = candidates["city"].tolist()

    # 距离矩阵 -> 字典 {(i, j): cost}
    d = {}
    for _, row in dist.iterrows():
        key = (row["origin"], row["dest"])
        d[key] = float(row.get("cost", row.get("distance_km", np.inf)))

    prob = pulp.LpProblem(f"pmedian_p{p}", pulp.LpMinimize)

    # 决策变量（Decision Variables）
    # 经典 pulp API（2.7.x）：LpVariable.dicts；注意 pulp 4.x 已移除该写法
    x = pulp.LpVariable.dicts(
        "assign", [(i, j) for i in demand_ids for j in cand_ids], cat="Binary"
    )
    y = pulp.LpVariable.dicts("open", cand_ids, cat="Binary")

    # 目标：加权运输成本最小（Weighted Transportation Cost）
    prob += pulp.lpSum(
        d.get((i, j), 1e9) * demand.loc[demand["city"] == i, "weight"].iloc[0] * x[(i, j)]
        for i in demand_ids
        for j in cand_ids
    ), "total_weighted_cost"

    # 约束 1：每个需求点恰好被一个仓覆盖
    for i in demand_ids:
        prob += pulp.lpSum(x[(i, j)] for j in cand_ids) == 1, f"assign_once_{i}"

    # 约束 2：只能分配给已开设的仓
    for i in demand_ids:
        for j in cand_ids:
            prob += x[(i, j)] <= y[j], f"link_{i}_{j}"

    # 约束 3：恰好开设 P 个仓
    prob += pulp.lpSum(y[j] for j in cand_ids) == p, f"exactly_p_{p}"

    # 约束 4（可选）：容量约束
    if use_capacity and "capacity" in candidates.columns:
        cap = dict(zip(candidates["city"], candidates["capacity"]))
        for j in cand_ids:
            prob += (
                pulp.lpSum(
                    demand.loc[demand["city"] == i, "weight"].iloc[0] * x[(i, j)]
                    for i in demand_ids
                )
                <= cap[j] * y[j],
                f"capacity_{j}",
            )

    prob.solve(pulp.PULP_CBC_CMD(timeLimit=time_limit_s, msg=0))
    return prob, x, y


def extract_solution(
    prob: pulp.LpProblem,
    x: dict[tuple[str, str], pulp.LpVariable],
    y: dict[str, pulp.LpVariable],
) -> dict:
    """从求解结果提取：开设仓、分配表、目标值。
    直接读取变量字典（x / y）的取值，不依赖变量名解析，避免 pulp 命名清洗问题。
    """
    opened = [j for j, v in y.items() if v.varValue and v.varValue > 0.5]
    assign = {i: j for (i, j), v in x.items() if v.varValue and v.varValue > 0.5}
    return {
        "status": pulp.LpStatus[prob.status],
        "objective": pulp.value(prob.objective),
        "opened": opened,
        "assignment": assign,
    }


def run(p: int, **kwargs) -> dict:
    """单次求解入口，供 CLI 与批量比选复用。"""
    demand, candidates, dist = load_inputs(**kwargs)
    prob, x, y = build_model(demand, candidates, dist, p)
    return extract_solution(prob, x, y)


def main() -> None:
    parser = argparse.ArgumentParser(description="P-中值仓网选址模型")
    parser.add_argument("--p", type=int, action="append", required=True,
                        help="仓数 P，可传多个值做比选，如 --p 3 --p 5 --p 7")
    parser.add_argument("--output", default=None, help="比选结果输出 CSV 路径")
    parser.add_argument("--capacity", action="store_true", help="启用容量约束")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in args.p:
        print(f"==> 求解 P={p} ...")
        sol = run(p, use_capacity=args.capacity)
        print(f"    状态={sol['status']}  目标值={sol['objective']:.2f}")
        print(f"    开设仓: {', '.join(sol['opened'])}")
        rows.append({"p": p, "status": sol["status"], "objective": sol["objective"],
                     "opened": "|".join(sol["opened"])})

    out = args.output or RESULTS_DIR / "p_median_comparison.csv"
    with Path(out).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["p", "status", "objective", "opened"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[ok] 比选结果已写入: {out}")


if __name__ == "__main__":
    main()
