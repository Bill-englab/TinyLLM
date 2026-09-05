# progress-dashboard 变更规格

## ADDED Requirements

### Requirement: 单文件离线可用

`docs/dashboard.html` MUST 为零依赖单文件(无 CDN/网络请求),
双击即可在浏览器打开并正常工作,进度数据 MUST 持久化在浏览器
localStorage,不依赖任何服务端。

#### Scenario: 离线打开

- **WHEN** 断网状态下双击打开 dashboard.html
- **THEN** 页面完整渲染,勾选操作即时生效
- **AND** 刷新/关闭后重开,勾选状态保留

### Requirement: 直观呈现知识体系与当前位置

页面 MUST 包含:课程总进度(讲数与百分比)、8 篇知识地图
(各篇完成态着色)、自动定位的"当前位置"卡片
(第一个未完成讲)及其建议动作。

#### Scenario: 当前位置自动更新

- **WHEN** 完成讲 1.1 的理论与实践勾选
- **THEN** "当前位置"自动前进到讲 1.2
- **AND** 总进度与第 1 篇进度同步更新

#### Scenario: 知识地图着色

- **WHEN** 某篇全部讲完成
- **THEN** 地图中该篇卡片显示完成态(绿色)
- **AND** 有进度的篇显示部分完成态

### Requirement: 逐讲勾选与详情

每讲 MUST 提供理论与实践两个勾选项(讲完成 = 两者皆勾),
点击讲标题 MUST 展开详情(理论要点/实践任务/产出物/面试自测题)。

#### Scenario: 勾选持久化

- **WHEN** 勾选讲 2.3 的"理论"后刷新页面
- **THEN** 该勾选状态保留
- **AND** 讲 2.3 在完成前不计入完成讲数

### Requirement: 进度快照导出

页面 MUST 提供导出功能,生成 Markdown 格式的进度快照
(日期/总进度/逐讲状态),可复制并粘贴到 `docs/progress/PROGRESS.md`
作为 git 留痕,衔接本地进度与仓库权威进度。

#### Scenario: 导出内容可用

- **WHEN** 点击"导出进度快照"
- **THEN** 得到含日期与完成度的 Markdown 文本
- **AND** 文本可直接粘贴进 PROGRESS.md 的更新日志
