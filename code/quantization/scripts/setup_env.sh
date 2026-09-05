#!/usr/bin/env bash
# ============================================================
# 修复版 v2:WSL2 ext4 + 国内镜像
#
# 改进:
#   1. envs/pkgs 落 WSL2 ext4(绕开 NTFS 大小写问题)
#   2. pip 全局走清华源
#   3. PyTorch wheel 走清华镜像(代替 download.pytorch.org)
#
# 用法:
#   bash /mnt/d/LLM_Project/code/quantization/scripts/setup_env.sh
# ============================================================
set -e

source "$(conda info --base)/etc/profile.d/conda.sh"

echo "===================================================="
echo "① 把 WSL2 原生路径加入 conda 配置"
echo "===================================================="
mkdir -p "$HOME/envs" "$HOME/conda-pkgs"
conda config --append envs_dirs "$HOME/envs"
conda config --append pkgs_dirs "$HOME/conda-pkgs"

echo
echo "===================================================="
echo "② 清理上次失败的半成品环境"
echo "===================================================="
rm -rf /mnt/i/learn_project/anaconda/envs/inference_opt 2>/dev/null || true
rm -rf "$HOME/envs/inference_opt" 2>/dev/null || true
conda env remove -n inference_opt 2>/dev/null || true

echo
echo "===================================================="
echo "③ 创建 inference_opt"
echo "===================================================="
conda create -n inference_opt python=3.10 -y

echo
echo "===================================================="
echo "④ 激活并验证路径"
echo "===================================================="
conda activate inference_opt
echo "Python 解释器: $(which python)"
case "$(which python)" in
    /mnt/*) echo "⚠️  Python 还在 /mnt 下,NTFS 大小写问题没解决"; exit 1 ;;
    *)      echo "OK 已在 WSL2 原生路径" ;;
esac

echo
echo "===================================================="
echo "⑤ 配置 pip 清华源(全局生效)"
echo "===================================================="
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
pip install --upgrade pip

echo
echo "===================================================="
echo "⑥ 安装 PyTorch (清华 cu121 镜像)"
echo "===================================================="
# 清华镜像代替 download.pytorch.org
pip install torch torchvision \
    --index-url https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu121

echo
echo "===================================================="
echo "⑦ 安装量化实验栈(走清华 PyPI 镜像)"
echo "===================================================="
pip install \
    "transformers>=4.40" \
    accelerate \
    optimum \
    bitsandbytes \
    auto-gptq \
    pynvml \
    sentencepiece \
    protobuf

echo
echo "===================================================="
echo "⑧ 验证安装"
echo "===================================================="
python -c "
import torch, transformers, bitsandbytes, auto_gptq, accelerate
print(f'torch           {torch.__version__}')
print(f'transformers    {transformers.__version__}')
print(f'bitsandbytes    {bitsandbytes.__version__}')
print(f'auto_gptq       {auto_gptq.__version__}')
print(f'accelerate      {accelerate.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU:            {torch.cuda.get_device_name(0)}')
"

echo
echo "===================================================="
echo "✅ 环境就绪"
echo "===================================================="
echo
echo "每次开新终端,先激活:"
echo "  conda activate inference_opt"
echo
echo "然后跑实验 1:"
echo "  python /mnt/d/LLM_Project/code/quantization/apps/quantize_bnb.py"
