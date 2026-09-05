"""
GPU监控模块
学习目标：实时监控GPU状态
"""
import torch
import psutil
import time
from datetime import datetime
from typing import Dict, List
import json

class GPUMonitor:
    """GPU性能监控器"""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.history = []
        self.max_history_length = 100

    def get_gpu_info(self) -> Dict:
        """获取当前GPU状态"""
        if not torch.cuda.is_available():
            return {
                "timestamp": datetime.now().isoformat(),
                "gpu_available": False,
                "message": "CUDA不可用"
            }

        try:
            # 获取GPU属性
            gpu_props = torch.cuda.get_device_properties(0)
            gpu_name = gpu_props.name
            total_memory = gpu_props.total_memory / (1024**3)  # GB

            # 获取显存使用情况
            allocated_memory = torch.cuda.memory_allocated(0) / (1024**3)  # GB
            cached_memory = torch.cuda.memory_reserved(0) / (1024**3)  # GB
            free_memory = total_memory - allocated_memory

            # GPU利用率（需要nvidia-ml-py）
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = utilization.gpu
                memory_util = utilization.memory

                # 温度
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                pynvml.nvmlShutdown()
            except ImportError:
                gpu_util = "未知"
                memory_util = "未知"
                temperature = "未知"

            # CPU和内存使用情况
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024**3)  # GB
            ram_total = ram.total / (1024**3)  # GB
            ram_percent = ram.percent

            info = {
                "timestamp": datetime.now().isoformat(),
                "gpu_available": True,
                "gpu_name": gpu_name,
                "gpu_memory": {
                    "total": round(total_memory, 2),
                    "allocated": round(allocated_memory, 2),
                    "cached": round(cached_memory, 2),
                    "free": round(free_memory, 2),
                    "utilization": memory_util
                },
                "gpu_utilization": gpu_util,
                "temperature": temperature,
                "cpu": {
                    "percent": cpu_percent,
                    "core_count": psutil.cpu_count()
                },
                "ram": {
                    "used": round(ram_used, 2),
                    "total": round(ram_total, 2),
                    "percent": ram_percent
                }
            }

            return info

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "gpu_available": False,
                "error": str(e)
            }

    def record_snapshot(self):
        """记录当前状态快照"""
        info = self.get_gpu_info()
        self.history.append(info)

        # 限制历史记录长度
        if len(self.history) > self.max_history_length:
            self.history.pop(0)

        return info

    def get_history(self) -> List[Dict]:
        """获取历史记录"""
        return self.history

    def get_summary(self) -> Dict:
        """获取统计摘要"""
        if not self.history:
            return {}

        gpu_utils = [h.get("gpu_utilization", 0) for h in self.history if isinstance(h.get("gpu_utilization"), (int, float))]
        temps = [h.get("temperature", 0) for h in self.history if isinstance(h.get("temperature"), (int, float))]
        mem_utils = [h.get("gpu_memory", {}).get("utilization", 0) for h in self.history if isinstance(h.get("gpu_memory", {}).get("utilization"), (int, float))]

        summary = {
            "record_count": len(self.history),
            "time_range": {
                "start": self.history[0]["timestamp"],
                "end": self.history[-1]["timestamp"]
            }
        }

        if gpu_utils:
            summary["gpu_utilization"] = {
                "avg": round(sum(gpu_utils) / len(gpu_utils), 1),
                "max": max(gpu_utils),
                "min": min(gpu_utils)
            }

        if temps:
            summary["temperature"] = {
                "avg": round(sum(temps) / len(temps), 1),
                "max": max(temps),
                "min": min(temps)
            }

        if mem_utils:
            summary["memory_utilization"] = {
                "avg": round(sum(mem_utils) / len(mem_utils), 1),
                "max": max(mem_utils),
                "min": min(mem_utils)
            }

        return summary

    def clear_history(self):
        """清除历史记录"""
        self.history = []

    def save_to_file(self, filename: str):
        """保存历史记录到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

# 测试函数
def test_gpu_monitor():
    """测试GPU监控器"""
    monitor = GPUMonitor()

    print("GPU监控测试")
    print("=" * 50)

    # 获取当前状态
    current = monitor.get_gpu_info()
    print("当前GPU状态:")
    print(json.dumps(current, indent=2, ensure_ascii=False))

    # 连续监控几次
    print("\n连续监控5秒...")
    for i in range(5):
        monitor.record_snapshot()
        time.sleep(1)
        print(f"第{i+1}秒: GPU利用率 {monitor.history[-1].get('gpu_utilization', 'N/A')}%")

    # 显示统计摘要
    print("\n统计摘要:")
    summary = monitor.get_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_gpu_monitor()