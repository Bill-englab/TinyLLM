"""
稳定版聊天应用 - 修复历史记录问题
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

MODEL_PATH = "../../model/llama-3.2-1b-instruct/LLM-Research/Llama-3___2-1B-Instruct"

# 全局变量
model = None
tokenizer = None

def load_model():
    """加载模型"""
    global model, tokenizer
    if model is not None and tokenizer is not None:
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
    print("✅ 模型加载完成！")

def generate_response(message, history):
    """生成回复 - 修复历史记录处理"""
    global model, tokenizer

    # 加载模型
    if model is None or tokenizer is None:
        load_model()

    try:
        # 构建消息历史 - 修复解包问题
        messages = []
        for item in history:
            # 确保item是元组或列表，并且有2个元素
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                user_msg = item[0]
                bot_msg = item[1]

                if user_msg:  # 只有用户消息不为空才添加
                    messages.append({"role": "user", "content": user_msg})
                if bot_msg:  # 只有机器人回复不为空才添加
                    messages.append({"role": "assistant", "content": bot_msg})

        # 添加当前消息
        if message:
            messages.append({"role": "user", "content": message})

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
        print(f"生成回复时出错: {e}")
        import traceback
        traceback.print_exc()
        return f"错误: {str(e)}"

# 创建界面
demo = gr.ChatInterface(
    fn=generate_response,
    title="🤖 LLaMA-3.2-1B 聊天",
    description="支持多轮对话的AI助手"
)

print("🚀 启动稳定版聊天应用...")
print("📱 访问地址: http://127.0.0.1:7869")

demo.launch(
    server_name="127.0.0.1",
    server_port=7869,
    share=False
)