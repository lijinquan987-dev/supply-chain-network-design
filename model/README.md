# model/ —— 模型文件（Model）

Excel + OpenSolver 对照版模型说明：

- **原始模型**：基于 Excel + OpenSolver 搭建的仓网选址 MILP 模型（含业务口径参数），为本项目研究期使用。
- **存放状态**：该 `.xlsx` 为本地私有文件，**不随本仓库发布**（涉及业务口径参数，避免敏感信息外泄）。如需发布脱敏版模板，请在 `model/` 下放入后自行提交。
- **Python 对照实现**：`src/model_full.py`（全成本口径）与 `src/pmedian_model.py`（P-中值口径）已从该 Excel 模型提取全部参数并复现求解，完成双轨交叉验证：
  - Python（CBC）：9 仓方案总成本 **579,082 元/日**
  - Excel（OpenSolver）：9 仓方案总成本 **579,165 元/日**
  - 交叉验证误差 **0.014%**（详见 `README.md` 与 `results/sweep_p1_15.csv`）
