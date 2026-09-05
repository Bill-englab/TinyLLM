# 📚 TinyLLM 文档总索引(INDEX)

> 本页是仓库文档体系的唯一入口。所有计划、进度、说明、规格从这里出发,
> 3 次点击内可达任意文档。
> 文档归置规则与各层职责见 [项目结构说明.md](../项目结构说明.md)。

## 🗺️ 快速路径

| 你想… | 去这里 |
|-------|--------|
| 了解这个项目是什么 | [README](../README.md) → [学习路线图](plans/学习路线图.md) |
| 看当前进度 | [PROGRESS 进度看板](progress/PROGRESS.md) |
| 跑起来某个应用 | [快速入门](../快速入门.md) |
| 按顺序系统学习 | 博客 [01](01-模型部署篇.md) → [02](02-AI推理优化环境搭建篇.md) → [03](03-模型量化篇.md) |
| 开始阶段 3 学习 | [阶段 3 详细计划](plans/stage-3-推理优化.md) |
| 提出一个变更 | `openspec/`(用法见 [openspec/config.yaml](../openspec/config.yaml) 与 `.claude/commands/opsx/`) |

---

## 🗂️ 视图一:按内容类型

### 📋 计划层(`docs/plans/`)
| 文档 | 说明 |
|------|------|
| [学习路线图](plans/学习路线图.md) | 5 阶段总路线(含 AI Infra 缺口审查记录) |
| [stage-3-推理优化](plans/stage-3-推理优化.md) | 阶段 3 执行级计划:6 模块/验收标准/风险备选 |

### 📊 进度层(`docs/progress/`)
| 文档 | 说明 |
|------|------|
| [PROGRESS](progress/PROGRESS.md) | **唯一权威进度源**:状态总览/关键数据汇总/更新日志 |

### 📖 说明层 — 博客(`docs/`)
| 文档 | 对应阶段 |
|------|----------|
| [01-模型部署篇](01-模型部署篇.md) | 阶段 1 |
| [02-AI推理优化环境搭建篇](02-AI推理优化环境搭建篇.md) | 阶段 1.5 |
| [03-模型量化篇](03-模型量化篇.md) | 阶段 2 |
| *(待产出)* 04-推理优化篇 | 阶段 3 |

### 📄 说明层 — 阶段技术文档(`code/<stage>/docs/`)
| 阶段 | 入口 |
|------|------|
| 1 部署 | [deployment/docs/](../code/deployment/docs/):使用指南 · 项目总结 · 文件整理说明 |
| 1.5 环境 | [environment_setup/docs/](../code/environment_setup/docs/):技术总结 · 问题记录 · 代码说明 · 使用指南 |
| 2 量化 | [quantization/docs/](../code/quantization/docs/):**量化基础概念** · 技术总结 · 问题记录 · 代码说明 · 使用指南 |

### ⚙️ 规格层(`openspec/`)
| 内容 | 位置 |
|------|------|
| 生效规格(仓库版本控制/文档体系) | `openspec/specs/` |
| 归档变更(决策历史) | `openspec/changes/archive/` |
| 项目上下文(变更创建时读取) | [openspec/config.yaml](../openspec/config.yaml) |

### 🏠 入口文档(仓库根目录)
[README](../README.md) · [快速入门](../快速入门.md) ·
[项目结构说明](../项目结构说明.md) ·
[inference_environment_summary](../inference_environment_summary.md)

### 🛠️ 工作流(`skill/`)
[stage-organization SKILL](../skill/stage-organization/SKILL.md):
对话式学习 → 阶段整理的循环规范(博客/目录/学习记录/检查清单的产出标准)。

---

## 🗂️ 视图二:按学习阶段

### 阶段 1 · 模型部署 ✅
计划:路线图 §阶段1 · 代码:`code/deployment/`(apps/monitoring/tests/archive)
技术文档:[使用指南](../code/deployment/docs/使用指南.md) ·
[项目总结](../code/deployment/docs/项目总结.md) ·
启动:`start.bat` · 博客:[01-模型部署篇](01-模型部署篇.md)

### 阶段 1.5 · 推理环境搭建 ✅
计划:路线图 §阶段1.5 · 代码:`code/environment_setup/`
技术文档:[技术总结](../code/environment_setup/docs/技术总结.md) ·
[问题记录](../code/environment_setup/docs/问题记录.md) ·
[学习记录](../code/environment_setup/学习记录.md) ·
[检查清单](../code/environment_setup/阶段完成检查清单.md) ·
博客:[02-环境搭建篇](02-AI推理优化环境搭建篇.md)

### 阶段 2 · 模型量化 ✅
计划:路线图 §阶段2 · 代码:`code/quantization/`(apps/experiments/benchmarks/scripts/logs)
技术文档:[量化基础概念](../code/quantization/docs/量化基础概念.md) ·
[技术总结](../code/quantization/docs/技术总结.md) ·
[问题记录](../code/quantization/docs/问题记录.md) ·
[学习记录](../code/quantization/学习记录.md) ·
[检查清单](../code/quantization/阶段完成检查清单.md) ·
实测日志:`code/quantization/logs/`(5 份基准报告) ·
博客:[03-模型量化篇](03-模型量化篇.md)

### 阶段 3 · 推理优化 🔜(进行中)
计划:[stage-3-推理优化.md](plans/stage-3-推理优化.md)(6 模块)
进度:PROGRESS §阶段3模块进度 · 代码:`code/optimization/`(待创建)
博客:04-推理优化篇(阶段完成时产出)

### 阶段 4 · 高级监控 / 阶段 5 · 生产部署 ⏳
计划:路线图 §阶段4/§阶段5(已含监控管道/能耗/回归 CI/PD 分离等补充)

---

## 📐 文档维护规则

1. **归属唯一**:计划只进 `docs/plans/`;进度只在 PROGRESS 更新;
   新博客按 `NN-主题篇.md` 命名放 `docs/` 根。
2. **索引同步**:新增文档须同步登记本页;阶段完成须更新 PROGRESS 与路线图状态。
3. **变更留痕**:文档体系结构或路线级变更走 openspec 流程。
4. **完整规范**:目录结构标准见
   [skill/stage-organization/references/directory-structure.md](../skill/stage-organization/references/directory-structure.md)。

---

*索引版本:2026-09-05 · 由 openspec change `docs-system-and-plan-supplement` 建立*
