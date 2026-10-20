"""公共工具模块（Utilities）：数据加载、覆盖率计算、画图辅助等。"""
from __future__ import annotations

import pandas as pd

from config import PROCESSED_DIR


def load_demand() -> pd.DataFrame:
    """加载需求点（337 地级行政区 + 权重）。"""
    return pd.read_csv(PROCESSED_DIR / "demand.csv")


def load_candidates() -> pd.DataFrame:
    """加载候选仓。"""
    return pd.read_csv(PROCESSED_DIR / "candidates.csv")


def load_distance_matrix() -> pd.DataFrame:
    """加载城间距离/耗时矩阵。"""
    return pd.read_csv(PROCESSED_DIR / "distance_matrix.csv")


def coverage_share(assignment: dict[str, str], weights: dict[str, float]) -> dict[str, float]:
    """按仓汇总覆盖份额：{仓: 覆盖需求量占比}。"""
    total = sum(weights.values())
    share: dict[str, float] = {}
    for city, hub in assignment.items():
        share[hub] = share.get(hub, 0.0) + weights[city]
    return {k: round(v / total * 100, 2) for k, v in share.items()}
