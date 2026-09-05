#!/usr/bin/env python3
"""
使用Transformers测试本地Llama-3.2-1B模型
绕过vLLM的Triton编译问题
"""

import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def test_with_transformers():
    """使用Transformers测试模型"""
    model_path = "/mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

    print("🚀 使用Transformers测试本地Llama-3.2-1B模型")
    print("=" * 60)
    print(f"📦 模型路径: {model_path}")
    print()

    # 检查CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  使用设备: {device}")
    print(f"🔥 CUDA可用: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"📊 GPU名称: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")

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
        # 加载tokenizer
        print("📝 加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print(f"✅ Tokenizer加载成功")
        print(f"  词汇表大小: {tokenizer.vocab_size}")

        # 加载模型
        print("🧠 加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        load_time = time.time() - load_start
        print(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")

        # 显示模型信息
        print()
        print("📊 模型信息:")
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"  总参数量: {total_params:,}")
        print(f"  可训练参数: {trainable_params:,}")
        print(f"  模型大小: ~{total_params * 2 / 1024**3:.2f}GB (FP16)")

        # GPU显存使用
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.max_memory_allocated() / 1024**3
            print(f"  显存使用: {gpu_memory:.2f}GB")

        print()
        print("🧪 开始推理测试...")
        print("-" * 60)

        # 测试提示词
        prompts = [
            "Hello, my name is",
            "The capital of France is",
            "Machine learning is",
            "What is AI?"
        ]

        # 执行推理
        inference_start = time.time()

        for i, prompt in enumerate(prompts, 1):
            print(f"\n测试 {i}:")
            print(f"输入: {prompt}")

            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to(device) for k, v in inputs.items()}

            # 生成
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            # Decode
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated_only = generated_text[len(prompt):]

            print(f"输出: {generated_only}")
            print(f"tokens: {outputs.shape[1] - inputs['input_ids'].shape[1]}")

            # 清理GPU内存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        inference_time = time.time() - inference_start

        print()
        print("=" * 60)
        print("📊 性能统计:")
        print(f"  总推理时间: {inference_time:.2f}秒")
        print(f"  平均每个请求: {inference_time/len(prompts):.2f}秒")
        print(f"  平均速度: {len(prompts) / inference_time:.2f} 请求/秒")

        print("\n🎉 测试成功！模型运行正常")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_format():
    """测试聊天格式"""
    model_path = "/mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

    print("\n💬 测试聊天格式")
    print("=" * 60)

    try:
        from transformers import AutoTokenizer

        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        # 构造对话
        messages = [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is..."},
            {"role": "user", "content": "Can you explain more?"}
        ]

        # 应用聊天模板
        formatted_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        print("📝 聊天格式化输出:")
        print("-" * 60)
        print(formatted_text)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"❌ 聊天格式测试失败: {str(e)}")
        return False

def test_simple_generation():
    """简单生成测试"""
    model_path = "/mnt/d/LLM_Project/code/model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

    print("\n⚡ 快速生成测试")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        # 加载模型
        print("🔥 加载模型...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )

        # 简单推理
        prompt = "The future of AI is"
        inputs = tokenizer(prompt, return_tensors="pt")

        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        print(f"📝 输入: {prompt}")

        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        generation_time = time.time() - start_time

        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_only = result[len(prompt):]

        print(f"🤖 输出: {generated_only}")
        print(f"⏱️  生成时间: {generation_time:.2f}秒")
        print(f"📊 速度: {outputs.shape[1] - inputs['input_ids'].shape[1]:.0f} tokens / {generation_time:.2f}秒 = {(outputs.shape[1] - inputs['input_ids'].shape[1]) / generation_time:.1f} tokens/秒")

        return True

    except Exception as e:
        print(f"❌ 快速生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行测试
    results = []

    # 快速生成测试
    results.append(("快速生成", test_simple_generation()))

    # 聊天格式测试
    results.append(("聊天格式", test_chat_format()))

    # 完整测试
    results.append(("完整推理", test_with_transformers()))

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
        print("🎉 所有测试通过！本地Llama模型可以正常使用")
        print()
        print("💡 关于vLLM问题:")
        print("  当前WSL2环境下的vLLM有Triton编译问题")
        print("  但Transformers可以正常工作")
        print("  建议:")
        print("  1. 使用Transformers进行基础学习")
        print("  2. 等待vLLM修复或尝试其他推理框架")
        print("  3. 考虑使用ollama等其他推理工具")
    else:
        print("⚠️  部分测试失败，请检查配置")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)