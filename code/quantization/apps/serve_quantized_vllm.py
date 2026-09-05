#!/usr/bin/env python3
"""
实验 6:加载 GPTQ 量化模型,提供推理服务
=============================================

两种运行模式:
  - **chat**(默认):命令行交互,跟量化模型对话
  - **bench**:加载并跑一组测试 prompt,记录性能

可选 API 模式(--mode api):启动 OpenAI 兼容的 HTTP 服务。
  - 需要 `pip install fastapi uvicorn`,跟 vLLM 同样的接口
  - 真正的 vLLM 服务见本文件末尾"附录"部分

用法示例:
  # 命令行聊天
  python serve_quantized_vllm.py chat \\
      --model /mnt/d/LLM_Project/code/model/llama-3.2-1b-gptq-4bit

  # 性能测试
  python serve_quantized_vllm.py bench \\
      --model /mnt/d/LLM_Project/code/model/llama-3.2-1b-gptq-4bit

  # 启动 HTTP API(可选,需要 fastapi)
  python serve_quantized_vllm.py api \\
      --model /mnt/d/LLM_Project/code/model/llama-3.2-1b-gptq-4bit \\
      --port 8000

附录:用 vLLM 跑 GPTQ 模型(替代本脚本,获得 5-10x 吞吐):
  # 1. 装包(实验 6 真正的"vLLM 路线")
  #    pip install vllm
  #
  # 2. 启动服务
  #    python -m vllm.entrypoints.openai.api_server \\
  #        --model /path/to/llama-3.2-1b-gptq-4bit \\
  #        --quantization gptq \\
  #        --port 8000
  #
  # 3. 测试
  #    curl http://localhost:8000/v1/chat/completions \\
  #      -H "Content-Type: application/json" \\
  #      -d '{"model":"...","messages":[{"role":"user","content":"Hello"}]}'
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_MODEL = (
    Path(__file__).resolve().parents[2]
    / "model"
    / "llama-3.2-1b-gptq-4bit"
)


def parse_args():
    p = argparse.ArgumentParser(
        description="加载 GPTQ 量化模型做推理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("mode", choices=["chat", "bench", "api"], default="chat",
                   nargs="?", help="运行模式")
    p.add_argument("--model", type=str, default=str(DEFAULT_MODEL),
                   help="量化模型路径")
    p.add_argument("--max-new-tokens", type=int, default=256)
    p.add_argument("--port", type=int, default=8000, help="API 模式端口")
    return p.parse_args()


def load_quantized(model_path: str):
    """加载 GPTQ 量化模型(transformers 自动从 config 识别)"""
    print(f"📦 加载模型:{model_path}")
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"模型不存在:{model_path}\n"
            f"请先跑 experiments/gptq_quantize.py 产出 GPTQ 模型"
        )

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # GPTQ 模型:走 gptqmodel 直接 API,强制 Triton backend
    # (transformers 默认选 MarlinLinear,WSL2 上 nvcc 11.5 编译失败)
    t0 = time.time()
    try:
        from gptqmodel import GPTQModel, BACKEND
        model = GPTQModel.from_quantized(
            model_path, backend=BACKEND.GPTQ_TRITON,
        )
    except (ImportError, Exception) as e:
        # fallback:尝试 transformers 默认加载(适用于 Marlin 已编译或非 GPTQ 模型)
        print(f"  gptqmodel 加载失败({e}),尝试 transformers 默认路径...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path, device_map="auto", trust_remote_code=True,
        )
    model.eval()
    print(f"✅ 加载完成 耗时 {time.time()-t0:.1f}s")

    # 报告显存
    try:
        import pynvml
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        used = pynvml.nvmlDeviceGetMemoryInfo(h).used / 1024**3
        total = pynvml.nvmlDeviceGetMemoryInfo(h).total / 1024**3
        pynvml.nvmlShutdown()
        print(f"   显存占用:{used:.2f} / {total:.2f} GB")
    except Exception:
        pass

    return model, tokenizer


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 256) -> tuple[str, float]:
    """生成回复,返回 (text, tokens_per_second)"""
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    n_in = inputs.input_ids.shape[1]

    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    dt = time.time() - t0

    new_ids = out[0][n_in:]
    new_text = tokenizer.decode(new_ids, skip_special_tokens=True)
    tps = len(new_ids) / dt if dt > 0 else 0
    return new_text, tps


# ----------------------------------------------------------------------
# 模式:chat
# ----------------------------------------------------------------------

def mode_chat(model, tokenizer, max_new_tokens: int):
    print("\n" + "=" * 60)
    print("💬 进入聊天模式(输入 'quit' 或 'exit' 退出)")
    print("=" * 60 + "\n")

    history = []
    while True:
        try:
            user = input("🧑 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break
        if not user:
            continue
        if user.lower() in ("quit", "exit"):
            print("再见!")
            break

        # 简化处理:不维护多轮历史(量化模型对长上下文更敏感)
        text, tps = generate(model, tokenizer, user, max_new_tokens)
        print(f"\n🤖 模型 ({tps:.1f} tok/s):\n{text}\n")


# ----------------------------------------------------------------------
# 模式:bench
# ----------------------------------------------------------------------

BENCH_PROMPTS = [
    "Hello! How are you today?",
    "用三句话介绍深度学习。",
    "Write a Python function to reverse a string.",
    "What are the benefits of exercise?",
    "解释什么是 GPU。",
]

def mode_bench(model, tokenizer, max_new_tokens: int):
    print("\n" + "=" * 60)
    print("📊 性能测试")
    print("=" * 60)

    total_tokens = 0
    total_time = 0.0
    for i, p in enumerate(BENCH_PROMPTS, 1):
        text, tps = generate(model, tokenizer, p, max_new_tokens)
        # 简单估算 token 数
        n_new = len(tokenizer.encode(text))
        total_tokens += n_new
        total_time += n_new / tps if tps > 0 else 0
        print(f"\n[Prompt {i}] {p}")
        print(f"  → {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"  速度: {tps:.1f} tok/s")

    print(f"\n{'=' * 60}")
    print(f"总计 {total_tokens} tokens / {total_time:.2f}s")
    print(f"平均吞吐: {total_tokens/total_time:.1f} tok/s")
    print("=" * 60)


# ----------------------------------------------------------------------
# 模式:api(OpenAI 兼容,需要 fastapi + uvicorn)
# ----------------------------------------------------------------------

def mode_api(model, tokenizer, port: int, max_new_tokens: int):
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        print("API 模式需要 fastapi 和 uvicorn:")
        print("  pip install fastapi uvicorn")
        sys.exit(1)

    app = FastAPI(title="GPTQ Quantized LLM API")

    class ChatRequest(BaseModel):
        model: str = "default"
        messages: list[dict]
        max_tokens: int = max_new_tokens
        temperature: float = 0.0

    @app.post("/v1/chat/completions")
    def chat_completions(req: ChatRequest):
        # 拼接 messages
        text = tokenizer.apply_chat_template(
            req.messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=req.max_tokens,
                do_sample=(req.temperature > 0),
                temperature=max(req.temperature, 0.01),
                pad_token_id=tokenizer.pad_token_id,
            )
        new_text = tokenizer.decode(out[0][inputs.input_ids.shape[1]:],
                                     skip_special_tokens=True)
        return JSONResponse({
            "id": "chatcmpl-quantized",
            "object": "chat.completion",
            "model": req.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": new_text},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": inputs.input_ids.shape[1],
                "completion_tokens": len(tokenizer.encode(new_text)),
            },
        })

    @app.get("/v1/models")
    def list_models():
        return {"data": [{"id": "quantized-llm", "object": "model"}]}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    print(f"\n🚀 API 服务启动:http://0.0.0.0:{port}")
    print(f"   POST /v1/chat/completions  (OpenAI 兼容)")
    print(f"   GET  /v1/models")
    print(f"   GET  /health")
    uvicorn.run(app, host="0.0.0.0", port=port)


# ----------------------------------------------------------------------

def main():
    args = parse_args()
    model, tokenizer = load_quantized(args.model)

    if args.mode == "chat":
        mode_chat(model, tokenizer, args.max_new_tokens)
    elif args.mode == "bench":
        mode_bench(model, tokenizer, args.max_new_tokens)
    elif args.mode == "api":
        mode_api(model, tokenizer, args.port, args.max_new_tokens)


if __name__ == "__main__":
    main()
