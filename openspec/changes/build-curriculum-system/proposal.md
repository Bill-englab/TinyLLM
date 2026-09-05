# Proposal: build-curriculum-system

## Why

现有路线图是"阶段×目录"的工程视角,缺少教学视角:没有循序渐进的章节序列、
没有每讲的理论/实践/自测结构、没有覆盖面试所需的完整知识体系
(训练侧、kernel 层、分布式此前都是空白或散点)。用户需要以学生身份
跟着固定节奏学习,并直观掌握知识脉络与个人进度。

## What Changes

- 新增 `docs/plans/课程大纲.md`:课程制总计划——8 篇 47 讲,
  每讲含理论要点/实践任务/产出物/面试自测题/时长/先修,
  覆盖 GPU 体系结构→推理引擎→量化→kernel→训练微调→生产服务化→分布式前沿,
  附篇↔代码目录↔旧阶段映射、毕业标准、面试高频题速查
- 新增 `docs/dashboard.html`:单文件离线网页进度台——
  总进度条、知识地图(8 篇卡片)、"当前位置"自动定位、
  逐讲理论/实践勾选(localStorage 持久化)、进度快照导出
- 重构 `docs/plans/学习路线图.md` 为映射文档(篇↔阶段↔代码目录),
  教学内容职责移交课程大纲
- PROGRESS/INDEX/README/openspec config 接入课程视角
- 吸收上轮硬件可行性评估结论:7B 用社区预量化模型、3B 全链路自量化、
  .wslconfig 内存解锁、vLLM 独立环境,写入大纲附录

## Capabilities

### New Capabilities
- `curriculum-system`: 课程大纲(结构完整性/覆盖度/理论与实践配对/面试导向)
- `progress-dashboard`: 网页进度台(离线单文件/逐讲勾选/当前位定位/快照导出)

### Modified Capabilities
- `learning-plan-v2`: 计划层主文档由路线图变更为课程大纲,路线图降为映射文档

## Impact

- 新增:`docs/plans/课程大纲.md`、`docs/dashboard.html`
- 修改:`docs/plans/学习路线图.md`(重构)、`docs/plans/stage-3-推理优化.md`(标注被课程大纲取代)、`docs/progress/PROGRESS.md`、`docs/INDEX.md`、`README.md`、`openspec/config.yaml`
- 不动:学习代码、博客、已归档变更

## 所属阶段

跨阶段教学基础设施变更。
完成定义:47 讲全部有理论/实践/产出/自测四要素、大纲覆盖面试六大主题域、
dashboard 可离线打开并持久化进度、全仓链接有效、openspec validate 通过。
