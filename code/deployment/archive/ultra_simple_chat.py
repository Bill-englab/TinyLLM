"""
超简单聊天应用 - 使用Gradio Interface
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
    """加载模型"""
    global model, tokenizer, model_loaded
    if model_loaded:
        return

    print("正在加载模型...")
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

def generate_response(message):
    """生成回复"""
    global model, tokenizer, model_loaded

    # 加载模型
    if not model_loaded:
        load_model()

    try:
        # 构建消息
        messages = [{"role": "user", "content": message}]

        # 使用chat template
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # 编码
        inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

        # 生成
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

        # 解码
        response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response

    except Exception as e:
        return f"错误: {str(e)}"

# 创建最简单的Interface
iface = gr.Interface(
    fn=generate_response,
    inputs="text",
    outputs="text",
    title="🤖 LLaMA-3.2-1B 聊天",
    description="简单的AI聊天界面"
)

print("🚀 启动聊天应用...")
print("📱 访问地址: http://127.0.0.1:7866")

iface.launch(
    server_name="127.0.0.1",
    server_port=7866,
    share=False
)