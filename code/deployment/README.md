# 模型部署项目

## 📁 项目结构

### 主文件夹
```
LLM_Project/
├── code/              # 所有代码和模型
│   ├── deployment/   # 部署项目主文件夹（所有代码和文档）
│   └── model/        # 模型文件（LLaMA-3.2-1B）
└── .claude/          # Claude Code配置
```

### deployment文件夹
```
deployment/
├── apps/              # 应用程序
│   ├── stable_chat.py         # ✅ 稳定版多轮聊天应用（推荐使用）
│   ├── gradio_app.py          # 完整的Gradio应用
│   └── integrated_app.py      # 集成监控的应用
├── monitoring/        # 监控系统
│   ├── gpu_monitor.py         # GPU监控模块
│   ├── performance_monitor.py # 性能监控模块
│   └── dashboard.py           # 监控仪表盘
├── tests/             # 测试文件
│   ├── test_model.py          # 模型测试
│   └── fix_chinese_test.py    # 中文输出测试
├── archive/           # 归档文件（测试版本）
│   └── [7个测试版本文件]
├── docs/              # 文档
│   ├── 使用指南.md
│   ├── 项目总结.md
│   └── 文件整理说明.md
├── download_model.py  # 模型下载脚本
├── start_chat.bat     # Windows启动脚本
├── start_chat.sh      # Linux启动脚本
└── README.md          # 本文件
```

## 🚀 快速开始

### 1. 稳定版聊天应用（推荐）

```bash
# Windows用户
start_chat.bat

# 或命令行启动
python apps/stable_chat.py
```

**访问地址**: http://127.0.0.1:7869

**特点**:
- ✅ 支持多轮对话
- ✅ 修复了历史记录格式问题
- ✅ 稳定可靠，推荐使用

### 2. 完整Gradio应用

```bash
python apps/gradio_app.py
```

**访问地址**: http://127.0.0.1:7860

**特点**:
- 完整的Gradio界面
- 支持参数调节
- 适合学习Gradio使用

### 3. 集成监控应用

```bash
pythonapps/integrated_app.py
```

**访问地址**: http://127.0.0.1:7863

**特点**:
- 集成GPU监控
- 集成性能监控
- 适合学习监控技术

## 📊 监控系统

### 启动监控仪表盘

```bash
pythonmonitoring/dashboard.py
```

**访问地址**: http://127.0.0.1:7862

### 监控功能

- **GPU监控**: 实时GPU状态、温度、显存使用
- **性能监控**: 推理时间、Token速度、吞吐量
- **活动记录**: 最近推理历史

## 🧪 测试

### 模型测试

```bash
pythontests/test_model.py
```

### 中文输出测试

```bash
pythontests/fix_chinese_test.py
```

## 📦 模型信息

- **模型**: LLaMA-3.2-1B-Instruct
- **参数量**: 1.24B
- **存储路径**: `./model/llama-3.2-1b-instruct/`
- **数据类型**: FP16
- **设备**: GPU (RTX 3070)

## 🔧 环境要求

- Python 3.10+
- PyTorch 2.6.0+ with CUDA 12.6
- transformers
- gradio
- modelscope
- accelerate

## 📚 学习路径

1. **基础部署**: 使用 `stable_chat.py` 学习基础模型部署
2. **Gradio框架**: 使用 `gradio_app.py` 学习Web界面开发
3. **监控系统**: 使用 `integrated_app.py` 学习性能监控
4. **监控模块**: 学习 `monitoring/` 下的监控实现

## 🎯 学习成果

- ✅ **C环节**: 修复中文输出问题
- ✅ **A环节**: Gradio Web部署
- ✅ **B环节**: 实时监控系统
- ✅ **集成应用**: 完整的推理优化学习平台