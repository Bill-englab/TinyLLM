# learning-plan-v2 变更规格

## ADDED Requirements

### Requirement: 阶段 3 计划须以测量为基础模块

补充后的阶段 3 计划 MUST 将"测量与基础"(GPU 体系结构、HBM 带宽实测、
roofline 分析、nsys profiling、统一基准 harness)列为第一个模块,
后续优化模块 MUST 引用该模块产出的测量基线。

#### Scenario: 测量先行

- **WHEN** 阅读 docs/plans/stage-3-推理优化.md
- **THEN** 模块 3.0 为测量与基础,包含 nsys、roofline、基准 harness 三项
- **AND** 其余模块的验证方式引用 3.0 产出的 harness 或 profiling 方法

### Requirement: 计划须覆盖六类 AI Infra 缺口

补充后的学习计划 MUST 覆盖以下六类内容(以模块或明确条目形式):
(1)硬件与测量层;(2)kernel/算子层(Triton、FlashAttention 原理、
torch.compile、CUDA Graphs);(3)引擎内部(vLLM 源码精读、KV cache 实测);
(4)基准方法论(P99、重复与方差、负载模型);(5)模型规模对比(7B GPTQ);
(6)概念性扩展(TP/PP、PD 分离、引擎横向对比)。

#### Scenario: kernel 层入计划

- **WHEN** 查看阶段 3 计划的 kernel 模块
- **THEN** 包含 Triton 入门实践与 FlashAttention 论文精读条目
- **AND** 包含 torch.compile 与 CUDA Graphs 实验

#### Scenario: 7B 对比入计划

- **WHEN** 查看阶段 3 计划
- **THEN** 存在 7B GPTQ 对比实验条目,用于验证 1B"量化不提速"结论的外推性

### Requirement: 阶段 4/5 计划须补监控与生产化缺口

阶段 4 计划 MUST 包含 prometheus 真实数据管道、能耗指标(tok/J)与
性能回归 CI;阶段 5 计划 MUST 包含 PD 分离概念条目。

#### Scenario: 监控管道落地

- **WHEN** 查看补充后的阶段 4 规划
- **THEN** prometheus + grafana 管道与能耗指标均在条目中
- **AND** 性能回归 CI 有明确归属(阶段 4 或 5,不得缺失)

### Requirement: 路线图与进度看板保持一致

`docs/plans/学习路线图.md` 的阶段状态 MUST 与 `docs/progress/PROGRESS.md`
一致,两文件 MUST 互相链接。

#### Scenario: 状态一致

- **WHEN** 对比路线图的进度表与 PROGRESS 看板
- **THEN** 各阶段状态描述一致
- **AND** PROGRESS 链接到路线图,路线图链接到 PROGRESS
