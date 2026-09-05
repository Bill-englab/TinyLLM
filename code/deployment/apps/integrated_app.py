"""
集成应用：模型推理 + 实时监控
一个文件搞定所有功能！
"""
import gradio as gr
import torch
import time
import json
from datetime import datetime
from modelscope import AutoModelForCausalLM, AutoTokenizer
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODEL_PATH = "../../model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

class IntegratedApp:
    def __init__(self):
        print("正在加载模型...")
        self.model_loaded = False
        self.load_model()
        self.inference_history = []

    def load_model(self):
        """加载模型"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            self.model_loaded = True
            print("✅ 模型加载成功!")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.model_loaded = False

    def get_gpu_info(self):
        """获取GPU信息"""
        if not torch.cuda.is_available():
            return "❌ GPU不可用"

        try:
            gpu_props = torch.cuda.get_device_properties(0)
            gpu_name = gpu_props.name
            total_memory = gpu_props.total_memory / (1024**3)
            allocated_memory = torch.cuda.memory_allocated(0) / (1024**3)
            free_memory = total_memory - allocated_memory

            # 获取GPU利用率
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = utilization.gpu
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                pynvml.nvmlShutdown()
            except:
                gpu_util = "N/A"
                temperature = "N/A"

            info = f"""
### 🖥️ GPU状态
**型号**: {gpu_name}
**利用率**: {gpu_util}%
**温度**: {temperature}°C
**显存**: {allocated_memory:.2f}GB / {total_memory:.2f}GB
**空闲**: {free_memory:.2f}GB
"""
            return info
        except Exception as e:
            return f"❌ 获取GPU信息失败: {e}"

    def get_performance_stats(self):
        """获取性能统计"""
        if not self.inference_history:
            return "### 📈 性能统计\n暂无推理数据"

        count = len(self.inference_history)
        total_time = sum(r['time'] for r in self.inference_history)
        total_tokens = sum(r['tokens'] for r in self.inference_history)
        avg_time = total_time / count
        avg_tokens = total_tokens / count
        avg_tps = total_tokens / total_time if total_time > 0 else 0

        stats = f"""
### 📈 推理性能统计
**总推理次数**: {count}
**总耗时**: {total_time:.2f}秒
**平均推理时间**: {avg_time:.2f}秒
**平均Token数**: {avg_tokens:.1f}
**平均速度**: {avg_tps:.1f} tokens/秒
**总Token数**: {total_tokens}
"""
        return stats

    def get_recent_activity(self):
        """获取最近活动"""
        if not self.inference_history:
            return "### 🕐 最近活动\n暂无数据"

        activity = "### 🕐 最近活动\n\n"
        recent = self.inference_history[-5:]  # 最近5次

        for i, record in enumerate(reversed(recent), 1):
            timestamp = record['timestamp'].split('T')[1].split('.')[0]
            prompt = record['prompt'][:25] + "..." if len(record['prompt']) > 25 else record['prompt']
            activity += f"**{i}. {timestamp}**\n"
            activity += f"   提示词: {prompt}\n"
            activity += f"   耗时: {record['time']:.2f}秒\n"
            activity += f"   Token: {record['tokens']} ({record['tps']:.1f} t/s)\n\n"

        return activity

    def chat(self, message, history, temperature, max_tokens):
        """聊天推理"""
        if not self.model_loaded:
            return "❌ 模型未加载", history

        try:
            # 构建对话历史
            messages = []
            for human, assistant in history:
                messages.append({"role": "user", "content": human})
                if assistant:
                    messages.append({"role": "assistant", "content": assistant})
            messages.append({"role": "user", "content": message})

            # 使用chat template
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # 编码输入
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt", padding=True).to(self.model.device)

            # 开始计时
            start_time = time.time()

            # 生成回复
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id
                )

            # 结束计时
            inference_time = time.time() - start_time

            # 解码输出
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            # 计算token数量（估算）
            tokens_generated = len(response) // 2  # 粗略估计
            tps = tokens_generated / inference_time if inference_time > 0 else 0

            # 记录推理历史
            self.inference_history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': message,
                'response': response,
                'time': inference_time,
                'tokens': tokens_generated,
                'tps': tps
            })

            return response, history + [[message, response]]

        except Exception as e:
            error_msg = f"推理出错: {str(e)}"
            return error_msg, history

def create_interface():
    """创建集成界面"""
    app = IntegratedApp()

    with gr.Blocks(title="AI推理优化学习平台") as demo:
        gr.Markdown("# 🎯 AI推理优化学习平台")
        gr.Markdown("**模型**: LLaMA-3.2-1B | **设备**: RTX 3070 | **学习**: 推理+监控")

        with gr.Row():
            # 左侧：聊天界面
            with gr.Column(scale=2):
                gr.Markdown("## 💬 模型对话")

                chatbot = gr.Chatbot(
                    label="对话历史",
                    height=350
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="输入消息",
                        placeholder="请输入您的问题...",
                        scale=4
                    )
                    send_btn = gr.Button("发送", scale=1, variant="primary")

                with gr.Accordion("生成参数", open=False):
                    temperature = gr.Slider(0.1, 2.0, value=0.7, step=0.1, label="温度")
                    max_tokens = gr.Slider(10, 300, value=100, step=10, label="最大长度")

                clear_btn = gr.Button("🗑️ 清除对话", size="sm")

            # 右侧：监控面板
            with gr.Column(scale=1):
                gr.Markdown("## 📊 实时监控")

                with gr.Tabs():
                    with gr.Tab("GPU"):
                        gpu_info = gr.Markdown("### 🖥️ GPU状态\n正在加载...")
                        refresh_gpu = gr.Button("🔄 刷新", size="sm")

                    with gr.Tab("性能"):
                        perf_info = gr.Markdown("### 📈 性能统计\n暂无数据")
                        refresh_perf = gr.Button("🔄 刷新", size="sm")

                    with gr.Tab("活动"):
                        activity_info = gr.Markdown("### 🕐 最近活动\n暂无数据")
                        refresh_activity = gr.Button("🔄 刷新", size="sm")

        # 事件处理
        def user_message(message, history):
            return "", history + [[message, None]]

        def bot_response(message, history, temperature, max_tokens):
            if not message or not history:
                return history

            # 获取最后一条用户消息
            last_message = history[-1][0] if history else message

            response, updated_history = app.chat(last_message, history[:-1], temperature, max_tokens)
            return updated_history

        msg.submit(
            user_message,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_response,
            [msg, chatbot, temperature, max_tokens],
            chatbot
 ).then(
            lambda: (app.get_performance_stats(), app.get_recent_activity()),
            outputs=[perf_info, activity_info]
        )

        send_btn.click(
            user_message,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_response,
            [msg, chatbot, temperature, max_tokens],
            chatbot
 ).then(
            lambda: (app.get_performance_stats(), app.get_recent_activity()),
            outputs=[perf_info, activity_info]
        )

        clear_btn.click(
            lambda: [],
            outputs=chatbot
        )

        refresh_gpu.click(
            app.get_gpu_info,
            outputs=gpu_info
        )

        refresh_perf.click(
            app.get_performance_stats,
            outputs=perf_info
        )

        refresh_activity.click(
            app.get_recent_activity,
            outputs=activity_info
        )

        # 初始加载
        demo.load(
            lambda: (app.get_gpu_info(), app.get_performance_stats(), app.get_recent_activity()),
            outputs=[gpu_info, perf_info, activity_info]
        )

    return demo

if __name__ == "__main__":
    print("🚀 启动AI推理优化学习平台...")
    print("📱 访问地址: http://127.0.0.1:7863")
    print("💡 提示: 在浏览器中打开上述地址即可使用")

    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True
    )