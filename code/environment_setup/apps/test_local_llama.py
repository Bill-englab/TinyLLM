#!/usr/bin/env python3
"""
测试本地Llama-3.2-1B模型
使用vLLM加载和推理
"""

import time
from vllm import LLM, SamplingParams

def test_local_model():
    """测试本地模型推理"""
    model_path = "/mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

    print("🚀 测试本地Llama-3.2-1B模型")
    print("=" * 60)
    print(f"📦 模型路径: {model_path}")
    print()

    # 检查模型文件
    import os
    if not os.path.exists(model_path):
        print(f"❌ 模型路径不存在: {model_path}")
        return False

    print("📋 模型文件检查:")
    model_files = os.listdir(model_path)
    required_files = ['config.json', 'tokenizer.json', 'model.safetensors']

    for file in required_files:
        status = "✅" if file in model_files else "❌"
        print(f"  {status} {file}")

    if not all(file in model_files for file in required_files):
        print("❌ 缺少必要的模型文件")
        return False

    print()
    print("🔥 开始加载模型...")
    load_start = time.time()

    try:
        # 创建LLM实例
        llm = LLM(
            model=model_path,
            gpu_memory_utilization=0.6,  # 使用60%显存
            max_model_len=8192,          # 最大长度
            dtype='half'                 # 使用FP16
        )

        load_time = time.time() - load_start
        print(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")

        # 设置采样参数
        sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=256
        )

        # 测试提示词
        prompts = [
            "Hello, my name is",
            "The capital of France is",
            "Machine learning is",
            "What is AI?"
        ]

        print(f"\n🧪 开始推理测试 ({len(prompts)}个提示词)...")
        print("-" * 60)

        # 执行推理
        inference_start = time.time()
        outputs = llm.generate(prompts, sampling_params)
        inference_time = time.time() - inference_start

        # 显示结果
        for i, output in enumerate(outputs, 1):
            print(f"\n测试 {i}:")
            print(f"输入: {output.prompt}")
            print(f"输出: {output.outputs[0].text}")
            print(f"tokens: {len(output.outputs[0].token_ids)}")

        # 性能统计
        total_tokens = sum(len(output.outputs[0].token_ids) for output in outputs)
        tokens_per_second = total_tokens / inference_time
        avg_time_per_request = inference_time / len(prompts)

        print(f"\n" + "=" * 60)
        print("📊 性能统计:")
        print(f"  总推理时间: {inference_time:.2f}秒")
        print(f"  平均每个请求: {avg_time_per_request:.2f}秒")
        print(f"  总生成tokens: {total_tokens}")
        print(f"  生成速度: {tokens_per_second:.2f} tokens/秒")

        print("\n🎉 测试成功！模型运行正常")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_mode():
    """测试对话模式"""
    model_path = "/mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

    print("\n💬 测试对话模式")
    print("=" * 60)

    try:
        from transformers import AutoTokenizer

        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print(f"✅ Tokenizer加载成功")
        print(f"  词汇表大小: {tokenizer.vocab_size}")
        print(f"  BOS token: {tokenizer.bos_token} (ID: {tokenizer.bos_token_id})")
        print(f"  EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")

        # 构造对话格式
        messages = [
            {"role": "user", "content": "What is machine learning?"}
        ]

        # 使用Llama-3聊天模板
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        print(f"\n📝 格式化输入:\n{text}")

        return True

    except Exception as e:
        print(f"❌ 对话模式测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行测试
    results = []

    # 基础推理测试
    results.append(("模型推理", test_local_model()))

    # 对话模式测试
    results.append(("对话模式", test_chat_mode()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("-" * 60)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)
    print()

    if all_passed:
        print("🎉 所有测试通过！本地模型可以正常使用")
        print()
        print("💡 使用建议:")
        print("  1. 此模型适合快速测试和学习")
        print("  2. 1B参数模型性能有限，适合简单任务")
        print("  3. 可以用于vLLM的基本功能学习")
    else:
        print("⚠️  部分测试失败，请检查配置")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)