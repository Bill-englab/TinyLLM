#!/usr/bin/env python3
"""
基准 3:质量评估
================

对比不同量化方案的输出质量。两种评估方式:
  1. **困惑度 PPL**(客观指标):在固定测试文本上计算
  2. **输出对比**(主观指标):固定一组难 prompt,看输出是否合理

用法:
  python /mnt/d/LLM_Project/code/quantization/benchmarks/bench_quality.py \
      --fp16 /path/to/fp16 \
      --gptq /path/to/gptq
"""

from __future__ import annotations

import argparse
import gc
import math
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


# 困惑度测试文本(多语言、多主题)
PPL_TEXTS = [
    # 英文 - 知识
    "The transformer architecture has revolutionized natural language processing "
    "by introducing the self-attention mechanism, which allows the model to weigh "
    "the importance of different words in a sequence when making predictions.",
    # 英文 - 代码
    "def quicksort(arr):\n"
    "    if len(arr) <= 1:\n"
    "        return arr\n"
    "    pivot = arr[len(arr) // 2]\n"
    "    left = [x for x in arr if x < pivot]\n"
    "    middle = [x for x in arr if x == pivot]\n"
    "    right = [x for x in arr if x > pivot]\n"
    "    return quicksort(left) + middle + quicksort(right)",
    # 中文
    "深度学习是机器学习的一个分支,它使用多层神经网络来从大量数据中自动学习"
    "特征表示。这种方法在图像识别、自然语言处理和语音识别等领域取得了显著的成果。",
    # 数学
    "The Pythagorean theorem states that in a right-angled triangle, "
    "the square of the hypotenuse equals the sum of squares of the other two sides. "
    "If a and b are the legs and c is the hypotenuse, then a^2 + b^2 = c^2.",
]

# 难 prompt(放大量化精度差异)
HARD_PROMPTS = [
    # 1. 数学推理
    "Calculate: 17 * 23 = ?",
    # 2. 代码生成
    "Write a Python function binary_search(arr, target) that returns the index or -1.",
    # 3. 多步推理
    "If A > B and B > C, what is the relationship between A and C?",
    # 4. 长文创作
    "Write a 5-sentence short story about a robot learning to paint.",
    # 5. 知识问答
    "What are the three laws of thermodynamics?",
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--fp16", type=str)
    p.add_argument("--gptq", type=str)
    p.add_argument("--bnb-int8", action="store_true")
    p.add_argument("--bnb-nf4", action="store_true")
    p.add_argument("--max-new-tokens", type=int, default=200)
    p.add_argument("--output", type=str, default=None)
    return p.parse_args()


def load_model(path, quant):
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if quant == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            path, dtype=torch.float16, device_map="auto", trust_remote_code=True
        )
    elif quant == "gptq":
        try:
            from gptqmodel import GPTQModel, BACKEND
            model = GPTQModel.from_quantized(
                path, backend=BACKEND.GPTQ_TRITON,
            )
        except ImportError:
            model = AutoModelForCausalLM.from_pretrained(
                path, device_map="auto", trust_remote_code=True
            )
    elif quant == "bnb-int8":
        model = AutoModelForCausalLM.from_pretrained(
            path, quantization_config=BitsAndBytesConfig(load_in_8bit=True),
            device_map="auto", trust_remote_code=True,
        )
    elif quant == "bnb-nf4":
        model = AutoModelForCausalLM.from_pretrained(
            path,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            ),
            device_map="auto", trust_remote_code=True,
        )
    else:
        raise ValueError(quant)
    model.eval()
    return model, tokenizer


@torch.no_grad()
def compute_ppl(model, tokenizer, texts: list[str]) -> float:
    """计算平均困惑度。PPL = exp(avg NLL)"""
    total_nll = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(text, return_tensors="pt").to(model.device)
        # 让模型预测下一个 token,跟实际比较
        # input_ids 长度 N,labels 也用 input_ids,但 shift
        input_ids = enc.input_ids
        if input_ids.shape[1] < 2:
            continue
        # 限制长度,避免显存炸
        if input_ids.shape[1] > 512:
            input_ids = input_ids[:, :512]
        outputs = model(input_ids=input_ids, labels=input_ids)
        # loss 已经按 token 平均了,所以需要乘 token 数
        n_tokens = input_ids.shape[1] - 1   # 第一个 token 不算
        total_nll += outputs.loss.item() * n_tokens
        total_tokens += n_tokens
    if total_tokens == 0:
        return float("inf")
    return math.exp(total_nll / total_tokens)


def generate_for_prompts(model, tokenizer, prompts, max_new):
    outputs = []
    for p in prompts:
        messages = [{"role": "user", "content": p}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        enc = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **enc, max_new_tokens=max_new, do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        new_ids = out[0][enc.input_ids.shape[1]:]
        outputs.append(tokenizer.decode(new_ids, skip_special_tokens=True))
    return outputs


def bench_one(name: str, path: str, quant: str, max_new: int):
    print(f"\n{'=' * 60}\n{name} ({quant})\n{'=' * 60}")
    model, tokenizer = load_model(path, quant)

    print("  计算困惑度...")
    ppl = compute_ppl(model, tokenizer, PPL_TEXTS)
    print(f"  PPL = {ppl:.3f}")

    print("  生成测试 prompt...")
    gen = generate_for_prompts(model, tokenizer, HARD_PROMPTS, max_new)

    del model
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    return {"name": name, "quant": quant, "ppl": ppl, "gen": gen}


def main():
    args = parse_args()
    results = []

    if args.fp16:
        results.append(bench_one("FP16", args.fp16, "fp16", args.max_new_tokens))
    if args.bnb_int8 and args.fp16:
        results.append(bench_one("bnb-INT8", args.fp16, "bnb-int8", args.max_new_tokens))
    if args.bnb_nf4 and args.fp16:
        results.append(bench_one("bnb-NF4", args.fp16, "bnb-nf4", args.max_new_tokens))
    if args.gptq:
        results.append(bench_one("GPTQ-4bit", args.gptq, "gptq", args.max_new_tokens))

    if not results:
        print("没有指定模型")
        return

    # PPL 汇总
    print(f"\n{'=' * 60}")
    print("📊 困惑度对比(越低越好)")
    print("-" * 60)
    fp16_ppl = next((r["ppl"] for r in results if r["quant"] == "fp16"), None)
    for r in results:
        if fp16_ppl:
            delta = (r["ppl"] - fp16_ppl) / fp16_ppl * 100
            print(f"  {r['name']:<14} PPL = {r['ppl']:.3f}  "
                  f"(vs FP16: {'+' if delta >= 0 else ''}{delta:.2f}%)")
        else:
            print(f"  {r['name']:<14} PPL = {r['ppl']:.3f}")
    print("=" * 60)

    # 写报告
    out_path = args.output or (
        Path(__file__).resolve().parents[1] / "logs" /
        f"bench_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 质量评估报告",
        f"",
        f"- 时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## 困惑度 PPL(越低越好)",
        f"",
        f"| 方案 | PPL | 相对 FP16 |",
        f"|---|---|---|",
    ]
    for r in results:
        if fp16_ppl and r["quant"] != "fp16":
            delta = (r["ppl"] - fp16_ppl) / fp16_ppl * 100
            lines.append(f"| {r['name']} | {r['ppl']:.3f} | {'+' if delta >= 0 else ''}{delta:.2f}% |")
        else:
            lines.append(f"| {r['name']} | {r['ppl']:.3f} | baseline |")

    lines.append("\n## 输出对比\n")
    for i, p in enumerate(HARD_PROMPTS):
        lines.append(f"### Prompt {i + 1}: {p}\n")
        for r in results:
            lines.append(f"**[{r['name']}]**")
            lines.append("```")
            lines.append(r["gen"][i])
            lines.append("```\n")

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\n💾 报告已写入:{out_path}")


if __name__ == "__main__":
    main()
