# Proposal: build-course-portal-p1

## Why

课程制(8 篇 47 讲)已有大纲与进度台,但学生问"如何开展学习"——目前只有目录
和勾选,没有可读的教学内容。用户的学习循环是:备课(材料)→ 自学(理论+实践)
→ 答疑(对话)→ 沉淀(博客),需要一个 MOOC 式课件站承载前两个环节。

## What Changes

- 新增课件站 `docs/course/`:
  - `index.html` 门户:8 篇卡片 + 逐讲入口 + 课件可用状态(滚动备课)
  - `style.css`/`course.js` 共享教材样式与进度逻辑,**与 dashboard.html
    共享同一 localStorage 键**——课件页勾选即同步总进度台
  - `p0.html` 第0篇复习课件(链接既有博客 + 复习自测)
  - `p1-1.html` ~ `p1-7.html` 第1篇全部 7 讲完整课件:导语/分节理论/
    类比-重点-坑标注/可运行代码/ASCII 图解/自测题点击揭晓/实践清单/
    本讲完成勾选(理论·实践,与 dashboard 同步)
- 学习循环协议写入课程大纲(备课→自学→答疑→沉淀,粒度=篇,滚动备课)
- INDEX/README/dashboard/PROGRESS/config 接入课件层
- 滚动备课策略:本次产出第 0/1 篇;第 2 篇起待前一篇学习反馈后制作

## Capabilities

### New Capabilities
- `course-delivery`: 课件站(离线单页群/进度同步/教学结构/滚动备课)

## Impact

- 新增:`docs/course/{index.html,style.css,course.js,p0.html,p1-1..7.html}`
- 修改:`docs/plans/课程大纲.md`(学习循环协议节)、`docs/INDEX.md`、`README.md`、
  `docs/dashboard.html`(页脚课件入口)、`docs/progress/PROGRESS.md`、`openspec/config.yaml`
- 不动:学习代码、博客、既有课件无关文档

## 所属阶段

教学基础设施 + 第 0/1 篇内容产出。
完成定义:课件双击可读、勾选与 dashboard 互通、7 讲四要素齐、
全仓链接有效、openspec validate 通过。
