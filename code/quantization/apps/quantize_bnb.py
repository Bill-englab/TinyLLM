#!/usr/bin/env python3
"""
实验 1:bitsandbytes INT8 / NF4 动态量化对比
============================================

本脚本对比 LLaMA-3.2-1B 在三种精度下的表现:
  - FP16 (baseline)
  - INT8 (LLM.int8() 混合精度分解)
  - NF4 (4-bit NormalFloat,QLoRA 主流方案)

输出:
  - 每种方案的显存峰值
  - 每种方案的推理速度(tokens/s)
  - 同一组 prompt 的生成文本(人工对比质量)
  - 一张汇总表写入 logs/bnb_comparison_<timestamp>.md

运行方式(WSL2):
  conda activate inference_opt
  python /mnt/d/LLM_Project/code/quantization/apps/quantize_bnb.py
"""

from __future__ import annotations

import gc
import time
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# ----------------------------------------------------------------------
# 配置
# ----------------------------------------------------------------------

# 模型路径:允许通过环境变量覆盖,默认指向项目内本地模型
DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "model"
    / "llama-3.2-1b-instruct"
    / "LLM-Research"
    / "Llama-3___2-1B-Instruct"
)
import os
MODEL_PATH = os.environ.get("LLM_MODEL_PATH", str(DEFAULT_MODEL_PATH))

# 日志目录
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 测试 prompt(混合中英文,能体现量化的语义保持能力)
TEST_PROMPTS = [
    "用三句话解释什么是量化(quantization)。",
    "Write a Python function to compute fibonacci numbers.",
    "巴黎是哪个国家的首都?它有什么著名景点?",
    "Translate 'Artificial intelligence is transforming the world.' into Chinese.",
]

# 生成参数
GEN_KWARGS = dict(
    max_new_tokens=128,
    do_sample=False,        # 关闭采样,保证三种方案输出可比
    temperature=1.0,
    top_p=1.0,
    pad_token_id=None,      # 后面设置
)


# ----------------------------------------------------------------------
# GPU 监控工具
# ----------------------------------------------------------------------

def get_gpu_memory() -> tuple[float, float]:
    """返回 (已用 GB, 总 GB)"""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        pynvml.nvmlShutdown()
        return info.used / 1024**3, info.total / 1024**3
    except Exception as e:
        print(f"  ⚠️  GPU 监控不可用:{e}")
        return -1.0, -1.0


def torch_peak_reset() -> float:
    """返回 PyTorch 已记录的峰值显存(GB),然后清零"""
    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 1024**3
        torch.cuda.reset_peak_memory_stats()
        return peak
    return -1.0


def release_model(model) -> None:
    """彻底释放模型,避免下一次加载时显存堆积"""
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


# ----------------------------------------------------------------------
# 三种量化配置
# ----------------------------------------------------------------------

def build_bnb_int8_config() -> BitsAndBytesConfig:
    """LLM.int8():outlier 通道保持 FP16,其余 INT8"""
    return BitsAndBytesConfig(load_in_8bit=True)


def build_bnb_nf4_config() -> BitsAndBytesConfig:
    """NF4 4-bit:信息论最优的正态分布量化 + 双重量化"""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,    # 把 scale 本身也量化,再省 ~0.4 bits/param
    )


# ----------------------------------------------------------------------
# 实验
# ----------------------------------------------------------------------

def load_model(name: str, quant_config: BitsAndBytesConfig | None):
    """加载模型 + tokenizer,返回 (model, tokenizer, load_time)"""
    print(f"\n{'=' * 60}")
    print(f"📦 加载模型:{name}")
    print(f"   路径:{MODEL_PATH}")

    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"模型路径不存在:{MODEL_PATH}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    GEN_KWARGS["pad_token_id"] = tokenizer.pad_token_id

    load_start = time.time()
    kwargs = dict(
        trust_remote_code=True,
        device_map="auto",
    )
    if quant_config is not None:
        kwargs["quantization_config"] = quant_config
    else:
        kwargs["torch_dtype"] = torch.float16

    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, **kwargs)
    model.eval()
    load_time = time.time() - load_start

    used, total = get_gpu_memory()
    print(f"✅ 加载完成 耗时 {load_time:.2f}s")
    print(f"   显存:{used:.2f} / {total:.2f} GB")
    return model, tokenizer, load_time


def run_inference(model, tokenizer, prompts: list[str]) -> dict:
    """对每个 prompt 生成,统计 tokens/s 和输出"""
    outputs = []
    total_new_tokens = 0
    total_time = 0.0

    for i, prompt in enumerate(prompts, 1):
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        torch.cuda.reset_peak_memory_stats() if torch.cuda.is_available() else None
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(**inputs, **GEN_KWARGS)
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        dt = time.time() - t0

        new_ids = out[0][inputs.input_ids.shape[1]:]
        new_text = tokenizer.decode(new_ids, skip_special_tokens=True)
        n_new = len(new_ids)

        total_new_tokens += n_new
        total_time += dt
        outputs.append({"prompt": prompt, "response": new_text, "tokens": n_new, "time": dt})

        print(f"  [{i}/{len(prompts)}] {n_new} tokens / {dt:.2f}s "
              f"= {n_new / dt:.1f} tok/s")

    return {
        "outputs": outputs,
        "total_tokens": total_new_tokens,
        "total_time": total_time,
        "tokens_per_second": total_new_tokens / total_time if total_time > 0 else 0,
    }


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------

def main():
    print(f"⏰ 实验时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 模型:{MODEL_PATH}")
    print(f"📝 测试 prompt 数:{len(TEST_PROMPTS)}")

    used_before, total = get_gpu_memory()
    print(f"🎮 实验前显存:{used_before:.2f} / {total:.2f} GB")

    plans = [
        ("FP16 (baseline)", None),
        ("INT8 (bnb LLM.int8)", build_bnb_int8_config()),
        ("NF4 (bnb 4-bit)", build_bnb_nf4_config()),
    ]

    results = []
    for name, cfg in plans:
        try:
            model, tokenizer, load_time = load_model(name, cfg)
            used_after_load, _ = get_gpu_memory()
            inf = run_inference(model, tokenizer, TEST_PROMPTS)
            peak = torch_peak_reset()
            results.append({
                "name": name,
                "load_time_s": load_time,
                "vram_used_gb": used_after_load,
                "vram_peak_gb": peak,
                "tokens_per_second": inf["tokens_per_second"],
                "outputs": inf["outputs"],
            })
            release_model(model)
        except Exception as e:
            print(f"❌ {name} 失败:{e}")
            import traceback
            traceback.print_exc()
            results.append({"name": name, "error": str(e)})
            release_model(None)

    print_summary(results)
    write_log(results)


def print_summary(results: list[dict]):
    print("\n" + "=" * 60)
    print("📊 汇总对比")
    print("-" * 60)
    print(f"{'方案':<28}{'显存(GB)':<12}{'速度(tok/s)':<14}{'加载(s)':<10}")
    print("-" * 60)
    for r in results:
        if "error" in r:
            print(f"{r['name']:<28}{'FAIL':<12}")
            continue
        print(f"{r['name']:<28}"
              f"{r['vram_used_gb']:<12.2f}"
              f"{r['tokens_per_second']:<14.1f}"
              f"{r['load_time_s']:<10.2f}")
    print("=" * 60)

    # 同一 prompt 的输出对比(取第一条)
    print("\n🔍 质量对比(prompt #1):")
    print(f"原文:{TEST_PROMPTS[0]}")
    for r in results:
        if "error" in r:
            continue
        print(f"\n  [{r['name']}]")
        resp = r["outputs"][0]["response"]
        print("  " + resp.replace("\n", "\n  "))


def write_log(results: list[dict]):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"bnb_comparison_{ts}.md"
    lines = [
        f"# bitsandbytes 量化对比日志",
        f"",
        f"- 时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 模型:`{MODEL_PATH}`",
        f"",
        f"## 性能汇总",
        f"",
        f"| 方案 | 显存(GB) | 速度(tok/s) | 加载时间(s) |",
        f"|---|---|---|---|",
    ]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | FAIL | - | - |")
            continue
        lines.append(
            f"| {r['name']} | {r['vram_used_gb']:.2f} | "
            f"{r['tokens_per_second']:.1f} | {r['load_time_s']:.2f} |"
        )

    lines.append("\n## 生成质量对比\n")
    for i, prompt in enumerate(TEST_PROMPTS):
        lines.append(f"### Prompt {i + 1}: {prompt}\n")
        for r in results:
            if "error" in r:
                continue
            lines.append(f"**[{r['name']}]**")
            lines.append("```")
            lines.append(r["outputs"][i]["response"])
            lines.append("```\n")

    log_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n💾 日志已写入:{log_file}")


if __name__ == "__main__":
    main()
