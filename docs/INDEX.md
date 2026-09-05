# 📚 TinyLLM 文档总索引(INDEX)

> 本页是仓库文档体系的唯一入口。所有计划、进度、说明、规格从这里出发,
> 3 次点击内可达任意文档。
> 文档归置规则与各层职责见 [项目结构说明.md](../项目结构说明.md)。

## 🗺️ 快速路径

| 你想… | 去这里 |
|-------|--------|
| **开始学习(学生入口)** | **[课件中心](course/index.html)** 逐讲学习(第 0/1 篇已备) |
| **跟着课程系统学习** | **[dashboard.html](dashboard.html) 进度台**(逐讲勾选)→ [课程大纲](plans/课程大纲.md) |
| 了解这个项目是什么 | [README](../README.md) → [学习路线图](plans/学习路线图.md) |
| 看当前进度 | [PROGRESS 进度看板](progress/PROGRESS.md) |
| 跑起来某个应用 | [快速入门](../快速入门.md) |
| 按顺序读博客 | [01](01-模型部署篇.md) → [02](02-AI推理优化环境搭建篇.md) → [03](03-模型量化篇.md) |
| 开始第 1 篇学习 | 课程大纲 §第1篇(先读附录 A 硬件约束备忘) |
| 提出一个变更 | `openspec/`(用法见 [openspec/config.yaml](../openspec/config.yaml) 与 `.claude/commands/opsx/`) |

---

## 🗂️ 视图一:按内容类型

### 📋 计划层(`docs/plans/`)
| 文档 | 说明 |
|------|------|
| [课程大纲](plans/课程大纲.md) | **教学主文档**:8 篇 47 讲,每讲理论/实践/产出/面试自测 |
| [学习路线图](plans/学习路线图.md) | 工程映射:篇↔阶段↔代码目录 + AI Infra 审查史 |
| [stage-3-推理优化](plans/stage-3-推理优化.md) | (历史)已收编入课程大纲第 1-4 篇 |

### 🖥️ 进度台(`docs/dashboard.html`)
单文件离线网页:总进度/知识地图/当前位置/逐讲理论·实践勾选(localStorage)/
快照导出。双击即用,与课程大纲同源。

### 📖 课件层(`docs/course/`)
| 内容 | 说明 |
|------|------|
| [课件中心](course/index.html) | 门户:8 篇入口、课件可用状态(滚动备课) |
| `course/p0.html` | 第 0 篇课件(复习指引+自测) |
| `course/p1-1.html` ~ `p1-7.html` | 第 1 篇全部 7 讲完整课件(理论/图解/代码/自测揭晓/实践清单) |

课件与进度台共享本地进度,勾选双向同步;第 2 篇起滚动制作。

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
