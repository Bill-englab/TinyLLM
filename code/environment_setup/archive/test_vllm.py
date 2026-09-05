#!/usr/bin/env python3
"""
vLLM基础测试脚本
用于测试环境配置是否正常
"""

import time
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

def test_basic_inference():
    """测试基础推理功能"""
    print("🧪 开始vLLM基础测试...")
    print("=" * 60)

    # 使用小模型进行快速测试
    model_name = "gpt2"

    print(f"📦 加载模型: {model_name}")
    start_time = time.time()

    try:
        # 创建LLM实例
        llm = LLM(model=model_name, gpu_memory_utilization=0.4)

        load_time = time.time() - start_time
        print(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")

        # 设置采样参数
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.95,
            max_tokens=50
        )

        # 测试提示词
        prompts = [
            "Hello, my name is",
            "The future of AI is",
            "Machine learning is"
        ]

        print(f"\n🔥 开始推理测试...")
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

        print(f"\n✅ 推理测试完成！")
        print(f"总推理时间: {inference_time:.2f}秒")
        print(f"平均每个请求: {inference_time/len(prompts):.2f}秒")

        # 性能统计
        total_tokens = sum(len(output.outputs[0].token_ids) for output in outputs)
        tokens_per_second = total_tokens / inference_time

        print(f"总生成tokens: {total_tokens}")
        print(f"生成速度: {tokens_per_second:.2f} tokens/秒")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！环境配置正常")
    return True

def test_gpu_monitoring():
    """测试GPU监控功能"""
    print("\n🖥️  GPU监控测试...")
    print("-" * 60)

    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        # 获取GPU信息
        name = pynvml.nvmlDeviceGetName(handle)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

        print(f"GPU名称: {name.decode('utf-8')}")
        print(f"显存使用: {memory_info.used / 1024**3:.2f}GB / {memory_info.total / 1024**3:.2f}GB")
        print(f"显存占用率: {memory_info.used / memory_info.total * 100:.1f}%")
        print(f"GPU利用率: {utilization.gpu}%")
        print(f"GPU温度: {temperature}°C")

        pynvml.nvmlShutdown()
        print("✅ GPU监控正常")
        return True

    except Exception as e:
        print(f"❌ GPU监控测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 vLLM环境综合测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行测试
    results = []

    # GPU监控测试
    results.append(("GPU监控", test_gpu_monitoring()))

    # 基础推理测试
    results.append(("基础推理", test_basic_inference()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("-" * 60)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    print()
    if all_passed:
        print("🎉 恭喜！所有测试通过，环境可以正常使用！")
    else:
        print("⚠️  部分测试失败，请检查环境配置")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)