# data/ —— 数据目录（Data）

- `raw/`：原始数据 —— 337 地级行政区经纬度表、高德城间距离/耗时表（**公开数据**，材料归位后落地）
- `processed/`：模型输入 —— demand.csv、candidates.csv、distance_matrix.csv
- `params/`：参数表 —— 成本/时效参数（口径见 `docs/data-dictionary.md`）

> 安全红线：高德 API Key（密钥）绝不入库；本目录仅存放可公开数据。
