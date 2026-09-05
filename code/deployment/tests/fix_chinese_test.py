"""
修复中文输出的模型测试脚本
"""
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
import sys
import io

# 设置标准输出为UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODEL_PATH = "../../model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

def test_chinese_output():
    print("开始测试中文输出...")

    # 加载tokenizer和模型
    print("加载模型...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    # 设置pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("模型加载成功!\n")

    # 测试中文问题
    chinese_tests = [
        "你好，请介绍一下你自己",
        "什么是人工智能？",
        "用中文回答：今天天气怎么样？",
        "请用中文写一首关于春天的诗"
    ]

    for i, prompt in enumerate(chinese_tests, 1):
        print(f"测试 {i}:")
        print(f"输入: {prompt}")

        # 使用正确的chat template格式
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )

        # 解码输出，跳过输入部分
        response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        print(f"输出: {response}")
        print("-" * 50)

    print("\n中文测试完成!")

if __name__ == "__main__":
    test_chinese_output()