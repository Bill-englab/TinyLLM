#!/usr/bin/env python3
"""
共享模型加载工具
================

统一的模型加载接口,处理 FP16 / bnb-INT8 / bnb-NF4 / GPTQ 四种方案。

特别注意:
  - GPTQ 通过 gptqmodel 直接加载,指定 backend=BACKEND.GPTQ_TRITON
  - 原因:transformers 默认会选 MarlinLinear,而 Marlin 需要 nvcc 12.x+ 才能编译
  - WSL2 上系统 nvcc 是 11.5,无法编译 Marlin,所以强制用 Triton
"""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def load_model(path: str, quant: str):
    """
    加载模型。返回 (model, tokenizer)。
    quant 取值:fp16 / gptq / bnb-int8 / bnb-nf4
    """
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if quant == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            path, dtype=torch.float16,
            device_map="auto", trust_remote_code=True,
        )

    elif quant == "gptq":
        # 关键修复:走 gptqmodel 直接 API,强制 Triton backend,绕开 Marlin
        # 否则 transformers 默认会选 MarlinLinear,在 nvcc 11.5 上编译失败
        try:
            from gptqmodel import GPTQModel, BACKEND
            model = GPTQModel.from_quantized(
                path,
                backend=BACKEND.GPTQ_TRITON,
            )
        except ImportError:
            # 旧版本没有 gptqmodel,走 transformers 默认路径
            model = AutoModelForCausalLM.from_pretrained(
                path, device_map="auto", trust_remote_code=True,
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
        raise ValueError(f"unknown quant: {quant}")

    model.eval()
    return model, tokenizer
