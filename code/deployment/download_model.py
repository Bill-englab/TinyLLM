"""
通过ModelScope SDK下载LLaMA-3.2-1B-Instruct模型
"""
from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer
import torch
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

MODEL_ID = "LLM-Research/Llama-3.2-1B-Instruct"
MODEL_PATH = "../model/llama-3.2-1b-instruct"

def download_model():
    print(f"开始通过ModelScope下载模型: {MODEL_ID}")
    print(f"保存路径: {MODEL_PATH}")

    try:
        # 下载模型到本地
        print("正在下载模型文件...")
        model_dir = snapshot_download(
            MODEL_ID,
            cache_dir=MODEL_PATH,
            revision="master"
        )
        print(f"模型下载完成! 保存至: {model_dir}")

        # 加载模型进行测试
        print("\n测试加载模型...")
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("模型加载成功!")

        # 显示模型信息
        total_params = sum(p.numel() for p in model.parameters())
        print(f"\n模型信息:")
        print(f"   参数量: {total_params / 1e9:.2f}B")
        print(f"   数据类型: {next(model.parameters()).dtype}")
        print(f"   设备: {next(model.parameters()).device}")

        # 测试推理
        print("\n测试模型推理...")
        test_prompt = "Hello, how are you?"
        inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=20,
                do_sample=False
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"   输入: {test_prompt}")
        print(f"   输出: {response}")
        print("模型推理测试成功!")

        return model, tokenizer

    except Exception as e:
        print(f"下载失败: {e}")
        print("\n建议:")
        print("   1. 检查网络连接")
        print("   2. 访问 https://modelscope.cn/models/LLM-Research/Llama-3.2-1B-Instruct")
        print("   3. 尝试手动下载")
        raise

if __name__ == "__main__":
    try:
        model, tokenizer = download_model()
        print(f"\n全部完成! 模型已准备就绪")
        print(f"模型路径: {MODEL_PATH}")
    except Exception as e:
        print(f"\n过程出错: {e}")