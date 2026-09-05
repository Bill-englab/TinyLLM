"""快速Gradio测试"""
import gradio as gr
import time

def hello(name):
    return f"Hello {name}!"

iface = gr.Interface(fn=hello, inputs="text", outputs="text")
iface.launch(server_name="127.0.0.1", server_port=7861, share=False)

# 保持运行一段时间
time.sleep(5)
print("Gradio应用已在 http://127.0.0.1:7861 启动")