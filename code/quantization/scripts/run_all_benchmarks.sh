#!/usr/bin/env bash
# 一键跑全部基准测试
#
# 用法(WSL2,inference_opt 环境):
#   conda activate inference_opt
#   bash /mnt/d/LLM_Project/code/quantization/scripts/run_all_benchmarks.sh
#
# 前置条件:
#   - FP16 模型:code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct
#   - GPTQ 模型:code/model/llama-3.2-1b-gptq-4bit(由 experiments/gptq_quantize.py 产出)

set -e

PYTHON="/home/qiu/envs/inference_opt/bin/python"
ROOT="/mnt/d/LLM_Project/code"

FP16="$ROOT/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"
GPTQ="$ROOT/model/llama-3.2-1b-gptq-4bit"

if [ ! -d "$GPTQ" ]; then
    echo "❌ GPTQ 模型不存在: $GPTQ"
    echo "   请先跑 experiments/gptq_quantize.py"
    exit 1
fi

echo "===================================================="
echo "基准 1/3:吞吐量"
echo "===================================================="
$PYTHON "$ROOT/quantization/benchmarks/bench_throughput.py" \
    --fp16 "$FP16" \
    --bnb-int8 --bnb-nf4 \
    --gptq "$GPTQ" \
    --batch-sizes 1 4 8

echo
echo "===================================================="
echo "基准 2/3:显存"
echo "===================================================="
$PYTHON "$ROOT/quantization/benchmarks/bench_memory.py" \
    --fp16 "$FP16" \
    --bnb-int8 --bnb-nf4 \
    --gptq "$GPTQ"

echo
echo "===================================================="
echo "基准 3/3:质量"
echo "===================================================="
$PYTHON "$ROOT/quantization/benchmarks/bench_quality.py" \
    --fp16 "$FP16" \
    --bnb-int8 --bnb-nf4 \
    --gptq "$GPTQ"

echo
echo "✅ 全部基准测试完成"
echo "   日志在: $ROOT/quantization/logs/bench_*.md"
