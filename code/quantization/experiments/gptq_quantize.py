#!/usr/bin/env python3
"""
实验 2:GPTQ 4-bit 离线量化
===========================

跟实验 1 (bnb 动态量化) 的本质区别:
  - 动态量化:加载时按需转换,不产出新模型文件
  - GPTQ 静态量化:用校准数据离线计算每层最优 scale,产出可保存的 INT4 模型

本脚本:
  1. 加载 FP16 baseline
  2. 用内置校准文本(中英文 + 代码混合,无需联网)
  3. 用 transformers 内置 GPTQConfig 量化到 4-bit (group_size=128)
  4. 保存到 code/model/llama-3.2-1b-gptq-4bit/
  5. 记录量化耗时、显存、产出体积
  6. 对比量化前后在固定 prompt 上的输出

运行(WSL2,预计 10-20 分钟):
  conda activate inference_opt
  python /mnt/d/LLM_Project/code/quantization/experiments/gptq_quantize.py
"""

from __future__ import annotations

import os
import time
import shutil
from datetime import datetime
from pathlib import Path

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GPTQConfig,
)

# ----------------------------------------------------------------------
# 配置
# ----------------------------------------------------------------------

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "model"
    / "llama-3.2-1b-instruct"
    / "LLM-Research"
    / "Llama-3___2-1B-Instruct"
)
MODEL_PATH = os.environ.get("LLM_MODEL_PATH", str(DEFAULT_MODEL_PATH))

OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "model"
    / "llama-3.2-1b-gptq-4bit"
)

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 量化参数
BITS = 4
GROUP_SIZE = 128
DESC_ACT = False        # False:按顺序激活(True 精度更高但更慢,适合超低 bit)

# ----------------------------------------------------------------------
# 内置校准数据集(无需联网)
# ----------------------------------------------------------------------
# 设计原则:
#   - 128 条左右(GPTQ 推荐 128-512)
#   - 中英文 + 代码混合,贴近真实使用
#   - 每条 50-150 token,足够覆盖语言分布

CALIBRATION_TEXTS = [
    # 英文段落(覆盖通用知识、科学、技术)
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
    "The transformer architecture revolutionized natural language processing by introducing self-attention mechanisms.",
    "Quantization reduces the precision of neural network weights from floating point to lower bit representations.",
    "Graphics processing units are highly parallel processors originally designed for rendering computer graphics.",
    "Python is a high-level programming language known for its readability and versatile applications.",
    "Deep learning models require large amounts of data and computational resources to train effectively.",
    "The field of computer vision has been transformed by convolutional neural networks.",
    "Reinforcement learning agents learn by interacting with environments and receiving rewards.",
    "Natural language processing involves the interaction between computers and human language.",
    "Neural networks are composed of layers of interconnected nodes that process information.",
    "Gradient descent is an optimization algorithm used to minimize the loss function in machine learning.",
    "Attention mechanisms allow models to focus on relevant parts of the input sequence.",
    "Tokenization is the process of breaking text into smaller units called tokens.",
    "Fine-tuning adapts a pre-trained model to a specific task using domain-specific data.",
    "The development of large language models has accelerated progress in AI research.",
    "Cloud computing provides on-demand computing resources over the internet.",
    "Distributed training splits the workload across multiple devices or machines.",
    "Data preprocessing is a critical step in building effective machine learning pipelines.",
    "Model evaluation metrics help assess the performance of trained models on test data.",
    "Overfitting occurs when a model learns training data too well but fails to generalize.",
    # 中文段落(覆盖语言理解、知识、文化)
    "人工智能是计算机科学的一个重要分支,致力于让机器模拟人类的智能行为。",
    "深度学习使用多层神经网络从大量数据中自动学习特征表示。",
    "量化技术通过降低模型参数的精度来减少存储空间和计算开销。",
    "图形处理器最初是为渲染计算机图形而设计的高度并行处理器。",
    "Python 是一种高级编程语言,以其可读性和广泛的应用领域而闻名。",
    "Transformer 架构引入自注意力机制,彻底改变了自然语言处理领域。",
    "强化学习智能体通过与环境的交互和获得的奖励来学习决策策略。",
    "微调技术使预训练模型能够适应特定领域的任务需求。",
    "大语言模型的快速发展推动了人工智能研究的整体进步。",
    "梯度下降是一种用于最小化损失函数的优化算法。",
    "注意力机制让模型能够关注输入序列中的关键部分。",
    "分词是将文本切分成更小单元的过程,是语言处理的基础步骤。",
    "云计算通过互联网按需提供计算资源和服务。",
    "分布式训练将计算任务分配到多个设备或机器上以提高效率。",
    "数据预处理是构建机器学习系统的关键环节。",
    "模型评估指标帮助我们衡量训练模型在测试数据上的表现。",
    "过拟合发生在模型过度学习训练数据但无法泛化的情况下。",
    "卷积神经网络特别适合处理图像和视频等网格化数据。",
    "循环神经网络能够处理序列数据并保留时间依赖关系。",
    "迁移学习利用已学到的知识来解决相关但不同的问题。",
    # 代码片段(覆盖常见编程模式)
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "for i in range(10):\n    print(f'The square of {i} is {i**2}')",
    "class NeuralNetwork:\n    def __init__(self, layers):\n        self.layers = layers\n        self.weights = []",
    "import numpy as np\narray = np.random.randn(100, 100)\nmean = np.mean(array)",
    "with open('data.txt', 'r') as f:\n    content = f.read()\n    lines = content.split('\\n')",
    "async def fetch_data(url):\n    response = await client.get(url)\n    return response.json()",
    "try:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f'Error: {e}')",
    "SELECT name, age FROM users WHERE age > 18 ORDER BY name DESC;",
    "git commit -m 'Add new feature'\ngit push origin main",
    "docker build -t myapp .\ndocker run -p 8080:80 myapp",
    # 数学与逻辑
    "The Pythagorean theorem states that a^2 + b^2 = c^2 for right triangles.",
    "In probability theory, the expected value is the long-run average of random variables.",
    "Linear regression finds the best-fitting line through a set of data points.",
    "The chain rule in calculus allows differentiation of composite functions.",
    "Matrix multiplication is associative but not commutative in general.",
    # 日常对话
    "Hello, how can I help you today?",
    "What's the weather like in your city?",
    "Could you recommend a good book to read?",
    "I'm planning to travel to Japan next year.",
    "Thank you very much for your assistance.",
    "你今天过得怎么样?",
    "请帮我推荐一本好书。",
    "明天的天气会怎么样?",
    "我正在学习人工智能相关的知识。",
    "非常感谢你的帮助。",
] * 2  # 70 条 × 2 = 140 条,够用

# 测试 prompt(量化前后跑同一组,对比质量)
TEST_PROMPTS = [
    "用三句话解释什么是量化(quantization)。",
    "Write a Python function to compute fibonacci numbers.",
    "解释 GPTQ 量化的核心思想。",
]

# ----------------------------------------------------------------------
# GPU 监控(简化版,避免依赖)
# ----------------------------------------------------------------------

def gpu_mem_gb() -> float:
    try:
        import pynvml
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        used = pynvml.nvmlDeviceGetMemoryInfo(h).used / 1024**3
        pynvml.nvmlShutdown()
        return used
    except Exception:
        return -1.0


def dir_size_gb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total / 1024**3


# ----------------------------------------------------------------------
# 流程
# ----------------------------------------------------------------------

def generate_text(model, tokenizer, prompt: str, max_new_tokens: int = 100) -> str:
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    new_ids = out[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(new_ids, skip_special_tokens=True)


def main():
    print(f"⏰ 实验时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 源模型:{MODEL_PATH}")
    print(f"📦 量化输出:{OUTPUT_DIR}")
    print(f"⚙️  量化参数:bits={BITS}, group_size={GROUP_SIZE}, desc_act={DESC_ACT}")
    print(f"📚 校准样本数:{len(CALIBRATION_TEXTS)}")

    # 清理旧的输出目录
    if OUTPUT_DIR.exists():
        print(f"🧹 清理旧的量化模型目录")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 步骤 1:加载 tokenizer + FP16 baseline,跑一遍参考输出
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("① 加载 FP16 baseline,生成参考输出")
    print('=' * 60)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    t0 = time.time()
    fp16_model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    fp16_model.eval()
    print(f"✅ FP16 加载完成 耗时 {time.time()-t0:.1f}s,显存 {gpu_mem_gb():.2f} GB")

    print("\n生成 FP16 参考输出:")
    fp16_outputs = []
    for i, p in enumerate(TEST_PROMPTS, 1):
        out = generate_text(fp16_model, tokenizer, p)
        fp16_outputs.append(out)
        print(f"  [Prompt {i}] {p}")
        print(f"    → {out[:120]}{'...' if len(out) > 120 else ''}")

    # 释放 FP16 模型,腾出显存给量化
    del fp16_model
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    print(f"\n释放 FP16 模型,显存降至 {gpu_mem_gb():.2f} GB")

    # ------------------------------------------------------------------
    # 步骤 2:GPTQ 量化
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"② GPTQ 4-bit 离线量化(预计 10-20 分钟)")
    print('=' * 60)

    # GPTQConfig:transformers 内置,dataset 接受原始文本列表
    print(f"准备校准数据:{len(CALIBRATION_TEXTS)} 条原始文本")
    quantization_config = GPTQConfig(
        bits=BITS,
        group_size=GROUP_SIZE,
        desc_act=DESC_ACT,
        dataset=CALIBRATION_TEXTS,    # List[str] 原始文本,tokenizer 由 GPTQConfig 内部处理
    )

    t0 = time.time()
    print(f"\n开始量化(加载 + 量化同步进行)...")
    quantized_model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )
    quantize_time = time.time() - t0
    print(f"✅ 量化完成!耗时 {quantize_time/60:.2f} 分钟 ({quantize_time:.0f}s)")
    print(f"   量化时显存峰值:{gpu_mem_gb():.2f} GB")

    # ------------------------------------------------------------------
    # 步骤 3:保存量化模型
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"③ 保存量化模型到 {OUTPUT_DIR}")
    print('=' * 60)
    quantized_model.save_pretrained(OUTPUT_DIR, safe_serialization=True)
    tokenizer.save_pretrained(OUTPUT_DIR)
    out_size = dir_size_gb(OUTPUT_DIR)
    fp16_size = dir_size_gb(Path(MODEL_PATH))
    print(f"✅ 保存完成")
    print(f"   FP16 模型体积:{fp16_size:.2f} GB")
    print(f"   GPTQ 模型体积:{out_size:.2f} GB")
    print(f"   压缩比:{fp16_size / out_size:.2f}×")

    # ------------------------------------------------------------------
    # 步骤 4:跑量化后输出,跟 baseline 对比
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"④ 量化后输出对比")
    print('=' * 60)

    print(f"\n当前显存:{gpu_mem_gb():.2f} GB")
    print("\n生成 GPTQ 量化后输出:")
    gptq_outputs = []
    for i, p in enumerate(TEST_PROMPTS, 1):
        out = generate_text(quantized_model, tokenizer, p)
        gptq_outputs.append(out)
        print(f"\n  [Prompt {i}] {p}")
        print(f"    FP16 → {fp16_outputs[i-1][:120]}")
        print(f"    GPTQ → {out[:120]}")

    # ------------------------------------------------------------------
    # 步骤 5:写日志
    # ------------------------------------------------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"gptq_quantize_{ts}.md"
    lines = [
        "# GPTQ 4-bit 离线量化日志",
        "",
        f"- 时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 源模型:`{MODEL_PATH}`",
        f"- 输出模型:`{OUTPUT_DIR}`",
        f"- 参数:bits={BITS}, group_size={GROUP_SIZE}, desc_act={DESC_ACT}",
        f"- 校准样本数:{len(CALIBRATION_TEXTS)}",
        "",
        "## 关键指标",
        "",
        f"- 量化耗时:**{quantize_time/60:.2f} 分钟**",
        f"- FP16 模型体积:{fp16_size:.2f} GB",
        f"- GPTQ 模型体积:**{out_size:.2f} GB**",
        f"- 压缩比:**{fp16_size / out_size:.2f}×**",
        "",
        "## 输出对比",
        "",
    ]
    for i, p in enumerate(TEST_PROMPTS):
        lines.append(f"### Prompt {i+1}: {p}")
        lines.append(f"\n**FP16 baseline:**")
        lines.append(f"```\n{fp16_outputs[i]}\n```")
        lines.append(f"\n**GPTQ 4-bit:**")
        lines.append(f"```\n{gptq_outputs[i]}\n```\n")

    log_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n💾 日志已写入:{log_file}")

    # 清理
    del quantized_model
    gc.collect()
    torch.cuda.empty_cache()

    print(f"\n{'=' * 60}")
    print(f"✅ 实验 2 完成")
    print(f"{'=' * 60}")
    print(f"\n下一步:用 vLLM 加载这个 GPTQ 模型跑基准(实验 6)")
    print(f"模型位置:{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
