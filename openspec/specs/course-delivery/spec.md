# course-delivery Specification

## Purpose
TBD - created by archiving change build-course-portal-p1. Update Purpose after archive.
## Requirements
### Requirement: 课件离线可读

课件站 MUST 以纯静态 HTML/CSS/JS 实现(相对路径引用,无 CDN/构建/服务端),
双击 `docs/course/index.html` 即可完整使用,断网可用。

#### Scenario: 双击学习

- **WHEN** 断网状态双击打开任一课件页
- **THEN** 页面样式与交互(自测揭晓/勾选)完整可用
- **AND** 通过页内导航可在门户与相邻讲次间跳转

### Requirement: 课件进度与进度台互通

课件页的"理论/实践"勾选 MUST 写入与 `docs/dashboard.html` 相同的
localStorage 键与数据结构,两边进度 MUST 双向一致。

#### Scenario: 课件勾选同步进度台

- **WHEN** 在课件页 p1-1 勾选"理论完成"后打开 dashboard.html
- **THEN** 总进度与讲 1.1 的理论状态同步更新
- **AND** 在 dashboard 勾选后回到课件页刷新,课件页按钮状态一致

### Requirement: 每讲课件具备教学结构

每讲课件页 MUST 包含:导语(为什么学/本讲地图)、分节理论讲解、
自测题(点击揭晓答案)、实践清单(可勾选的操作步骤)、产出物说明、
本讲完成勾选;理论讲解 MUST 含至少一个类比或图解。

#### Scenario: 自测可揭晓

- **WHEN** 阅读自测题后点击"显示答案"
- **THEN** 答案展开且含解释,不只给结论

#### Scenario: 实践可跟随

- **WHEN** 按实践清单操作
- **THEN** 每一步有明确指令(命令/文件路径),产出物路径与课程大纲一致

### Requirement: 滚动备课策略成文

课程大纲 MUST 记录学习循环协议(备课→自学→答疑→沉淀,粒度=篇)
与课件可用状态表;未制作课件的篇 MUST 在门户标注"待制作"而非死链。

#### Scenario: 门户无死链

- **WHEN** 打开课件门户
- **THEN** 仅第 0/1 篇课件可点入,其余篇显示"待制作(滚动备课)"状态
- **AND** 每篇卡片显示其讲次完成进度(读共享进度数据)

