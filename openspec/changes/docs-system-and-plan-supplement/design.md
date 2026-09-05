# Design: docs-system-and-plan-supplement

## Context

仓库现有 30+ 篇文档但没有导航体系:计划在 code/、进度三处重复、
技术文档藏在各阶段目录里。同时从 AI Infra 视角审查发现路线图的内容缺口
(测量基础、kernel 层、7B 对比、基准方法论等),需要在阶段 3 开工前补齐,
否则会按旧清单直接冲"开关式实验"。

## Goals / Non-Goals

**Goals:**
- 四层文档体系 + 总索引,任何文档 3 次点击内可达
- 进度唯一权威源(PROGRESS.md),消除三处维护漂移
- AI Infra 缺口落到阶段 3 的 6 模块详细计划与路线图补充
- 全部引用更新,无断链

**Non-Goals:**
- 不改动学习代码与既有博客内容
- 不为阶段 4/5 写详细计划(仅在路线图层面补条目,届时再展开)
- 不引入 docs 工具链(mkdocs/hugo 等)——纯 Markdown 索引即可

## Decisions

### Decision 1: 学习路线图迁至 docs/plans/(git mv)

计划是文档,应归计划层;code/ 只留代码与模型。用 `git mv` 保留历史。
影响引用:README、快速入门、项目结构说明、openspec/config.yaml、
skill 的 directory-structure.md(该规范同步更新,后续阶段沿用新约定)。

### Decision 2: 进度分三层,PROGRESS.md 为全局聚合

- 全局:`docs/progress/PROGRESS.md`(状态表 + 关键数据汇总 + 更新日志)
- 阶段:`code/<stage>/阶段完成检查清单.md`(既有,不动)
- 变更:`openspec/changes/*/tasks.md`(既有,不动)
README 只保留摘要表并链接 PROGRESS,避免再次出现"README 新、入门旧"的漂移。

### Decision 3: 阶段 3 重构为 6 模块,测量先行

3.0 测量与基础 → 3.1 KV cache → 3.2 量化×引擎(含 7B)→ 3.3 引擎内部 →
3.4 kernel 层 → 3.5 投机采样。理由:nsys/roofline/harness 是其余模块的
验证工具,不先建则所有结论仍靠推断;7B 实验放在 3.2 是因为它复用阶段 2
的量化脚本,是最便宜的高价值对比。概念性内容(TP/PP/PD 分离/引擎对比)
作为各模块的"概念学习"子条目,不单独设模块。

### Decision 4: 投机采样采用 1B draft + 3B GPTQ target 配对

单卡 8GB 无法容纳"1B target + 更小 draft"以外的大 target;
3B GPTQ(约 2GB)作 target、1B 作 draft 可行,顺带产出第二个量化模型资产。

### Decision 5: INDEX 双视图,不做分类页

单一 INDEX.md 内含"按类型"(计划/进度/博客/技术文档/规格)与
"按阶段"(每阶段全部产物)两张表,外加推荐阅读路径。
不拆多个索引页——文档量级(30+)单页足够,避免索引的索引。
