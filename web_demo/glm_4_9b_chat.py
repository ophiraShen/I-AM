# web_demo/glm_edge_1.5b_chat.py

import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel

device = "cuda"

# 基础模型路径和 LoRA 模型路径
BASE_MODEL_PATH = "/root/autodl-fs/modelscope/glm_4_9b_chat"  # 替换为你使用的基础模型路径
LORA_PATH = "/root/autodl-tmp/I-AM/models/glm_4_9b_chat/output/i_am-20241217-013701/lora"

# 加载tokenizer和基础模型
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH, 
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
)

# 加载 LoRA 权重
model = PeftModel.from_pretrained(model, LORA_PATH)
model = model.to(device).eval()

gen_kwargs = {"max_length": 1024, "do_sample": True, "top_k": 1}

def generate_response(messages):
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True
        )
        inputs = inputs.to(device)
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

def chat(message, history):
    # 将历史对话和当前消息转换为模型期望的格式
    messages = [
        {
            "role": "system",
            "content": "你是一个熟悉吸引力法则和显化法则的咨询师，请根据用户的问题给出专业的回答。"
        }
    ]
    
    # 添加历史对话
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": message})
    
    # 生成回复
    response = generate_response(messages)
    
    return response

# 创建Gradio界面
demo = gr.ChatInterface(
    fn=chat,
    title="ChatGLM-LoRA 对话",
    description="这是一个经过 LoRA 微调的 ChatGLM 模型",
    examples=["你好，请介绍一下你自己", "你接受过什么训练？"],
    theme="soft",
)

# 启动服务
if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)