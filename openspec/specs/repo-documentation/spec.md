# repo-documentation Specification

## Purpose
TBD - created by archiving change init-repo-organization. Update Purpose after archive.
## Requirements
### Requirement: 文档与实际状态一致

入口文档描述的进度、环境、脚本名 MUST 与仓库实际内容一致,MUST NOT 引用不存在的文件。

#### Scenario: 环境信息为重建后版本

- **WHEN** 阅读 `inference_environment_summary.md`
- **THEN** 记录的是 2026-06 重建后的环境(PyTorch 2.12 / transformers 5.12.1 / gptqmodel 7.1.0)
- **AND** 如引用旧环境差异(如 transformers 4.x),明确标注为历史信息

#### Scenario: 快速入门引用的脚本真实存在

- **WHEN** 按 `快速入门.md` 的启动指引操作
- **THEN** 文中提到的脚本文件名(如 `start_chat.bat`)在仓库中真实存在且路径正确

#### Scenario: 进度状态为阶段 2 完成

- **WHEN** 阅读任一入口文档(README/快速入门/结构说明)
- **THEN** 学习进度均表述为"阶段 1/1.5/2 完成,阶段 3 待开始"

### Requirement: README 作为仓库主页提供完整导览

`README.md` MUST 让新访客在 1 分钟内理解项目定位、当前进度与目录结构。

#### Scenario: 新访客导览

- **WHEN** 首次打开仓库主页
- **THEN** 能看到项目定位(TinyLLM 推理优化学习)、五阶段路线及完成状态、关键实测数据
- **AND** 有指向学习路线图、博客、各阶段代码的链接(均有效)

### Requirement: 每个阶段目录有依赖清单

每个已完成学习阶段的目录 MUST 包含 `requirements.txt`,记录该阶段的 Python 依赖。

#### Scenario: 依赖清单存在且可读

- **WHEN** 查看 `code/deployment/`、`code/environment_setup/`、`code/quantization/`
- **THEN** 每个目录下存在 `requirements.txt`,含依赖名与版本号
- **AND** 文件头注释说明对应的环境(Windows/WSL2,conda 环境名)

