# Design: init-repo-organization

## Context

仓库此前无版本控制。学习代码按 stage-organization skill 的目录规范组织
(`code/<阶段>/{apps,experiments,benchmarks,scripts,docs,logs}`),
但入口文档(README、快速入门、结构说明)写于 2026-04,落后于实际进度约两个阶段;
根目录的 `inference_environment_summary.md` 记录的是已被重建替换的旧 conda 环境。

## Goals / Non-Goals

**Goals:**
- git + GitHub 版本控制就绪,模型文件排除策略明确且可复现
- OpenSpec 规范落地:后续阶段 3 的学习变更走 propose → apply → archive 流程
- 所有入口文档与实际状态一致,README 可作为公开仓库主页
- 每阶段补齐 requirements.txt

**Non-Goals:**
- 不改动任何学习代码(包括 `stable_chat.py` 的相对路径问题,留给阶段 3 顺带处理)
- 不重写技术博客(docs/01-03),只修事实性错误
- 不拆分/移动既有阶段目录,保持现有结构

## Decisions

### Decision 1: 先提交基线,再做整理

先以"原始状态 + .gitignore"提交基线(3b34398),再分主题提交整理改动。
理由:保留整理前的真实快照,文档修复的前后差异在 git diff 中可审计。

### Decision 2: 模型目录用"白名单"式 gitignore

用 `code/model/*` + `!code/model/README.md`,而非直接忽略整个目录。
理由:git 无法追踪空目录,`code/model/` 的存在性和获取方式需要随仓库分发。

### Decision 3: 依赖清单按阶段分文件,不做全仓统一环境

三个阶段环境差异大(阶段 1 为 Windows + modelscope,阶段 1.5/2 为 WSL2 + vLLM/gptqmodel),
统一 requirements 会失真。按阶段各写一份,头部注释标明运行环境。

### Decision 4: OpenSpec 用 spec-driven schema,项目上下文写入 config.yaml

`openspec/config.yaml` 的 context 字段承载项目定位、阶段路线、目录约定,
供后续所有变更的 artifact 生成引用;`.claude/` 下的 opsx 命令随仓库分发。
