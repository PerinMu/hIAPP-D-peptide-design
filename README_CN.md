# 中文评审导航

本仓库是第一届全球大学生生命科学挑战赛 Track 1 的公开代码与可复现性材料，
用于评委运行复核、结果追踪和答辩查阅。英文 README 与技术文档为完整、权威版本。

## 五分钟快速复核

```bash
git clone https://github.com/PerinMu/hIAPP-D-peptide-design.git
cd hIAPP-D-peptide-design
conda env create -f environment.yml
conda activate hiapp-d-peptide-analysis
bash run.sh
```

运行后将得到 `results/submission/results.csv`。程序会重新计算并核对：

```text
9,806 条进入排序 → 904 条通过硬筛选 → 42 条进入结构复核 → 12 条最终候选
```

## 评审入口

- [完整英文 README](README.md)：环境、运行命令、输入输出和项目创新点。
- [完整 GPU 工作流 Notebook](notebooks/00_full_generation_to_selection.ipynb)：从 BoltzGen、BoltzIF、D-肽转换、Boltz-2 预测到多指标筛选。
- [CPU 复现 Notebook](notebooks/01_reproduce_screening.ipynb)：无需 GPU，复现全部筛选数量与最终清单。
- [附件5逐项合规表](docs/COMPETITION_COMPLIANCE.md)：代码提交要求与仓库证据的一一对应。
- [赛道评分对照](docs/SCORING_ALIGNMENT.md)：五项评分标准与仓库材料、证据边界的对应关系。
- [Model Card](MODEL_CARD.md)：第三方模型、参数、版本、适用范围与局限。
- [生产环境记录](docs/PRODUCTION_ENVIRONMENT.md)：权重哈希、依赖、GPU、CUDA、运行时间和调度记录。
- [最终结果 CSV](results/submission/results.csv)与[格式化 Excel](results/submission/results.xlsx)：12 条候选及对应模型、指标和结构文件。

## 项目边界

团队使用开源预训练的 BoltzGen、BoltzIF 和 Boltz-2，没有自行训练或微调模型。
项目创新集中在通用 D-肽从头设计工作流、显式立体化学编码、失败任务恢复、
理化性质计算、多目标优先级筛选和可追踪的 hIAPP 案例验证。

湿实验正在进行，本次公开版本不包含尚未完成质量控制的实验数据，也不把模型分数
表述为实测活性。历史随机种子等无法恢复的信息已在 Model Card 和生产环境记录中
如实披露，没有使用推测值填补。
