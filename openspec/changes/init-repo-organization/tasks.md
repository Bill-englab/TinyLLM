# Tasks: init-repo-organization

## 1. 版本控制

- [x] 1.1 创建 `.gitignore`(模型/缓存/本地配置),新增 `code/model/README.md`
- [x] 1.2 `git init` + 配置本地身份 + 关联远程 `Bill-englab/TinyLLM`
- [x] 1.3 提交基线(原始学习代码快照)

## 2. OpenSpec 初始化

- [x] 2.1 `openspec init`,填写 `openspec/config.yaml` 项目上下文
- [x] 2.2 创建本 change 并完成 proposal/specs/design/tasks

## 3. 文档修复

- [x] 3.1 重写 `README.md`(TinyLLM 主页:定位/路线/数据/导览;修正不存在的 start_chat.bat 引用)
- [x] 3.2 修正 `inference_environment_summary.md`(更新为重建后环境)
- [x] 3.3 更新 `快速入门.md`(阶段进度、模型获取步骤、环境速查)
- [x] 3.4 更新 `项目结构说明.md`(补阶段 1.5/2/openspec/skill 目录与统计)

## 4. 依赖清单

- [x] 4.1 `code/deployment/requirements.txt`(Windows + modelscope 环境)
- [x] 4.2 `code/environment_setup/requirements.txt`(WSL2 + vLLM)
- [x] 4.3 `code/quantization/requirements.txt`(WSL2 + gptqmodel)

## 5. 验证与收尾

- [x] 5.1 `openspec validate init-repo-organization` 通过
- [x] 5.2 链接检查(README/快速入门/结构说明/环境总结引用的相对路径均存在)
- [ ] 5.3 分主题提交并推送 main 到 GitHub
- [ ] 5.4 归档本 change
