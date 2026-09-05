#!/usr/bin/env bash
# 内部 wrapper:激活 conda 环境,然后跑指定命令
# 用法: _run_with_env.sh <command...>
set -e
source /mnt/i/learn_project/anaconda/etc/profile.d/conda.sh
conda activate inference_opt
exec "$@"
