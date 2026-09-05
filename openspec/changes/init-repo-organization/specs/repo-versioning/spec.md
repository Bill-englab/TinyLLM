# repo-versioning 变更规格

## ADDED Requirements

### Requirement: 模型与缓存文件不入库

git 仓库 MUST NOT 包含模型权重和 Python 缓存等大文件/生成物,防止仓库膨胀。

#### Scenario: 克隆仓库后不含模型

- **WHEN** 执行 `git clone` 后查看 `code/model/` 目录
- **THEN** 目录下仅有 `README.md`
- **AND** README 说明了 FP16 基线模型(ModelScope 下载)与 GPTQ 模型(脚本重新量化)两种获取方式

#### Scenario: 缓存与本地配置被忽略

- **WHEN** 工作区存在 `__pycache__/`、`.claude/settings.local.json` 等生成物/本地配置
- **THEN** `git status` 不显示这些文件

### Requirement: 提交历史分阶段可追溯

仓库历史 MUST 能区分"整理前的原始状态"与"整理后的状态"。

#### Scenario: 基线与整理分离

- **WHEN** 查看 `git log`
- **THEN** 存在一个包含原始学习代码的基线提交
- **AND** 后续提交分别对应文档修复、依赖清单、OpenSpec 初始化等独立改动

### Requirement: 可推送到 GitHub 远程仓库

本地 main 分支 MUST 与 `git@github.com:Bill-englab/TinyLLM.git` 关联并可推送。

#### Scenario: 推送成功

- **WHEN** 执行 `git push -u origin main`
- **THEN** 推送成功且远程仓库内容与本地 main 一致
