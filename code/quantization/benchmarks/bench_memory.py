#!/usr/bin/env python3
"""
基准 2:显存占用测试
====================

对比不同量化方案的显存占用。
关键指标:
  - 模型加载后显存(steady state)
  - 推理时峰值显存(包含 KV cache 和激活)
  - 模型文件磁盘大小

用法:
  python /mnt/d/LLM_Project/code/quantization/benchmarks/bench_memory.py \
      --fp16 /path/to/fp16 \
      --gptq /path/to/gptq
"""

from __future__ import annotations

import argparse
import gc
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--fp16", type=str)
    p.add_argument("--gptq", type=str)
    p.add_argument("--bnb-int8", action="store_true")
    p.add_argument("--bnb-nf4", action="store_true")
    p.add_argument("--gen-len", type=int, default=128, help="推理时生成长度,用于测峰值")
    p.add_argument("--output", type=str, default=None)
    return p.parse_args()


def gpu_mem_info():
    """返回 (used_gb, total_gb)"""
    try:
        import pynvml
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(h)
        pynvml.nvmlShutdown()
        return info.used / 1024**3, info.total / 1024**3
    except Exception:
        return -1.0, -1.0


def dir_size_gb(path):
    p = Path(path)
    if not p.exists():
        return 0.0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1024**3


def load_model(path: str, quant: str):
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
            path,
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
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


def bench_one(name: str, path: str, quant: str, gen_len: int):
    print(f"\n{'=' * 60}\n{name} ({quant})\n{'=' * 60}")

    disk_size = dir_size_gb(path)
    print(f"  磁盘大小: {disk_size:.2f} GB")

    _, total = gpu_mem_info()
    print(f"  加载前显存: {_:.2f} / {total:.2f} GB")

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    model, tokenizer = load_model(path, quant)

    steady_used, _ = gpu_mem_info()
    print(f"  加载后显存(steady): {steady_used:.2f} GB")

    # 跑一次推理,记录峰值
    enc = tokenizer("Hello, tell me a story.", return_tensors="pt").to(model.device)
    with torch.no_grad():
        _ = model.generate(
            **enc, max_new_tokens=gen_len, do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 1024**3
    else:
        peak = -1.0
    after_gen, _ = gpu_mem_info()
    print(f"  推理后显存: {after_gen:.2f} GB")
    print(f"  PyTorch peak allocated: {peak:.2f} GB")

    del model
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    return {
        "name": name,
        "quant": quant,
        "disk_gb": disk_size,
        "steady_vram_gb": steady_used,
        "peak_vram_gb": peak,
    }


def main():
    args = parse_args()
    results = []

    if args.fp16:
        results.append(bench_one("FP16", args.fp16, "fp16", args.gen_len))
    if args.bnb_int8 and args.fp16:
        results.append(bench_one("bnb-INT8", args.fp16, "bnb-int8", args.gen_len))
    if args.bnb_nf4 and args.fp16:
        results.append(bench_one("bnb-NF4", args.fp16, "bnb-nf4", args.gen_len))
    if args.gptq:
        results.append(bench_one("GPTQ-4bit", args.gptq, "gptq", args.gen_len))

    if not results:
        print("没有指定模型")
        return

    # 汇总
    print(f"\n{'=' * 70}")
    print("📊 显存对比汇总")
    print("-" * 70)
    print(f"{'方案':<14}{'磁盘(GB)':<12}{'稳态显存(GB)':<16}{'峰值显存(GB)':<14}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<14}{r['disk_gb']:<12.2f}"
              f"{r['steady_vram_gb']:<16.2f}{r['peak_vram_gb']:<14.2f}")
    print("=" * 70)

    # 写报告
    out_path = args.output or (
        Path(__file__).resolve().parents[1] / "logs" /
        f"bench_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 显存对比报告",
        f"",
        f"- 时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 推理生成长度: {args.gen_len} tokens",
        f"",
        f"| 方案 | 磁盘 (GB) | 稳态显存 (GB) | 峰值显存 (GB) |",
        f"|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['disk_gb']:.2f} | "
            f"{r['steady_vram_gb']:.2f} | {r['peak_vram_gb']:.2f} |"
        )
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\n💾 报告已写入:{out_path}")


if __name__ == "__main__":
    main()
