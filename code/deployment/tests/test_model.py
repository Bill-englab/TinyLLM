"""
测试下载的LLaMA-3.2-1B模型
"""
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_PATH = "../../model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

def test_model():
    print("开始测试模型...")

    # 加载tokenizer和模型
    print("加载tokenizer和模型...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    print("模型加载成功!")

    # 显示模型信息
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n模型信息:")
    print(f"  参数量: {total_params / 1e9:.2f}B")
    print(f"  数据类型: {next(model.parameters()).dtype}")
    print(f"  设备: {next(model.parameters()).device}")

    # 测试推理
    print("\n测试推理功能...")
    test_prompts = [
        "Hello, how are you?",
        "What is AI?",
        "介绍一下你自己"
    ]

    for prompt in test_prompts:
        print(f"\n输入: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=50,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"输出: {response}")

    print("\n模型测试完成!")

if __name__ == "__main__":
    test_model()