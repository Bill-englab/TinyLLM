# docs-system Specification

## Purpose
TBD - created by archiving change docs-system-and-plan-supplement. Update Purpose after archive.
## Requirements
### Requirement: 总索引覆盖全部文档

`docs/INDEX.md` MUST 作为文档体系唯一入口,按"内容类型"与"学习阶段"两种视图
索引仓库内全部计划、进度、博客、阶段技术文档与规格,且 MUST NOT 含失效链接。

#### Scenario: 按类型查找

- **WHEN** 读者想找"某个阶段的计划"
- **THEN** INDEX 的"按类型"视图列出该阶段计划文件的相对路径链接
- **AND** 点击链接可到达目标文件

#### Scenario: 按阶段查找

- **WHEN** 读者想了解"阶段 2 产出了哪些东西"
- **THEN** INDEX 的"按阶段"视图列出该阶段的计划/代码/文档/记录/检查清单/博客
- **AND** 每项均为有效链接

### Requirement: 四层文档各有唯一归属

文档 MUST 按四层归位,同类内容 MUST NOT 出现多个权威来源:
计划 → `docs/plans/`;进度 → `docs/progress/PROGRESS.md`;
说明 → `docs/*.md`(博客)与 `code/<stage>/docs/`;规格 → `openspec/`。

#### Scenario: 进度唯一权威源

- **WHEN** 查询项目当前学习进度
- **THEN** `docs/progress/PROGRESS.md` 为唯一权威来源
- **AND** README 中的进度表仅作摘要并链接到 PROGRESS

#### Scenario: 计划集中存放

- **WHEN** 查看任一学习阶段的规划
- **THEN** 总路线与阶段详细计划均位于 `docs/plans/` 目录
- **AND** 仓库其他位置不再存在重复的路线图副本

### Requirement: 文档体系变更走 openspec 流程

涉及文档体系结构或学习计划路线的变更 MUST 创建 openspec change 记录提案与任务,
完成后归档。

#### Scenario: 结构变更留痕

- **WHEN** 本次文档体系建立完成
- **THEN** openspec/changes/archive/ 下存在对应变更记录
- **AND** 变更的 tasks.md 显示全部任务完成

