# 阶段 3 详细计划:推理优化(6 模块)

> ⚠️ **本文档已收编**(2026-09-05):模块设计全部并入
> [课程大纲.md](./课程大纲.md) 第 1-4 篇(3.0→第1篇,3.1/3.3→第2篇,
> 3.2→第2/3篇,3.4→第4篇,3.5→第2.6+第5.5)。
> 新的学习请以课程大纲为准;本文件保留作历史参考,
> 其"风险与备选"表已升级为课程大纲附录 A(硬件约束备忘)。

> 总路线见 [学习路线图.md](./学习路线图.md);本文件是阶段 3 的执行级计划。
> 制定日期:2026-09-05,基于 AI Infra 缺口审查(详见路线图文末)。
> 执行环境:WSL2 + conda `inference_opt`,RTX 3070 (8GB)。

## 设计原则

1. **测量先行**:模块 3.0 产出的统一基准 harness 与 profiling 方法,
   是所有后续模块的验证工具。没有可信测量,优化只是开关游戏。
2. **每个结论都要有"为什么"**:阶段 2 得出"推理是 memory-bound"靠的是端到端
   数据推断;本阶段要用 roofline、显存公式、kernel 时间线把它变成推导。
3. **概念与实验分离**:受单卡限制做不了的(TP/PP/PD 分离),以源码精读
   +论文笔记的方式学习,明确标注"概念学习",不假装做了实验。

## 模块依赖与顺序

```
3.0 测量与基础 ──┬──> 3.1 KV Cache ──┐
                ├──> 3.2 量化×引擎 ──┼──> 3.5 投机采样(依赖 3.2 的 3B GPTQ)
                └──> 3.4 Kernel 层   │
3.3 引擎内部(可与 3.1/3.2 并行,笔记驱动) <─┘
```

建议节奏:3.0 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5;3.3 的源码精读可穿插进行。

---

## 模块 3.0:测量与基础(新增,地基)

**目录**: `code/optimization/fundamentals/` + `code/optimization/benchmarks/`

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.0.1 | GPU 体系结构:SM/warp/内存层级(寄存器→shared→L2→HBM)/Tensor Core 概念 | `docs/gpu-体系结构笔记.md`(含 3070 规格表:448 GB/s 带宽、20.3 TFLOPS FP16) |
| 3.0.2 | HBM 带宽实测:torch 大张量拷贝测得有效带宽 | 实测脚本 + 日志 |
| 3.0.3 | Roofline 模型:计算 LLaMA-1B decode 的 arithmetic intensity,推导"为什么 memory-bound" | 推导笔记 + 图 |
| 3.0.4 | nsys 入门:profile Transformers 推理,读 kernel 时间线,定位时间大头 | profiling 报告 + 解读笔记 |
| 3.0.5 | **统一基准 harness**:重构为全阶段共用,支持 P50/P99、N 次重复+方差、warmup 隔离、prompt 长度分布、到达过程(open/closed loop) | `benchmarks/bench.py` + 使用文档 |

### 验收标准
- [ ] 实测带宽与标称值差距有解释(通常 70-80% 有效率)
- [ ] roofline 推导能定量解释阶段 2 的"量化不提速"现象
- [ ] harness 跑出的报告含 P50/P99/方差,且能复现阶段 1.5 的 349.6 tok/s(±10%)
- [ ] nsys 截图/导出 + "时间花在哪"的一页结论

### 关键问题(本模块要回答)
- decode 每 token 需要读多少字节?与 448 GB/s 相除理论 tok/s 是多少?与实测差多少?
- batch 增大时为什么吞吐先线性后饱和?

---

## 模块 3.1:KV Cache 深入(新增)

**目录**: `code/optimization/kv_cache/`

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.1.1 | KV cache 显存公式推导:`2 × layers × kv_heads × head_dim × dtype × seq_len`,代入 LLaMA-3.2-1B 参数 | 推导笔记 |
| 3.1.2 | 公式实测验证:不同 seq_len/batch 下显存增量与公式对齐 | 验证脚本 + 对比表 |
| 3.1.3 | vLLM block 管理观测:block_size、实际分配块数、preemption 现象 | 观测笔记 |
| 3.1.4 | KV cache INT8 量化(vLLM `--kv-cache-dtype int8`):吞吐/显存/质量三维对比(用 3.0 harness) | 基准日志 |
| 3.1.5 | Prefix caching 实验:共享 system prompt 场景的 TTFT 变化 | 实验日志 |

### 验收标准
- [ ] 公式预测与实测误差 <5%
- [ ] 能回答"8GB 显存下 LLaMA-1B 最长能服务多少并发/上下文"
- [ ] KV INT8 的三维数据齐备,并给出"是否值得开"的结论

---

## 模块 3.2:量化 × 引擎组合(强化原计划)

**目录**: `code/optimization/quantized_serving/`

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.2.1 | vLLM 加载 GPTQ 4-bit:跑通并三维基准(对齐阶段 2 的 transformers-GPTQ 数据) | 基准日志 |
| 3.2.2 | **7B GPTQ 对比实验**:量化 Qwen2.5-7B 或 Llama-3.1-8B 至 GPTQ 4-bit(~4GB,8GB 可跑),对比 1B/7B 的"量化提速比" | 7B 量化模型 + 对比报告 |
| 3.2.3 | llama.cpp 横向对比(可选):同一模型 GGUF vs vLLM-GPTQ | 对比笔记 |

### 验收标准
- [ ] vLLM+GPTQ vs Transformers+GPTQ 的加速比有数据
- [ ] 7B 上验证/反转"量化不提速"结论:预期 7B decode 更偏 memory-bound,
      4-bit 应能看到实际提速(权重读量降 4×)
- [ ] 产出第二个可复用量化模型资产

### 关键问题
- 模型多大时,4-bit 权重读量下降才开始"买得到"吞吐?

---

## 模块 3.3:引擎内部——vLLM 源码精读(具体化原"深入")

**目录**: `code/optimization/engine_internals/`(以笔记为主)

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.3.1 | 论文精读:Efficient Memory Management for LLM Serving with PagedAttention(vLLM 论文) | 精读笔记 |
| 3.3.2 | vLLM 源码走读:`vllm/core/scheduler.py`(调度循环)、`block_manager`(块分配) | 带注释的走读笔记 + 调用流程图 |
| 3.3.3 | Continuous batching 图解:对比 static batching 的调度时序 | 图解笔记 |
| 3.3.4 | 概念学习:chunked prefill、PD 分离(论文/博客笔记,不做实验) | 概念笔记 |
| 3.3.5 | 概念学习:Tensor/Pipeline 并行与 NCCL 通信原理(单卡限制,只读源码文档) | 概念笔记 |

### 验收标准
- [ ] 能徒手画出 vLLM 一次 generate 的调用链(API → scheduler → worker)
- [ ] 能说清 PagedAttention 解决了什么、代价是什么(块表间接寻址)
- [ ] 5 篇笔记入库,每篇含"对照本仓库实验数据"一节

---

## 模块 3.4:Kernel 层(新增)

**目录**: `code/optimization/kernels/`

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.4.1 | Triton 入门:vector add → fused softmax,理解 block 编程模型 | 可运行 kernel + 性能对比(对比 torch 原生) |
| 3.4.2 | FlashAttention 论文精读:online softmax / tiling / IO-aware 思想 | 精读笔记 |
| 3.4.3 | FlashAttention 原理复现(简化版):naive attention → tiled attention 的显存与速度对比 | 简化实现 + 对比数据 |
| 3.4.4 | torch.compile 实验:mode 差异(inductor)、对 1B decode 的影响 | 基准日志 |
| 3.4.5 | CUDA Graphs 实验:图捕获消除 kernel 启动开销,测小 batch 延迟收益 | 基准日志 |

### 验收标准
- [ ] Triton fused softmax 性能 ≥ torch 原生(或差距有解释)
- [ ] 复现版 tiled attention 显存 O(N) 特性有数据(对比 naive 的 O(N²))
- [ ] 能回答"torch.compile/CUDA Graphs 在什么场景下收益最大"(kernel 启动开销占比)

---

## 模块 3.5:投机采样(强化原计划)

**目录**: `code/optimization/speculative/`

> 配对决策:1B 作 draft + **3B GPTQ 作 target**(8GB 可容纳)。
> 若 3B 量化模型在 3.2 未产出,则先用 vLLM 内置的 draft-target 组合。

### 学习内容
| # | 条目 | 产出物 |
|---|------|--------|
| 3.5.1 | 论文精读:Fast Inference from Transformers via Speculative Decoding | 精读笔记 |
| 3.5.2 | vLLM speculative decoding 实测:1B draft + 3B target,acceptance rate / 实际加速比 | 基准日志 |
| 3.5.3 | 负载分析:什么输出分布下投机采样收益高/为负 | 分析笔记 |

### 验收标准
- [ ] acceptance rate 与加速比数据齐备
- [ ] 能定量回答"accept rate 低于多少时投机采样反而变慢"

---

## 阶段 3 整体验收(检查清单草案)

- [ ] 6 模块各有产出物入库,logs/ 有对应基准日志
- [ ] 统一 harness 成为全阶段唯一基准工具,旧三件套标注 deprecated
- [ ] LLaMA-3.2-1B 有效吞吐 ≥1000 tok/s(vLLM+GPTQ+并发),或给出未达标的原因分析
- [ ] 7B GPTQ 服务可运行且有完整三维数据
- [ ] 论文精读笔记 ≥3 篇(vLLM/FlashAttention/投机采样)
- [ ] 技术博客 `docs/04-推理优化篇.md` + 学习记录 + 检查清单(按 stage-organization 流程)
- [ ] 本阶段以 openspec change(阶段3各模块)跟踪执行

## 风险与备选

| 风险 | 备选方案 |
|------|----------|
| nvcc 11.5 无法编译某些 kernel 依赖 | 用 Triton 路线;升级 CUDA toolkit 作为独立练习 |
| 7.7GB 系统内存加载 7B 量化紧张 | 选 3B 模型做规模对比(Qwen2.5-3B);或纯 vLLM 流式加载 |
| nsys 在 WSL2 不可用/权限问题 | 改用 torch profiler + kineto 导出,概念相通 |
| 3B GPTQ 量化复现阶段 2 流程失败 | 降级用社区现成 GPTQ 模型,量化本身不是本模块重点 |

---

**计划版本**: v2.0(2026-09-05,经 AI Infra 审查补充)
**前置**: 阶段 2 完成(GPTQ 模型与基准脚本可直接复用)
**预计投入**: 每模块 4-8 小时,总计 30-45 小时
