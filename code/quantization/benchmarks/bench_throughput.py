#!/usr/bin/env python3
"""
基准 1:吞吐量测试
==================

对比不同量化方案在不同 batch size 下的吞吐量。
关键指标:
  - throughput (tokens/s):总生成 tokens / 总耗时
  - latency (s/req):单个请求平均延迟
  - ttft (s):Time To First Token(首 token 延迟)

用法:
  python /mnt/d/LLM_Project/code/quantization/benchmarks/bench_throughput.py \
      --fp16 /path/to/fp16 \
      --gptq /path/to/gptq

至少指定一个模型路径。可同时指定多个,自动对比。
"""

from __future__ import annotations

import argparse
import gc
import time
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

PROMPTS_SHORT = [
    "Explain what machine learning is in two sentences.",
    "Translate 'hello world' to Chinese.",
    "What is the capital of France?",
    "Write a one-line greeting.",
] * 4  # 16 条,模拟小 batch

PROMPTS_LONG = [
    "Write a detailed essay about the impact of artificial intelligence on modern society.",
    "Explain how transformers work, including the attention mechanism and key innovations.",
    "Provide a comprehensive guide to Python decorators with examples.",
] * 4  # 12 条,长输出


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--fp16", type=str, help="FP16 模型路径")
    p.add_argument("--gptq", type=str, help="GPTQ 量化模型路径")
    p.add_argument("--bnb-int8", action="store_true", help="测试 bnb INT8(用 --fp16 路径加载)")
    p.add_argument("--bnb-nf4", action="store_true", help="测试 bnb NF4(用 --fp16 路径加载)")
    p.add_argument("--batch-sizes", type=int, nargs="+", default=[1, 4, 8])
    p.add_argument("--max-new-tokens", type=int, default=128)
    p.add_argument("--output", type=str, default=None, help="输出 markdown 报告路径")
    return p.parse_args()


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


def load_model(path: str, quant: str):
    """加载模型。quant 取值:fp16 / gptq / bnb-int8 / bnb-nf4"""
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if quant == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            path, dtype=torch.float16, device_map="auto", trust_remote_code=True
        )
    elif quant == "gptq":
        # 走 gptqmodel 直接 API,强制 Triton backend,绕开 Marlin JIT 编译
        # (Marlin 需要 nvcc 12.x+,WSL2 系统 nvcc 11.5 无法编译)
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
            path,
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
            device_map="auto",
            trust_remote_code=True,
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
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        raise ValueError(f"unknown quant: {quant}")
    model.eval()
    return model, tokenizer


def bench_batch(model, tokenizer, prompts: list[str], max_new_tokens: int) -> dict:
    """对一组 prompt 跑批处理,统计吞吐"""
    # tokenize,padding 对齐
    enc = tokenizer(
        [f"[User] {p}\n[Assistant]" for p in prompts],
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(model.device)

    # 测 TTFT:用第 1 个 prompt 单独跑 1 token
    single = {k: v[:1] for k, v in enc.items()}
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    t_ttft_start = time.time()
    with torch.no_grad():
        out_first = model.generate(
            **single,
            max_new_tokens=1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    ttft = time.time() - t_ttft_start

    # 跑完整 batch
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    dt = time.time() - t0

    # 数生成 tokens(每条 prompt 的)
    input_len = enc.input_ids.shape[1]
    total_new = 0
    for i in range(out.shape[0]):
        # 截到生成的部分(去除 padding 影响)
        gen = out[i][input_len:]
        # 去掉 eos 之后的 padding
        if tokenizer.eos_token_id in gen.tolist():
            eos_pos = gen.tolist().index(tokenizer.eos_token_id)
            gen = gen[:eos_pos + 1]
        total_new += len(gen)

    return {
        "batch_size": len(prompts),
        "total_new_tokens": total_new,
        "wall_time_s": dt,
        "throughput_tok_s": total_new / dt if dt > 0 else 0,
        "latency_per_req_s": dt / len(prompts),
        "ttft_s": ttft,
    }


def run_one(name: str, path: str, quant: str, batch_sizes: list[int], max_new: int):
    print(f"\n{'=' * 60}\n加载模型:{name} ({quant})\n{'=' * 60}")
    model, tokenizer = load_model(path, quant)
    print(f"  显存(加载后):{gpu_mem_gb():.2f} GB")

    results = []
    for bs in batch_sizes:
        prompts = PROMPTS_LONG[:bs] if bs <= len(PROMPTS_LONG) else PROMPTS_SHORT[:bs]
        if len(prompts) < bs:
            prompts = (prompts * (bs // len(prompts) + 1))[:bs]
        print(f"\n  Batch size = {bs} ({len(prompts)} prompts)...")
        r = bench_batch(model, tokenizer, prompts, max_new)
        print(f"    throughput: {r['throughput_tok_s']:.1f} tok/s, "
              f"latency: {r['latency_per_req_s']:.2f}s/req, "
              f"TTFT: {r['ttft_s']:.3f}s")
        results.append({"name": name, "quant": quant, **r})

    # 释放
    del model
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    return results


def main():
    args = parse_args()
    all_results = []

    if args.fp16:
        all_results += run_one("FP16", args.fp16, "fp16",
                                args.batch_sizes, args.max_new_tokens)
    if args.bnb_int8 and args.fp16:
        all_results += run_one("bnb-INT8", args.fp16, "bnb-int8",
                                args.batch_sizes, args.max_new_tokens)
    if args.bnb_nf4 and args.fp16:
        all_results += run_one("bnb-NF4", args.fp16, "bnb-nf4",
                                args.batch_sizes, args.max_new_tokens)
    if args.gptq:
        all_results += run_one("GPTQ-4bit", args.gptq, "gptq",
                                args.batch_sizes, args.max_new_tokens)

    if not all_results:
        print("没有指定任何模型,用 --fp16 / --gptq 至少一个")
        return

    # 打印汇总表
    print(f"\n{'=' * 80}")
    print("📊 吞吐量汇总")
    print("-" * 80)
    print(f"{'方案':<14}{'batch':<8}{'tok/s':<12}{'latency(s)':<14}{'TTFT(s)':<10}")
    print("-" * 80)
    for r in all_results:
        print(f"{r['name']:<14}{r['batch_size']:<8}"
              f"{r['throughput_tok_s']:<12.1f}"
              f"{r['latency_per_req_s']:<14.3f}"
              f"{r['ttft_s']:<10.3f}")
    print("=" * 80)

    # 写 markdown 报告
    out_path = args.output or (
        Path(__file__).resolve().parents[1] / "logs" /
        f"bench_throughput_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 吞吐量基准报告",
        f"",
        f"- 时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- max_new_tokens: {args.max_new_tokens}",
        f"",
        f"| 方案 | batch | tok/s | latency (s/req) | TTFT (s) |",
        f"|---|---|---|---|---|",
    ]
    for r in all_results:
        lines.append(
            f"| {r['name']} | {r['batch_size']} | "
            f"{r['throughput_tok_s']:.1f} | "
            f"{r['latency_per_req_s']:.3f} | "
            f"{r['ttft_s']:.3f} |"
        )
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\n💾 报告已写入:{out_path}")


if __name__ == "__main__":
    main()
