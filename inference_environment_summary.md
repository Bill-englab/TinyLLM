# 推理优化环境配置总结

> ⚠️ 历史说明:2026-04 阶段 1.5 搭建的初版环境在 2026-06 丢失,阶段 2 期间重建。
> 本文记录的是 **2026-06 重建后的当前环境**(阶段 2 实测所用)。
> 初版环境快照见 `code/environment_setup/requirements.txt`。

## 🎯 环境信息

### 硬件配置
- **CPU**: AMD Ryzen 5 3600 (6核12线程)
- **内存**: 7.7GB(WSL2 可用)
- **GPU**: NVIDIA GeForce RTX 3070 (8GB显存)
- **系统**: WSL2 (Ubuntu)

### 软件环境(当前,2026-06 重建)
- **Python**: 3.10.4 (conda环境: `inference_opt`,位于 ext4 分区)
- **PyTorch**: 2.12.0(PyPI wheel,自带 CUDA 13.0 runtime)
- **transformers**: 5.12.1(大版本跳跃,API 跟 4.x 有显著差异)
- **系统 nvcc**: 11.5(较老,无法 JIT 编译 Marlin kernel,详见下文限制)

### 初版环境(2026-04,已丢失,仅存档)
- PyTorch 2.10.0 + CUDA 11.8 / transformers 4.57.6 / vLLM 0.19.0 / auto-gptq 0.7.1

## ✅ 当前已安装的核心工具

### 量化与推理(阶段 2)
- **PyTorch** (2.12.0): 深度学习框架
- **transformers** (5.12.1): 模型库,GPTQConfig 内置于此
- **gptqmodel** (7.1.0): GPTQ 量化主包(auto-gptq 的继任者,后者已废弃)
- **bitsandbytes** (0.49.2): 动态量化(INT8/NF4)
- **optimum** (2.2.0): transformers ↔ gptqmodel 桥接
- **accelerate** (1.14.0): device_map 支持
- **triton** (3.7.0): GPU kernel,GPTQ 的推理 backend

### 监控工具
- **nvidia-ml-py3** (7.352.0): pynvml,GPU 显存监控
- **prometheus-client** (0.25.0): 指标导出
- **tensorboard** (2.20.0): 可视化工具

### 待安装(阶段 3 计划)
- **vLLM**: 初版环境曾装 0.19.0(实测 349.6 tok/s),重建后未装;
  阶段 3 用它加载 GPTQ 模型时需重装

## 🚀 快速启动命令

### 激活环境

```bash
conda activate inference_opt
```

### 环境自检

```bash
python code/quantization/scripts/check_env.py
```

### 用本项目模型跑 vLLM(阶段 3 计划)

```bash
# FP16 基线
python -m vllm.entrypoints.openai.api_server \
    --model /mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct \
    --port 8000

# 阶段 2 产出的 GPTQ 量化模型
python -m vllm.entrypoints.openai.api_server \
    --model /mnt/d/LLM_Project/code/model/llama-3.2-1b-gptq-4bit \
    --quantization gptq \
    --port 8000
```

### GPU 监控

```bash
# 实时监控
watch -n 1 nvidia-smi

# Python 脚本监控
python -c "
import pynvml
pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'显存使用: {info.used / 1024**3:.2f}/{info.total / 1024**3:.2f} GB')
pynvml.nvmlShutdown()
"
```

## 📊 环境能力评估

### ✅ 完全支持的功能
1. **量化实验**: bnb 动态量化 + GPTQ 离线量化均已跑通(阶段 2 完成)
2. **Transformers 推理**: FP16 与 GPTQ 模型均可加载推理
3. **GPU 监控**: nvidia-smi 与 pynvml 均正常

### ⚠️ 已知限制(踩坑记录,详见 code/quantization/docs/问题记录.md)
1. **内存限制**: 7.7GB RAM,大型模型加载时可能紧张
2. **显存限制**: 8GB 显存,7B+ 模型必须量化
3. **nvcc 11.5 过老**: 无法 JIT 编译 GPTQ Marlin kernel(需 C++17 新特性),
   当前强制使用 Triton backend,推理慢 30-50%;升级 CUDA toolkit 可解锁
4. **conda 环境不要放 NTFS**: 大小写敏感问题会导致包损坏,已在 ext4 分区重建
   (envs_dirs 指向 ext4)

## 📝 常用配置参数

### vLLM 重要参数
- `--tensor-parallel-size`: 张量并行度 (1=单GPU)
- `--gpu-memory-utilization`: GPU显存使用率 (0.9=90%)
- `--max-model-len`: 最大模型长度
- `--quantization`: 量化方法 (gptq, awq 等)
- `--dtype`: 数据类型 (half, float32, bfloat16)

### 性能优化建议
- 使用 `--dtype half` 节省显存
- 设置 `--gpu-memory-utilization 0.9` 充分利用显存
- 对于 7B 模型,使用 4-bit 或 8-bit 量化
- pip 慢时使用清华镜像:`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <pkg>`

## 🎓 学习资源

### vLLM 官方资源
- GitHub: https://github.com/vllm-project/vllm
- 文档: https://docs.vllm.ai/

### 本项目相关文档
- 环境搭建过程: [docs/02-AI推理优化环境搭建篇.md](docs/02-AI推理优化环境搭建篇.md)
- 阶段 2 量化问题记录: [code/quantization/docs/问题记录.md](code/quantization/docs/问题记录.md)
- 各阶段依赖清单: `code/<阶段>/requirements.txt`

---

**最后更新**: 2026-09-05(阶段 2 完成后同步)
