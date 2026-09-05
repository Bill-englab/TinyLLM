# Proposal: init-repo-organization

## Why

项目已完成阶段 1/1.5/2 的学习(约 5000 行代码 + 39 篇文档),但存在三项工程债:
(1) 无版本控制,误删改无法回滚;(2) 依赖清单缺失,阶段 2 期间环境丢失重建过一次,
没有环境快照可参考;(3) 多份文档停留在旧状态(旧环境信息、旧阶段进度、旧脚本名),
与实际不符会误导后续阶段 3 的学习。此外项目即将公开到 GitHub(Bill-englab/TinyLLM),
需要一套规范的仓库结构与入口文档。

## What Changes

- 初始化 git 仓库,关联远程 `git@github.com:Bill-englab/TinyLLM.git`,main 分支
- 添加 `.gitignore`:排除模型文件(5.7 GB)、`__pycache__`、本地工具配置
- 新增 `code/model/README.md`:说明两个模型的来源与获取方式(下载/重新量化)
- 初始化 OpenSpec(`openspec/` 目录 + `.claude/` 工作流命令),并填写项目上下文
- 修正过时文档:
  - `inference_environment_summary.md`(2026-04 旧环境 → 2026-06 重建后环境)
  - `快速入门.md` / `项目结构说明.md`(停留在阶段 1,更新到阶段 2 完成状态)
- 重写 `README.md` 作为 TinyLLM 仓库主页(项目定位、结构导览、快速开始)
- 补充各阶段依赖清单(`requirements.txt`)

## Capabilities

### New Capabilities

- `repo-versioning`: 仓库版本控制规范(git + GitHub,模型文件排除策略)
- `repo-documentation`: 仓库文档体系(入口 README/快速入门/结构说明,与阶段进度同步)

### Modified Capabilities

无(本变更为仓库基础设施,不触碰任何阶段的学习代码)。

## Impact

- 新增:`.gitignore`、`code/model/README.md`、`openspec/**`、`.claude/commands|skills/**`、各阶段 `requirements.txt`
- 修改:`README.md`、`inference_environment_summary.md`、`快速入门.md`、`项目结构说明.md`
- 不动:`code/deployment|environment_setup|quantization/**` 全部学习代码与实验日志

## 所属阶段

不属于学习路线的任何阶段;是跨阶段的仓库基础设施变更(仓库整理)。
完成定义:git 历史可追溯(基线提交 + 整理提交)、所有文档与实际状态一致、
`openspec validate` 通过、可成功推送到 GitHub。
