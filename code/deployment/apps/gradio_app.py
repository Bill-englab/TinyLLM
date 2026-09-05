"""
Gradio Web应用 - LLaMA模型部署
学习目标：模型部署基础
"""
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
import gradio as gr
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODEL_PATH = "../../model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

class ChatModel:
    def __init__(self):
        print("正在加载模型...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )

        # 设置pad_token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print("模型加载完成!")

    def generate_response(self, message, history, temperature, max_tokens, top_p):
        """
        生成回复
        Args:
            message: 用户输入
            history: 对话历史
            temperature: 温度参数
            max_tokens: 最大生成长度
            top_p: top_p采样参数
        """
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

        # 生成回复
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.pad_token_id
            )

        # 解码输出
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

        return response

# 全局模型实例
chat_model = None

def initialize_model():
    """初始化模型（延迟加载）"""
    global chat_model
    if chat_model is None:
        chat_model = ChatModel()
    return "模型已就绪！"

def chat_interface(message, history, temperature, max_tokens, top_p):
    """Gradio聊天接口"""
    if chat_model is None:
        initialize_model()

    try:
        response = chat_model.generate_response(message, history, temperature, max_tokens, top_p)
        return response
    except Exception as e:
        return f"生成出错: {str(e)}"

# 创建Gradio界面
def create_interface():
    with gr.Blocks(title="LLaMA-3.2-1B 聊天机器人") as demo:
        gr.Markdown("# 🤖 LLaMA-3.2-1B 聊天机器人")
        gr.Markdown("基于Gradio的模型部署学习项目")

        with gr.Row():
            with gr.Column(scale=3):
                # 聊天界面
                chatbot = gr.Chatbot(
                    label="对话历史",
                    height=400,
                    bubble_full_width=False
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="输入消息",
                        placeholder="请输入您的问题...",
                        scale=4
                    )
                    submit = gr.Button("发送", scale=1, variant="primary")

                # 参数控制
                with gr.Accordion("生成参数设置", open=False):
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="温度 (Temperature)",
                        info="越高输出越随机，越低输出越确定"
                    )
                    max_tokens = gr.Slider(
                        minimum=10,
                        maximum=500,
                        value=100,
                        step=10,
                        label="最大生成长度",
                        info="控制回复的最大长度"
                    )
                    top_p = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.9,
                        step=0.1,
                        label="Top-P 采样",
                        info="核采样参数"
                    )

            with gr.Column(scale=1):
                # 信息面板
                gr.Markdown("## 📊 系统信息")
                model_info = gr.Markdown("""
                **模型**: LLaMA-3.2-1B-Instruct
                **参数量**: 1.24B
                **精度**: FP16
                **设备**: GPU (RTX 3070)
                """)

                gr.Markdown("## 🎯 学习目标")
                gr.Markdown("""
                - ✅ 模型部署
                - ⏳ 监控系统
                - ⏳ 性能优化
                """)

                status = gr.Textbox(label="状态", value="点击初始化模型", interactive=False)
                init_btn = gr.Button("初始化模型", variant="secondary")

        # 事件处理
        def user_message(message, history):
            """处理用户消息"""
            return "", history + [[message, None]]

        def bot_response(history, temperature, max_tokens, top_p):
            """生成机器人回复"""
            if history and history[-1][1] is None:
                user_msg = history[-1][0]
                bot_msg = chat_interface(user_msg, history[:-1], temperature, max_tokens, top_p)
                history[-1][1] = bot_msg
            return history

        # 绑定事件
        init_btn.click(
            initialize_model,
            outputs=status
        )

        msg.submit(
            user_message,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        ).then(
            bot_response,
            inputs=[chatbot, temperature, max_tokens, top_p],
            outputs=chatbot
        )

        submit.click(
            user_message,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        ).then(
            bot_response,
            inputs=[chatbot, temperature, max_tokens, top_p],
            outputs=chatbot
        )

    return demo

if __name__ == "__main__":
    print("启动Gradio应用...")
    demo = create_interface()

    # 启动服务器
    demo.launch(
        server_name="127.0.0.1",  # 本地访问
        server_port=7860,         # 端口号
        share=False,              # 不创建公共链接
        inbrowser=False           # 不自动打开浏览器
    )