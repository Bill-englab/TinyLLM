#!/usr/bin/env python3
"""检测当前 Python 环境是否满足阶段 2 量化实验的需求。"""
import importlib

PACKAGES = [
    "torch",
    "transformers",
    "vllm",
    "bitsandbytes",
    "auto_gptq",
    "accelerate",
    "optimum",
    "pynvml",
]

def main():
    print("=" * 50)
    print("环境检测")
    print("=" * 50)

    for pkg in PACKAGES:
        try:
            m = importlib.import_module(pkg)
            v = getattr(m, "__version__", "?")
            print(f"  OK   {pkg:<15} {v}")
        except ImportError:
            print(f"  MISS {pkg:<15} not installed")

    print()
    try:
        import torch
        print(f"CUDA available:  {torch.cuda.is_available()}")
        print(f"CUDA version:    {torch.version.cuda}")
        if torch.cuda.is_available():
            print(f"GPU:             {torch.cuda.get_device_name(0)}")
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU memory:      {total:.2f} GB")
    except Exception as e:
        print(f"torch check failed: {e}")

    print()
    import sys
    print(f"Python:  {sys.version.split()[0]}")
    print(f"Binary:  {sys.executable}")


if __name__ == "__main__":
    main()
