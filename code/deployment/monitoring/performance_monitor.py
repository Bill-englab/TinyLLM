"""
推理性能监控模块
学习目标：监控模型推理性能指标
"""
import time
import torch
from typing import Dict, List, Optional
from datetime import datetime
import json
from collections import deque

class InferencePerformanceMonitor:
    """推理性能监控器"""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.inference_history = deque(maxlen=max_history)
        self.current_inference = None

    def start_inference(self, prompt: str, model_name: str = "unknown"):
        """开始推理计时"""
        self.current_inference = {
            "prompt": prompt,
            "prompt_length": len(prompt),
            "model_name": model_name,
            "start_time": time.time(),
            "start_timestamp": datetime.now().isoformat()
        }

    def end_inference(self, response: str, tokens_generated: int = 0):
        """结束推理计时"""
        if self.current_inference is None:
            raise ValueError("没有正在进行的推理")

        end_time = time.time()
        inference_time = end_time - self.current_inference["start_time"]

        # 计算性能指标
        performance_data = {
            **self.current_inference,
            "response": response,
            "response_length": len(response),
            "tokens_generated": tokens_generated,
            "end_time": end_time,
            "end_timestamp": datetime.now().isoformat(),
            "inference_time": round(inference_time, 4),
            "tokens_per_second": round(tokens_generated / inference_time, 2) if inference_time > 0 and tokens_generated > 0 else 0,
            "time_per_token": round(inference_time / tokens_generated, 4) if tokens_generated > 0 else 0
        }

        self.inference_history.append(performance_data)
        self.current_inference = None

        return performance_data

    def get_current_stats(self) -> Dict:
        """获取当前统计信息"""
        if not self.inference_history:
            return {"message": "暂无推理记录"}

        recent_records = list(self.inference_history)

        # 计算统计数据
        inference_times = [r["inference_time"] for r in recent_records]
        tps_list = [r["tokens_per_second"] for r in recent_records if r["tokens_per_second"] > 0]
        tokens_per_inference = [r["tokens_generated"] for r in recent_records]

        stats = {
            "total_inferences": len(recent_records),
            "time_range": {
                "first": recent_records[0]["start_timestamp"],
                "last": recent_records[-1]["end_timestamp"]
            },
            "inference_time": {
                "avg": round(sum(inference_times) / len(inference_times), 4),
                "min": round(min(inference_times), 4),
                "max": round(max(inference_times), 4),
                "total": round(sum(inference_times), 4)
            },
            "throughput": {
                "inferences_per_second": round(len(recent_records) / sum(inference_times), 2) if sum(inference_times) > 0 else 0
            }
        }

        if tps_list:
            stats["tokens_per_second"] = {
                "avg": round(sum(tps_list) / len(tps_list), 2),
                "min": round(min(tps_list), 2),
                "max": round(max(tps_list), 2)
            }

        if tokens_per_inference:
            stats["tokens_per_inference"] = {
                "avg": round(sum(tokens_per_inference) / len(tokens_per_inference), 2),
                "min": min(tokens_per_inference),
                "max": max(tokens_per_inference)
            }

        return stats

    def get_recent_inferences(self, count: int = 10) -> List[Dict]:
        """获取最近的推理记录"""
        return list(self.inference_history)[-count:]

    def clear_history(self):
        """清除历史记录"""
        self.inference_history.clear()

    def export_to_json(self, filename: str):
        """导出数据到JSON文件"""
        data = {
            "statistics": self.get_current_stats(),
            "history": list(self.inference_history)
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# 测试函数
def test_performance_monitor():
    """测试性能监控器"""
    monitor = InferencePerformanceMonitor()

    print("推理性能监控测试")
    print("=" * 50)

    # 模拟几次推理
    test_prompts = [
        "你好",
        "什么是人工智能？",
        "请介绍一下Python编程语言",
        "如何学习机器学习？",
        "解释深度学习的概念"
    ]

    for i, prompt in enumerate(test_prompts, 1):
        # 开始推理
        monitor.start_inference(prompt, "LLaMA-3.2-1B")

        # 模拟推理时间
        simulated_time = 0.5 + i * 0.1
        time.sleep(simulated_time)

        # 模拟生成token数量
        tokens_generated = 20 + i * 10

        # 模拟回复
        response = f"这是对'{prompt}'的回复，包含{tokens_generated}个token"

        # 结束推理
        perf_data = monitor.end_inference(response, tokens_generated)

        print(f"推理 {i}:")
        print(f"  提示词: {prompt[:30]}...")
        print(f"  推理时间: {perf_data['inference_time']}秒")
        print(f"  生成token: {tokens_generated}")
        print(f"  速度: {perf_data['tokens_per_second']} tokens/秒")
        print()

    # 显示统计信息
    print("统计摘要:")
    stats = monitor.get_current_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # 显示最近几次推理
    print(f"\n最近{min(3, len(test_prompts))}次推理:")
    recent = monitor.get_recent_inferences(3)
    for record in recent:
        print(f"  {record['prompt'][:20]}... -> {record['inference_time']}秒")

if __name__ == "__main__":
    test_performance_monitor()