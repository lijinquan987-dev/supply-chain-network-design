# data/ —— 数据目录（Data）

- `raw/`：原始数据 —— 337 地级行政区经纬度表、高德城间距离/耗时表（**高德开放平台 API + Python 批量查询获取**，获取脚本见 `src/fetch_road_network.py`）
- `processed/`：模型输入 —— demand.csv（337 需求点）、candidates.csv（15 候选仓）、replenish.csv（15 条补货）、distance_cost.csv（5055 行=337×15）、solution_2hubs / solution_9hubs、assignment_9hubs（覆盖分配）

> 参数表（仓储/补货/配送成本、时效目标、容量）以常量形式在 `src/config.py` 与 `src/cost_timing_analysis.py` 中，口径见 `docs/data-dictionary.md`。

> 安全红线：高德 API Key（密钥）绝不入库（通过环境变量读取，`.gitignore` 排除 `.env`）；本目录仅存放可公开数据。
