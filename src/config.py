"""
配置模块（Configuration）
========================
统一管理项目配置。安全红线（Security Red Line）：
高德 API Key（密钥）绝不硬编码进代码 / 仓库，一律从环境变量或 .env 读取。
"""
from __future__ import annotations

import os
from pathlib import Path

# 项目根目录（src/ 的上一级）
ROOT_DIR = Path(__file__).resolve().parent.parent

# 数据目录
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PARAMS_DIR = ROOT_DIR / "data" / "params"
RESULTS_DIR = ROOT_DIR / "results"
MODEL_DIR = ROOT_DIR / "model"


def load_dotenv() -> None:
    """轻量加载 .env（若存在），避免额外依赖 python-dotenv。"""
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def get_amap_api_key() -> str:
    """
    获取高德 API Key。
    读取顺序：环境变量 AMAP_API_KEY -> .env 文件。
    未配置时直接报错，绝不使用默认值/占位值发起请求。
    """
    load_dotenv()
    key = os.environ.get("AMAP_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "未找到高德 API Key。请执行: export AMAP_API_KEY='your_key' "
            "或创建 .env 文件（已被 .gitignore 忽略）。"
        )
    return key
