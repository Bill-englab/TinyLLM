"""
简化的Gradio测试应用
"""
import gradio as gr

def simple_chat(message, history):
    """简单的聊天函数"""
    return f"收到消息: {message}"

# 创建简化界面
with gr.Blocks() as demo:
    gr.Markdown("# Gradio测试应用")
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        if history and history[-1][1] is None:
            history[-1][1] = simple_chat(history[-1][0], history)
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    print("启动简化Gradio应用...")
    print("访问地址: http://127.0.0.1:7860")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )