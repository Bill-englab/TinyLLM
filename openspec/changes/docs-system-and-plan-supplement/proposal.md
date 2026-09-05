# Proposal: docs-system-and-plan-supplement

## Why

仓库文档虽多(30+ 篇)但呈散点状:计划只在 code/学习路线图.md、进度散落在
README/路线图/各阶段检查清单三处、没有总索引,访客(包括未来的自己)难以定位。
同时,从 AI Infra 学习视角审查发现路线图存在内容缺口:阶段 3 只列了技术清单,
缺测量基础(profiling/roofline)、kernel 层(Triton/torch.compile/CUDA Graphs)、
7B 对比实验与基准方法论;阶段 4 缺真实监控管道与能耗指标。

## What Changes

- 建立四层文档体系并建索引:
  - `docs/INDEX.md` — 总索引(按类型 + 按阶段双视图)
  - `docs/plans/` — 计划层(学习路线图迁入 + 新增阶段 3 详细计划)
  - `docs/progress/PROGRESS.md` — 进度层(全局进度看板,唯一权威进度源)
  - 说明层(博客 docs/*.md + 各阶段 code/<stage>/docs/)与规格层
    (openspec/)维持现状,由索引统一收编
- 补充学习计划(AI Infra 视角):
  - 阶段 3 从 4 项平铺清单重构为 6 个模块,新增:测量基础(nsys/roofline/
    统一基准 harness)、KV cache 深入(公式实测+量化)、kernel 层
    (Triton/FlashAttention 原理/torch.compile/CUDA Graphs)、7B GPTQ 对比
  - 阶段 4 补:prometheus 真实管道、能耗 tok/J、性能回归 CI
  - 阶段 5 补:PD 分离概念、容器化时机说明
- 更新所有对学习路线图的引用(README/快速入门/项目结构说明/
  openspec config/skill 目录规范)

## Capabilities

### New Capabilities

- `docs-system`: 四层文档记录体系(索引/计划/进度/说明),每篇文档有唯一归属
- `learning-plan-v2`: 补充后的学习计划,覆盖 AI Infra 六层缺口

### Modified Capabilities

- `repo-documentation`: 入口文档接入新文档体系(README 指向 INDEX 与 PROGRESS)

## Impact

- 新增:`docs/INDEX.md`、`docs/plans/stage-3-推理优化.md`、`docs/progress/PROGRESS.md`
- 迁移:`code/学习路线图.md` → `docs/plans/学习路线图.md`(git mv 保留历史)
- 修改:`docs/plans/学习路线图.md`(内容补充)、`README.md`、`快速入门.md`、
  `项目结构说明.md`、`openspec/config.yaml`、
  `skill/stage-organization/references/directory-structure.md`
- 不动:各阶段代码、博客、openspec 既有规格

## 所属阶段

跨阶段基础设施变更(文档体系 + 计划修订),不涉及学习代码。
完成定义:索引覆盖全部文档且链接有效、路线图含全部补充模块、
PROGRESS 与各阶段检查清单一致、openspec validate 通过、推送 GitHub。
