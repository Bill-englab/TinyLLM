#!/bin/bash

# 推理优化环境快速启动脚本

echo "🚀 推理优化环境启动"
echo "===================="

# 激活conda环境
echo "📦 激活conda环境..."
source /root/anaconda3/etc/profile.d/conda.sh
conda activate inference_opt

# 检查环境
echo "🔍 检查环境状态..."
echo ""

echo "🐍 Python版本:"
python --version

echo ""
echo "🔥 CUDA状态:"
python -c "import torch; print(f'  CUDA可用: {torch.cuda.is_available()}'); print(f'  CUDA版本: {torch.version.cuda}'); print(f'  GPU数量: {torch.cuda.device_count()}'); print(f'  GPU名称: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"无\"}')"

echo ""
echo "⚡ vLLM版本:"
python -c "import vllm; print(f'  vLLM版本: {vllm.__version__}')"

echo ""
echo "🖥️  GPU状态:"
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,name --format=csv,noheader,nounits | awk -F', ' '{printf \"  显存: %.1fGB/%.1fGB | 利用率: %d%% | GPU: %s\n\", $1/1024, $2/1024, $3, $4}'

echo ""
echo "✅ 环境就绪！"
echo ""
echo "📖 常用命令:"
echo "  测试vLLM:       python test_vllm.py"
echo "  GPU监控:        watch -n 1 nvidia-smi"
echo "  启动API服务:    python start_api_server.py"
echo "  查看帮助:       cat /mnt/d/LLM_Project/inference_environment_summary.md"
echo ""

# 检查是否有常用脚本
if [ -f "/mnt/d/LLM_Project/test_vllm.py" ]; then
    echo "💡 检测到测试脚本，运行 'python test_vllm.py' 开始测试"
else
    echo "💡 建议创建测试脚本开始实践"
fi

echo ""
echo "🎯 环境激活完成！现在可以开始推理优化实践了。"
echo "   使用 'conda deactivate' 退出环境"