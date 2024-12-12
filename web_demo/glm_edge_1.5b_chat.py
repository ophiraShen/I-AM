# web_demo/glm_edge_1.5b_chat.py

import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel

# 基础模型路径和 LoRA 模型路径
BASE_MODEL_PATH = "/root/autodl-fs/modelscope"  # 替换为你使用的基础模型路径
LORA_PATH = "/root/autodl-tmp/I-AM/glm_edge_1.5b_chat/output/glm_edge_1.5b_chat-20241212-192015/checkpoint-450"   # 替换为你的 LoRA 权重路径

# 加载tokenizer和基础模型
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH, 
    trust_remote_code=True,
    device_map='auto'
).half()

# 加载 LoRA 权重
model = PeftModel.from_pretrained(model, LORA_PATH)
model = model.eval()

def generate_response(prompt):
    with torch.no_grad():
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            input_ids=input_ids,
            max_length=2048,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

def chat(message, history):
    # 构建完整的对话上下文
    conversation = ""
    for human, assistant in history:
        conversation += f"Human: {human}\nAssistant: {assistant}\n"
    conversation += f"Human: {message}\nAssistant: "
    
    # 生成回复
    full_response = generate_response(conversation)
    
    # 只返回模型的最新回复（去掉之前的对话历史）
    current_response = full_response.split("Assistant: ")[-1].strip()
    
    return current_response

# 创建Gradio界面
demo = gr.ChatInterface(
    fn=chat,
    title="ChatGLM-LoRA 对话",
    description="这是一个经过 LoRA 微调的 ChatGLM 模型",
    examples=["你好，请介绍一下你自己", "你接受过什么训练？"],
    theme="soft"
)

# 启动服务
if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)