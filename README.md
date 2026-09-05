# AI推理优化学习项目

## 🎯 项目概述

这是一个系统学习AI推理优化的项目，涵盖模型部署、量化、监控、优化和生产部署等全流程技术。

## 📁 当前项目结构

```
LLM_Project/
├── code/              # 所有代码和模型
│   ├── deployment/   # ✅ 阶段1：模型部署（已完成）
│   ├── model/        # 模型文件（LLaMA-3.2-1B）
│   └── 学习路线图.md  # 完整学习规划
└── .claude/          # Claude Code配置
```

### code文件夹结构

```
code/
├── deployment/        # 部署项目主文件夹
│   ├── apps/         # 应用程序
│   │   ├── stable_chat.py        # ✅ 稳定版聊天（推荐）
│   │   ├── gradio_app.py         # 完整Gradio应用
│   │   └── integrated_app.py     # 集成监控应用
│   ├── monitoring/    # 监控系统
│   │   ├── gpu_monitor.py        # GPU监控模块
│   │   ├── performance_monitor.py# 性能监控模块
│   │   └── dashboard.py          # 监控仪表盘
│   ├── tests/        # 测试文件
│   │   ├── test_model.py         # 模型测试
│   │   └── fix_chinese_test.py   # 中文测试
│   ├── archive/      # 归档文件（测试版本）
│   ├── docs/         # 文档
│   │   ├── 使用指南.md
│   │   ├── 项目总结.md
│   │   └── 文件整理说明.md
│   ├── download_model.py  # 模型下载脚本
│   ├── start_chat.bat     # Windows启动脚本
│   ├── start_chat.sh      # Linux启动脚本
│   └── README.md           # 部署项目说明
└── model/            # 模型文件
    └── llama-3.2-1b-instruct/
```

## 🚀 快速开始

### 启动聊天应用

**Windows用户**:
```bash
cd code\deployment
start_chat.bat
```

**Linux用户**:
```bash
cd code/deployment
./start_chat.sh
```

**命令行启动**:
```bash
python code\deployment\apps\stable_chat.py
```

**访问地址**: http://127.0.0.1:7869

### 第一次使用

1. 访问 http://127.0.0.1:7869
2. 输入第一条消息，按回车发送
3. **等待1-2分钟**（第一次会加载模型）
4. 之后可以进行连续的多轮对话

## 📚 详细文档

### 项目文档
- **code/学习路线图.md** - 完整的学习规划（推荐先看）
- **code/deployment/README.md** - 部署项目详细说明
- **code/deployment/docs/使用指南.md** - 使用方法和故障排除
- **code/deployment/docs/项目总结.md** - 学习成果总结

## 🎯 学习路线

### ✅ 阶段 1:模型部署
- ✅ 模型加载和推理
- ✅ Gradio Web部署
- ✅ 基础监控系统
- ✅ 中文输出修复
- ✅ 多轮对话实现

### ✅ 阶段 1.5:AI推理优化环境搭建
- ✅ WSL2 + conda + vLLM 工具链
- ✅ LLaMA-3.2-1B 推到 **349.6 tok/s**(vLLM),相比 Transformers 提升 **22×**
- ✅ PagedAttention / Continuous Batching 实测
- 技术博客:[02-AI推理优化环境搭建篇](docs/02-AI推理优化环境搭建篇.md)

### ✅ 阶段 2:模型量化
- ✅ bnb INT8/NF4 动态量化
- ✅ GPTQ 4-bit 离线量化(**4.72× 模型压缩**)
- ✅ 三维基准(吞吐量/显存/困惑度)
- ✅ 9 个脚本 + 7 篇文档 + 1 个可复用的 GPTQ 量化模型(0.98 GB)
- 技术博客:[03-模型量化篇](docs/03-模型量化篇.md)

### 🔜 阶段 3:推理优化(即将开始)
- 📈 vLLM 加载 GPTQ 量化模型
- 📈 FlashAttention
- 📈 Continuous Batching / PagedAttention 深入
- 📈 Speculative Decoding

### 后续计划
- 📊 高级监控系统
- 🚀 生产级部署

**详细规划**: 查看 [code/学习路线图.md](code/学习路线图.md)

## 🎯 当前学习成果

本项目第一阶段已完成：

- ✅ **C环节**: 修复中文输出问题
- ✅ **A环节**: Gradio Web部署
- ✅ **B环节**: 实时监控系统
- ✅ **集成应用**: 完整的推理优化学习平台

## 📊 技术信息

- **模型**: LLaMA-3.2-1B-Instruct (1.24B参数)
- **硬件**: NVIDIA RTX 3070 (8GB)
- **框架**: PyTorch 2.6.0 + CUDA 12.6
- **部署**: Gradio 6.11.0

## 💡 提示

- 第一次对话会加载模型，请耐心等待
- 支持多轮对话，保持上下文
- 界面简洁，操作简单
- 模型存储在 `code/model/` 目录下

---

**项目整理日期**: 2026-04-08
**最后更新**: 2026-06-18
**学习状态**: 阶段 2 完成,准备开始阶段 3(推理优化)