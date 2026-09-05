# TinyLLM — AI 推理优化学习项目

> 在一块 RTX 3070 (8GB) 上,系统学习大模型推理优化的全流程:
> **部署 → 量化 → 推理优化 → 监控 → 生产部署**。
> 每个阶段都有真实实测数据、可运行的代码和一篇技术博客。

## 📈 关键实测数据

| 实验 | 结果 |
|------|------|
| vLLM vs Transformers(阶段 1.5) | **349.6 tok/s**,吞吐提升 **22×** |
| GPTQ 4-bit 量化(阶段 2) | 模型 **4.61 GB → 0.98 GB**(4.72× 压缩) |
| 量化精度代价 | 峰值显存节省 56%,PPL 仅上升 2.29%(3.197 → 3.271) |
| 下一目标(阶段 3) | 量化 + vLLM 组合,有效吞吐 **1000+ tok/s** |

## 🗺️ 学习路线

| 阶段 | 主题 | 状态 | 代码 | 博客 |
|------|------|------|------|------|
| 1 | 模型部署(Gradio + GPU 监控) | ✅ 完成 | [code/deployment](code/deployment/) | [01-模型部署篇](docs/01-模型部署篇.md) |
| 1.5 | 推理环境搭建(WSL2 + vLLM) | ✅ 完成 | [code/environment_setup](code/environment_setup/) | [02-环境搭建篇](docs/02-AI推理优化环境搭建篇.md) |
| 2 | 模型量化(bnb + GPTQ) | ✅ 完成 | [code/quantization](code/quantization/) | [03-模型量化篇](docs/03-模型量化篇.md) |
| 3 | 推理优化(6 模块:测量基础/KV cache/量化×引擎/引擎内部/kernel/投机采样) | 🔜 进行中 | — | — |
| 4 | 高级监控(指标采集 / 告警 / 仪表盘) | ⏳ 计划 | — | — |
| 5 | 生产部署(FastAPI / 容器化 / 负载均衡) | ⏳ 计划 | — | — |

完整规划见 [docs/plans/学习路线图.md](docs/plans/学习路线图.md),
阶段 3 执行计划见 [docs/plans/stage-3-推理优化.md](docs/plans/stage-3-推理优化.md),
当前进度见 [docs/progress/PROGRESS.md](docs/progress/PROGRESS.md)。

## 🚀 快速开始

```bash
# 1. 获取模型(约 4.7 GB,首次必做)
conda activate work
python code/deployment/download_model.py

# 2. 启动聊天应用(Windows)
cd code/deployment
start.bat
# 访问 http://127.0.0.1:7869(首次对话需等 1-2 分钟加载模型)
```

更多入口见 [快速入门.md](快速入门.md),仓库结构详见
[项目结构说明.md](项目结构说明.md)。

## 🛠️ 技术栈

- **模型**: LLaMA-3.2-1B-Instruct(FP16 基线 + 自制 GPTQ 4-bit 量化版)
- **硬件**: NVIDIA RTX 3070 (8GB) / Ryzen 5 3600 / WSL2
- **框架**: PyTorch 2.12 / transformers 5.12 / vLLM / gptqmodel / bitsandbytes / Gradio
- **环境**: 阶段 1 用 Windows(conda `work`),阶段 1.5 起用 WSL2(conda `inference_opt`)

各阶段依赖清单见对应目录的 `requirements.txt`,
环境详情见 [inference_environment_summary.md](inference_environment_summary.md)。

## 📁 仓库结构

```
TinyLLM/
├── code/                  # 学习代码(每阶段一个子目录)
│   ├── deployment/        #   阶段1:模型部署
│   ├── environment_setup/ #   阶段1.5:推理环境
│   ├── quantization/      #   阶段2:模型量化
│   └── model/             #   模型文件(不入库,获取方式见其 README)
├── docs/                  # 文档体系(总索引见 docs/INDEX.md)
│   ├── INDEX.md           #   总索引(按类型+按阶段)
│   ├── plans/             #   计划层(路线图+阶段计划)
│   ├── progress/          #   进度层(PROGRESS 看板)
│   └── 01~03-*.md         #   技术博客(每阶段一篇)
├── openspec/              # OpenSpec 变更管理(proposal → tasks → archive)
├── skill/                 # 阶段整理工作流(自定义 skill)
├── README.md / 快速入门.md / 项目结构说明.md
└── inference_environment_summary.md
```

📚 **全部文档从 [docs/INDEX.md](docs/INDEX.md) 出发索引**。

## 🔄 工作流

学习采用「对话式学习 → 阶段整理」循环(定义于 `skill/`):
阶段目标达成后,统一产出技术博客、学习记录、完成检查清单并整理目录。
仓库级变更走 [OpenSpec](openspec/) 流程:提案 → 规格 → 任务 → 实施归档。

---

**学习状态**: 阶段 2 完成,阶段 3(推理优化)进行中
**最后更新**: 2026-09-05
