# 导入所需模块和库，包含用于加载模型、配置低秩适应（LoRA）参数、定义数据预处理等功能
import GPUtil
from datetime import datetime
import csv
import os
from threading import Thread
import time

import json
import gc
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq, 
    HfArgumentParser,
    TrainingArguments, 
    Trainer,
    set_seed,
    get_scheduler
)
from peft import LoraConfig, TaskType, get_peft_model
from arguments import ModelArguments, DataTrainingArguments, PeftArguments
from data_preprocess import InputOutputDataset
from accelerate import Accelerator
from accelerate.utils import DummyScheduler, DummyOptim, DeepSpeedPlugin
import deepspeed
from tqdm import tqdm


# 添加 GPU 监控类
class GPUMonitor:
    def __init__(self, log_dir="gpu_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"gpu_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        self.is_running = False
        
        # 创建CSV文件头
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'GPU ID', 'Memory Used (MB)', 
                           'Memory Total (MB)', 'GPU Load (%)', 'Temperature (°C)'])
    
    def _monitor(self):
        while self.is_running:
            try:
                gpus = GPUtil.getGPUs()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(self.log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    for gpu in gpus:
                        writer.writerow([
                            timestamp,
                            gpu.id,
                            gpu.memoryUsed,
                            gpu.memoryTotal,
                            gpu.load * 100,
                            gpu.temperature
                        ])
                        # 打印到控制台
                        print(f"\nGPU Stats at {timestamp}:")
                        print(f"GPU {gpu.id} - Memory Used: {gpu.memoryUsed}MB")
                        print(f"GPU Utilization: {gpu.load * 100:.2f}%")
                        print(f"Temperature: {gpu.temperature}°C")
                
                time.sleep(30)  # 每30秒记录一次
            except Exception as e:
                print(f"Error in GPU monitoring: {e}")
                
    def start(self):
        self.is_running = True
        self.monitor_thread = Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.is_running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)


def empty_cache():
    gc.collect()
    torch.cuda.empty_cache()

def main():
    # 使用 HfArgumentParser 解析命令行参数，并将参数解析成数据类对象：model_args（模型相关）、data_args（数据相关）、peft_args（LoRA参数）、training_args（训练配置）
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, PeftArguments, TrainingArguments))
    model_args, data_args, peft_args, training_args = parser.parse_args_into_dataclasses()

    # 初始化 Accelerator
    deepspeed_plugin = DeepSpeedPlugin(
        zero_stage=2,
        gradient_accumulation_steps=training_args.gradient_accumulation_steps
    )
    accelerator = Accelerator(
        gradient_accumulation_steps=training_args.gradient_accumulation_steps,
        deepspeed_plugin=deepspeed_plugin,
        mixed_precision="bf16"
    )
    accelerator.init_trackers("runs")

    set_seed(training_args.seed)

    empty_cache()  # 清空缓存
    
    # 加载预训练的生成式语言模型 (AutoModelForCausalLM) 和分词器 (AutoTokenizer)
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path, 
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path, 
        trust_remote_code=True
    )

    if peft_args.target_modules:
        peft_args.target_modules = peft_args.target_modules.split(",")
    else:
        peft_args.target_modules = ["q_proj", "k_proj", "v_proj"]
    
    # 设置LoRA的配置
    lora_config = LoraConfig(
        inference_mode=False,
        task_type=TaskType.CAUSAL_LM,
        target_modules=peft_args.target_modules,
        r=peft_args.lora_rank, 
        lora_alpha=peft_args.lora_alpha, 
        lora_dropout=peft_args.lora_dropout
    )


    empty_cache()  # 清空缓存
    # 将 LoRA 配置应用到模型中并移至 GPU
    model = get_peft_model(model, lora_config)
    # 输出模型中的可训练参数数量
    model.print_trainable_parameters()

    # 设置数据规整器用于在训练过程中对数据批量填充
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, 
        padding=True,
        pad_to_multiple_of=8
    )

    # 如果启用了 do_train 标志，读取训练数据文件（JSONL 格式）并加载为列表格式，然后通过 InputOutputDataset 类预处理数据
    if training_args.do_train:
        with open(data_args.train_file, "r", encoding="utf-8") as f:
            train_data = [json.loads(line) for line in f]
        train_dataset = InputOutputDataset(train_data, tokenizer, data_args)
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=training_args.per_device_train_batch_size,
            collate_fn=data_collator,
            shuffle=True,
            pin_memory=True,
            num_workers=8,
            persistent_workers=True
        )

    # 如果启用了 do_eval 标志，类似地读取验证数据文件并加载为验证数据集
    if training_args.do_eval:
        with open(data_args.validation_file, "r", encoding="utf-8") as f:
            eval_data = [json.loads(line) for line in f]
        eval_dataset = InputOutputDataset(eval_data, tokenizer, data_args)
        eval_dataloader = DataLoader(
            eval_dataset,                                                       
            batch_size=training_args.per_device_eval_batch_size,
            collate_fn=data_collator,
        )                            

    # 优化器设置
    optimizer = Adam(model.parameters(), lr=training_args.learning_rate)
    lr_scheduler = torch.optim.lr_scheduler.LinearLR(optimizer)

    # 使用 Accelerator 准备所有组件
    model, optimizer, train_dataloader, eval_dataloader, lr_scheduler = accelerator.prepare(
        model, optimizer, train_dataloader, eval_dataloader, lr_scheduler
    )

    # 启用梯度检查点
    # 启用梯度检查点
    if training_args.gradient_checkpointing:
        if hasattr(model.module, "gradient_checkpointing_enable"):
            model.module.gradient_checkpointing_enable()
        elif hasattr(model.module, "enable_gradient_checkpointing"):
            model.module.enable_gradient_checkpointing()
        
        if hasattr(model.module, "enable_input_require_grads"):
            model.module.enable_input_require_grads()


    gpu_monitor = GPUMonitor()
    gpu_monitor.start()

    try:
        # 训练循环
        if training_args.do_train:
            model.train()
            total_steps = len(train_dataloader) * training_args.num_train_epochs
            progress_bar = tqdm(range(int(total_steps)), desc="Training")

            for epoch in range(int(training_args.num_train_epochs)):
                for step, batch in enumerate(train_dataloader):
                    outputs = model(**batch)
                    loss = outputs.loss
                    accelerator.backward(loss)

                    if step % training_args.gradient_accumulation_steps == 0:
                        optimizer.step()
                        lr_scheduler.step()
                        optimizer.zero_grad()
                        empty_cache()  # 清空缓存
                    
                    if step % training_args.logging_steps == 0:
                        empty_cache()  # 清空缓存

                    progress_bar.update(1)

                    if training_args.logging_steps > 0 and step % training_args.logging_steps == 0:
                        accelerator.print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")

        
        # 评估
        if training_args.do_eval:
            empty_cache()  # 清空缓存
            model.eval()
            eval_loss = 0
            eval_steps = 0

            for batch in eval_dataloader:
                with torch.no_grad():
                    outputs = model(**batch)
                    eval_loss += outputs.loss.item()
                    eval_steps += 1

            eval_loss /= eval_steps
            accelerator.print(f"Eval Loss: {eval_loss:.4f}")
    
    finally:
        gpu_monitor.stop()

    
    # 保存模型
    if training_args.output_dir is not None:
        empty_cache()  # 清空缓存
        accelerator.wait_for_everyone()
        unwrapped_model = accelerator.unwrap_model(model)
        unwrapped_model.save_pretrained(
            training_args.output_dir,
            is_main_process=accelerator.is_main_process,
            save_function=accelerator.save,
            save_peft=True,
            save_model_only=True
        )
    

if __name__ == "__main__":
    main()
