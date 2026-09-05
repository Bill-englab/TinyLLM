# curriculum-system Specification

## Purpose
TBD - created by archiving change build-curriculum-system. Update Purpose after archive.
## Requirements
### Requirement: 课程结构循序渐进

课程大纲 MUST 按"篇→讲"两级组织,篇间顺序遵循依赖关系
(测量基础→推理机制→量化→kernel→训练→服务化→分布式),
每讲 MUST 标注先修讲次与预计时长。

#### Scenario: 依赖顺序正确

- **WHEN** 按大纲顺序到达第 2 篇(KV cache/批处理)
- **THEN** 其先修内容(显存带宽、roofline)已出现在第 1 篇
- **AND** 训练侧内容(第 5 篇)排在推理侧(第 1-4 篇)之后

#### Scenario: 每讲有节奏结构

- **WHEN** 查看任意一讲
- **THEN** 包含理论要点、实践任务、产出物、自测题四要素
- **AND** 标注预计时长(小时)与类型(理论/实践/复习/概念)

### Requirement: 覆盖面试所需知识域

课程 MUST 覆盖以下六大主题域,每域至少 3 讲:GPU 体系结构与测量、
推理引擎机制、量化、kernel/编译、训练与微调(SFT/LoRA/蒸馏)、
分布式与服务化;且每篇 MUST 附面试高频考点清单。

#### Scenario: 训练微调覆盖

- **WHEN** 查看第 5 篇
- **THEN** 包含训练显存算术、QLoRA 实战、蒸馏(含投机采样联动)三讲以上
- **AND** 含分布式训练概念(DDP/FSDP/ZeRO)条目

#### Scenario: 面试考点可检索

- **WHEN** 大纲末尾的"面试高频题速查"
- **THEN** 按篇组织,题量 ≥25 且每题可回链到所属讲次

### Requirement: 实践与本机硬件匹配

每个实践类讲次的任务 MUST 可在 RTX 3070 8GB + WSL2 环境完成;
超出硬件的任务 MUST 明确标注"概念学习"并给出替代学习方式(论文/源码笔记)。

#### Scenario: 硬件约束透明

- **WHEN** 课程涉及 7B 模型实验
- **THEN** 使用社区预量化 GPTQ 模型并注明显存预算
- **AND** 自行量化实验限定在 3B 规模以内

#### Scenario: 概念讲诚实标注

- **WHEN** 课程涉及 TP/PP/NCCL 实验
- **THEN** 标注为概念学习,不宣称完成硬件实验

### Requirement: 与仓库工程体系双向映射

课程大纲 MUST 提供篇↔代码目录↔旧学习阶段的映射表,
每讲的产出物 MUST 落在对应代码目录或 docs/ 下。

#### Scenario: 产出物有归属

- **WHEN** 完成任一讲的实践任务
- **THEN** 其产出物路径可由映射表唯一确定

