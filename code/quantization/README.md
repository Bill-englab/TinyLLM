# 阶段 2:模型量化

> AI 推理优化学习项目的第二阶段。在阶段 1.5(vLLM 22× 加速)的基础上,继续通过**量化**压缩模型体积、降低显存、提升吞吐。

## 阶段目标

1. 理解 INT8 / INT4 量化的数学原理与工程差异(对称/非对称、per-channel、动态 vs 静态)
2. 在 LLaMA-3.2-1B 上跑通 4 种主流量化方法
3. 产出**显存 / 速度 / 精度**三维对比数据
4. 验证量化模型在 vLLM 中的端到端可用性

## 量化方法路线

| # | 方法 | 工具 | 类型 | 难度 |
|---|---|---|---|---|
| 1 | bitsandbytes INT8 (`LLM.int8()`) | `bitsandbytes` 0.49.2 | 加载时动态 | ★ |
| 2 | bitsandbytes NF4 (4-bit) | `bitsandbytes` | 加载时动态 | ★ |
| 3 | GPTQ 4-bit | `auto-gptq` 0.7.1 | 离线静态 | ★★★ |
| 4 | AWQ 4-bit | `autoawq`(待装) | 离线静态 | ★★★ |

> **核心理解点**:动态量化(1、2)只是"加载时按需量化",不产出新模型文件;静态量化(3、4)需要校准数据集,**产出可保存、可分发的量化模型**。

## 目录结构

```
code/quantization/
├── apps/                  # 完整可运行应用
│   ├── quantize_bnb.py            # bitsandbytes INT8/NF4 加载对比
│   └── serve_quantized_vllm.py    # 用 vLLM 跑量化模型
├── experiments/           # 量化算法实验
│   ├── exp1_dynamic_vs_static.md # 动态 vs 静态量化对比说明
│   ├── gptq_quantize.py           # GPTQ 离线量化脚本
│   └── awq_quantize.py            # AWQ 离线量化脚本
├── benchmarks/            # 性能/显存/质量基准
│   ├── bench_throughput.py
│   ├── bench_memory.py
│   └── bench_quality.py
├── scripts/
│   └── run_all_benchmarks.sh
├── docs/                  # 阶段内文档
│   ├── 量化基础概念.md
│   ├── 使用指南.md
│   ├── 技术总结.md
│   ├── 代码说明.md
│   └── 问题记录.md
├── archive/               # 归档
├── 学习记录.md
└── 阶段完成检查清单.md
```

根目录新增技术博客:`docs/03-模型量化篇.md`

## 环境依赖

阶段 1.5 已经装好的可直接使用:
- `bitsandbytes==0.49.2`
- `auto-gptq==0.7.1`
- `optimum==2.1.0`
- `transformers==4.57.6`
- `accelerate==1.13.0`

AWQ 需要额外安装(可选):
```bash
pip install autoawq
```

## 硬件基线(来自阶段 1.5)

- 模型:LLaMA-3.2-1B-Instruct
- GPU:RTX 3070 (8GB)
- FP16 + vLLM baseline:**349.6 tokens/s**,显存 2.32 GB
- FP16 + Transformers baseline:**15.8 tokens/s**

本阶段所有量化结果将与上述 baseline 对齐对比。

## 快速开始

```bash
# 1. 进入 WSL2,激活环境
conda activate inference_opt

# 2. 第一个实验:bitsandbytes INT8/NF4 对比
python /mnt/d/LLM_Project/code/quantization/apps/quantize_bnb.py

# 3. 离线量化 GPTQ 模型(耗时 15-30 分钟)
python /mnt/d/LLM_Project/code/quantization/experiments/gptq_quantize.py

# 4. 跑基准测试
bash /mnt/d/LLM_Project/code/quantization/scripts/run_all_benchmarks.sh
```

## 进度

- [ ] 1. 目录骨架 + 概念文档
- [ ] 2. bitsandbytes INT8/NF4 实验
- [ ] 3. GPTQ 离线量化
- [ ] 4. AWQ 量化(可选)
- [ ] 5. Benchmarks 三件套
- [ ] 6. vLLM 加载量化模型
- [ ] 7. 文档体系 + 技术博客 03
- [ ] 8. 学习记录 + 检查清单

---

**阶段开始日期**:2026-06-17
**预期总时长**:约 10 小时
**前序阶段**:[阶段 1.5 推理优化环境搭建](../environment_setup/)
