"""
集成监控仪表盘
学习目标：创建可视化的监控系统
"""
import gradio as gr
import time
import json
from datetime import datetime
import sys
import io

# 导入监控模块
sys.path.append('.')
from monitoring.gpu_monitor import GPUMonitor
from monitoring.performance_monitor import InferencePerformanceMonitor

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class MonitoringDashboard:
    """监控仪表盘"""

    def __init__(self):
        self.gpu_monitor = GPUMonitor()
        self.perf_monitor = InferencePerformanceMonitor()
        self.monitoring_active = False
        self.monitor_interval = 2.0  # 监控间隔(秒)

    def update_gpu_stats(self):
        """更新GPU统计信息"""
        gpu_info = self.gpu_monitor.record_snapshot()

        # 格式化显示
        if not gpu_info.get("gpu_available"):
            return "❌ GPU不可用"

        gpu_name = gpu_info.get("gpu_name", "未知")
        memory = gpu_info.get("gpu_memory", {})
        gpu_util = gpu_info.get("gpu_utilization", "N/A")
        temp = gpu_info.get("temperature", "N/A")
        cpu = gpu_info.get("cpu", {})
        ram = gpu_info.get("ram", {})

        stats = f"""
### 🖥️ GPU状态
**型号**: {gpu_name}
**利用率**: {gpu_util}%
**温度**: {temp}°C

### 💾 显存使用
**总量**: {memory.get('total', 0):.1f} GB
**已分配**: {memory.get('allocated', 0):.1f} GB
**缓存**: {memory.get('cached', 0):.1f} GB
**空闲**: {memory.get('free', 0):.1f} GB
**利用率**: {memory.get('utilization', 0)}%

### 📊 系统资源
**CPU**: {cpu.get('percent', 0)}% ({cpu.get('core_count', 0)}核心)
**内存**: {ram.get('used', 0):.1f}GB / {ram.get('total', 0):.1f}GB ({ram.get('percent', 0)}%)
"""
        return stats

    def update_performance_stats(self):
        """更新性能统计信息"""
        stats = self.perf_monitor.get_current_stats()

        if "message" in stats:
            return "### 📈 性能统计\n暂无推理数据"

        perf_info = f"""
### 📈 推理性能统计
**总推理次数**: {stats['total_inferences']}
**推理吞吐量**: {stats['throughput']['inferences_per_second']} inferences/秒

### ⏱️ 推理时间
**平均**: {stats['inference_time']['avg']:.4f}秒
**最短**: {stats['inference_time']['min']:.4f}秒
**最长**: {stats['inference_time']['max']:.4f}秒
**总耗时**: {stats['inference_time']['total']:.4f}秒

### 🚀 Token生成速度
**平均**: {stats.get('tokens_per_second', {}).get('avg', 0):.2f} tokens/秒
**最快**: {stats.get('tokens_per_second', {}).get('max', 0):.2f} tokens/秒
**最慢**: {stats.get('tokens_per_second', {}).get('min', 0):.2f} tokens/秒

### 📝 Token统计
**平均生成**: {stats.get('tokens_per_inference', {}).get('avg', 0):.1f} tokens
**最少生成**: {stats.get('tokens_per_inference', {}).get('min', 0)} tokens
**最多生成**: {stats.get('tokens_per_inference', {}).get('max', 0)} tokens
"""
        return perf_info

    def get_recent_activity(self):
        """获取最近活动"""
        recent = self.perf_monitor.get_recent_inferences(5)

        if not recent:
            return "暂无最近活动"

        activity = "### 🕐 最近活动\n\n"
        for i, record in enumerate(recent, 1):
            timestamp = record['start_timestamp'].split('T')[1].split('.')[0]
            prompt = record['prompt'][:30] + "..." if len(record['prompt']) > 30 else record['prompt']
            activity += f"**{i}. {timestamp}**\n"
            activity += f"   提示词: {prompt}\n"
            activity += f"   推理时间: {record['inference_time']}秒\n"
            activity += f"   生成: {record['tokens_generated']} tokens\n"
            activity += f"   速度: {record['tokens_per_second']} tokens/秒\n\n"

        return activity

    def simulate_inference(self, prompt):
        """模拟推理（用于演示）"""
        # 开始监控
        self.perf_monitor.start_inference(prompt, "LLaMA-3.2-1B")

        # 模拟推理时间
        import random
        simulated_time = 0.3 + random.random() * 0.5
        time.sleep(simulated_time)

        # 模拟回复
        tokens_generated = random.randint(20, 50)
        response = f"这是对'{prompt}'的模拟回复，包含{tokens_generated}个token。在实际应用中，这里会调用真实的模型进行推理。"

        # 结束监控
        perf_data = self.perf_monitor.end_inference(response, tokens_generated)

        return response, f"✅ 推理完成！耗时: {perf_data['inference_time']}秒，速度: {perf_data['tokens_per_second']} tokens/秒"

    def clear_data(self):
        """清除监控数据"""
        self.gpu_monitor.clear_history()
        self.perf_monitor.clear_history()
        return "🗑️ 数据已清除"

    def export_data(self):
        """导出监控数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gpu_filename = f"gpu_monitor_{timestamp}.json"
        perf_filename = f"perf_monitor_{timestamp}.json"

        try:
            self.gpu_monitor.save_to_file(gpu_filename)
            self.perf_monitor.export_to_json(perf_filename)
            return f"✅ 数据已导出:\n- {gpu_filename}\n- {perf_filename}"
        except Exception as e:
            return f"❌ 导出失败: {str(e)}"

def create_dashboard():
    """创建监控仪表盘界面"""
    dashboard = MonitoringDashboard()

    with gr.Blocks(title="AI推理监控系统") as demo:
        gr.Markdown("# 🎯 AI推理优化监控系统")
        gr.Markdown("学习项目：GPU监控 + 性能分析 + 可视化仪表盘")

        with gr.Tabs():
            # 实时监控标签页
            with gr.Tab("📊 实时监控"):
                with gr.Row():
                    with gr.Column():
                        gpu_stats = gr.Markdown("### 🖥️ GPU状态\n正在加载...")
                        refresh_gpu = gr.Button("🔄 刷新GPU状态", size="sm")

                    with gr.Column():
                        perf_stats = gr.Markdown("### 📈 性能统计\n正在加载...")
                        refresh_perf = gr.Button("🔄 刷新性能统计", size="sm")

            # 推理测试标签页
            with gr.Tab("🧪 推理测试"):
                gr.Markdown("### 模拟推理测试（用于演示监控功能）")

                with gr.Row():
                    test_prompt = gr.Textbox(
                        label="测试提示词",
                        placeholder="输入测试文本...",
                        value="你好，请介绍一下你自己"
                    )
                    test_btn = gr.Button("🚀 开始推理", variant="primary")

                test_response = gr.Textbox(label="模型回复", lines=3)
                test_result = gr.Textbox(label="推理结果", lines=2)

            # 活动记录标签页
            with gr.Tab("📋 活动记录"):
                recent_activity = gr.Markdown("### 🕐 最近活动\n暂无数据")
                refresh_activity = gr.Button("🔄 刷新活动记录", size="sm")

            # 数据管理标签页
            with gr.Tab("💾 数据管理"):
                gr.Markdown("### 监控数据管理")

                with gr.Row():
                    clear_btn = gr.Button("🗑️ 清除所有数据", variant="stop")
                    export_btn = gr.Button("📥 导出数据", variant="secondary")

                export_result = gr.Textbox(label="操作结果", lines=3)

        # 事件绑定
        refresh_gpu.click(
            dashboard.update_gpu_stats,
            outputs=gpu_stats
        )

        refresh_perf.click(
            dashboard.update_performance_stats,
            outputs=perf_stats
        )

        refresh_activity.click(
            dashboard.get_recent_activity,
            outputs=recent_activity
        )

        test_btn.click(
            dashboard.simulate_inference,
            inputs=test_prompt,
            outputs=[test_response, test_result]
        ).then(
            dashboard.update_performance_stats,
            outputs=perf_stats
        ).then(
            dashboard.get_recent_activity,
            outputs=recent_activity
        )

        clear_btn.click(
            dashboard.clear_data,
            outputs=export_result
        ).then(
            lambda: [dashboard.update_gpu_stats(), dashboard.update_performance_stats(), dashboard.get_recent_activity()],
            outputs=[gpu_stats, perf_stats, recent_activity]
        )

        export_btn.click(
            dashboard.export_data,
            outputs=export_result
        )

        # 初始加载
        demo.load(
            lambda: [dashboard.update_gpu_stats(), dashboard.update_performance_stats(), dashboard.get_recent_activity()],
            outputs=[gpu_stats, perf_stats, recent_activity]
        )

    return demo

if __name__ == "__main__":
    print("启动AI推理监控系统...")
    demo = create_dashboard()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False
    )