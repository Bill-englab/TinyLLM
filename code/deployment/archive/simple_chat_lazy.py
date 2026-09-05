"""
最简单的纯聊天应用 - 延迟加载版本
界面先启动，模型在第一次对话时加载
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

# 全局变量
model = None
tokenizer = None
model_loaded = False

def load_model():
    """延迟加载模型"""
    global model, tokenizer, model_loaded

    if model_loaded:
        return True

    try:
        print("开始加载模型...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )

        model_loaded = True
        print("✅ 模型加载完成！")
        return True
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False

def chat(message, history):
    """聊天函数"""
    global model, tokenizer, model_loaded

    # 第一次对话时加载模型
    if not model_loaded:
        if not load_model():
            return "模型加载失败，请检查控制台错误信息"

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
    gr.Markdown("第一次对话时会自动加载模型，请稍等...")

    chatbot = gr.Chatbot(label="对话")
    msg = gr.Textbox(label="输入", placeholder="请输入消息...")
    clear = gr.Button("清除")

    def user_message(message, history):
        return "", history + [[message, None]]

    def bot_message(history):
        if not history or not history[-1]:
            return history

        # 获取最后一条用户消息
        last_user_msg = history[-1][0]
        if not last_user_msg:
            return history

        # 获取历史记录（不包括当前正在处理的这条）
        chat_history = history[:-1]

        # 获取回复
        bot_response = chat(last_user_msg, chat_history)

        # 更新最后一条消息
        history[-1][1] = bot_response
        return history

    msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
        bot_message, chatbot, chatbot
    )

    clear.click(lambda: None, None, chatbot)

print("🚀 启动聊天应用...")
print("📱 访问地址: http://127.0.0.1:7865")
print("💡 提示: 第一次对话时会加载模型，需要等待1-2分钟")

demo.launch(
    server_name="127.0.0.1",
    server_port=7865,
    share=False
)