# 模型文件说明

> ⚠️ 本目录下的模型文件体积过大,**不入 git 仓库**(见根目录 `.gitignore`)。
> 克隆仓库后需要按下述方法自行获取模型。

## 模型清单

| 目录 | 说明 | 体积 | 来源 |
|------|------|------|------|
| `llama-3.2-1b-instruct/` | FP16 基线模型(1.24B 参数) | 4.7 GB | ModelScope 下载 |
| `llama-3.2-1b-gptq-4bit/` | 阶段 2 产出的 GPTQ 4-bit 量化模型 | 0.98 GB | 本项目量化脚本生成 |

## 获取方式

### 1. FP16 基线模型(下载)

```bash
conda activate <环境名>
python code/deployment/download_model.py
```

或直接使用 ModelScope SDK:

```python
from modelscope import snapshot_download
model_dir = snapshot_download(
    "LLM-Research/Llama-3.2-1B-Instruct",
    cache_dir="code/model/llama-3.2-1b-instruct",
    revision="master",
)
```

下载完成后,实际模型位于
`code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct/`。

### 2. GPTQ 4-bit 量化模型(自行生成)

该模型是阶段 2 的实验产出,无法从外部下载,需运行量化脚本重新生成:

```bash
conda activate inference_opt   # WSL2 环境
python code/quantization/experiments/gptq_quantize.py
```

脚本会读取 FP16 基线模型,执行 GPTQ 4-bit 离线量化(约 5 分钟),
并将结果保存到本目录。实测压缩比 4.72×(4.61 GB → 0.98 GB),
困惑度损失仅 2.29%(PPL 3.197 → 3.271)。

详见 [阶段 2 量化文档](../quantization/docs/技术总结.md)。

## 目录结构

```
code/model/
├── README.md                    # 本文件
├── llama-3.2-1b-instruct/       # FP16 基线(ModelScope 目录结构)
│   └── LLM-Research/Llama-3___2-1B-Instruct/
│       ├── model.safetensors
│       ├── tokenizer.json
│       └── ...
└── llama-3.2-1b-gptq-4bit/      # GPTQ 量化模型(阶段 2 产出)
    ├── model.safetensors
    ├── tokenizer.json
    └── ...
```
