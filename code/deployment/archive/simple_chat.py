"""
最简单的纯聊天应用
只有一个功能：和模型对话
"""
import gradio as gr
import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODEL_PATH = "./model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

print("正在加载模型...")

# 加载模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

print("✅ 模型加载完成！")

def chat(message, history):
    """聊天函数"""
    try:
        # 构建对话历史
        messages = []
        for human, assistant in history:
            messages.append({"role": "user", "content": human})
            if assistant:
                messages.append({"role": "assistant", "content": assistant})
        messages.append({"role": "user", "content": message})

        # 使用chat template
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # 编码输入
        inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True).to(model.device)

        # 生成回复
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )

        # 解码输出
        response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

        return response
    except Exception as e:
        return f"出错了: {str(e)}"

# 创建最简单的界面
with gr.Blocks(title="LLaMA聊天") as demo:
    gr.Markdown("# 🤖 LLaMA-3.2-1B 聊天")

    chatbot = gr.Chatbot(label="对话")
    msg = gr.Textbox(label="输入", placeholder="请输入消息...")
    clear = gr.Button("清除")

    def user_message(message, history):
        return "", history + [[message, None]]

    def bot_message(message, history):
        if not message:
            return history

        bot_response = chat(message, history)
        history[-1][1] = bot_response
        return history

    msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
        bot_message, [msg, chatbot], chatbot
    )

    clear.click(lambda: None, None, chatbot)

print("🚀 启动聊天应用...")
print("📱 访问地址: http://127.0.0.1:7864")

demo.launch(
    server_name="127.0.0.1",
    server_port=7864,
    share=False
)