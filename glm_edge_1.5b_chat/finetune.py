# 导入所需模块和库，包含用于加载模型、配置低秩适应（LoRA）参数、定义数据预处理等功能
import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq, 
    HfArgumentParser,
    TrainingArguments, 
    Trainer
)
from peft import LoraConfig, TaskType, get_peft_model
from arguments import ModelArguments, DataTrainingArguments, PeftArguments
from data_preprocess import InputOutputDataset

def main():
    # 使用 HfArgumentParser 解析命令行参数，并将参数解析成数据类对象：model_args（模型相关）、data_args（数据相关）、peft_args（LoRA参数）、training_args（训练配置）
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, PeftArguments, TrainingArguments))
    model_args, data_args, peft_args, training_args = parser.parse_args_into_dataclasses()

    # 加载预训练的生成式语言模型 (AutoModelForCausalLM) 和分词器 (AutoTokenizer)
    model = AutoModelForCausalLM.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)

    if peft_args.target_modules:
        peft_args.target_modules = peft_args.target_modules.split(",")
    else:
        peft_args.target_modules = ["q_proj", "k_proj", "v_proj"]
    
    # 设置LoRA的配置
    lora_config = LoraConfig(
        inference_mode=False,
        # 指定任务类型为生成语言模型 (TaskType.CAUSAL_LM)
        task_type=TaskType.CAUSAL_LM,
        # 指定了模型中应用 LoRA 的模块，如 q_proj、k_proj 和 v_proj
        target_modules=peft_args.target_modules,
        r=peft_args.lora_rank, 
        lora_alpha=peft_args.lora_alpha, 
        lora_dropout=peft_args.lora_dropout
    )
    # 将 LoRA 配置应用到模型中并移至 GPU
    model = get_peft_model(model, lora_config).to("cuda")
    # 输出模型中的可训练参数数量
    model.print_trainable_parameters()

    # 设置数据规整器用于在训练过程中对数据批量填充
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, 
        padding=True
    )

    # 如果启用了 do_train 标志，读取训练数据文件（JSONL 格式）并加载为列表格式，然后通过 InputOutputDataset 类预处理数据
    if training_args.do_train:
        with open(data_args.train_file, "r", encoding="utf-8") as f:
            train_data = [json.loads(line) for line in f]
        train_dataset = InputOutputDataset(train_data, tokenizer, data_args)
    # 如果启用了 do_eval 标志，类似地读取验证数据文件并加载为验证数据集
    if training_args.do_eval:
        with open(data_args.validation_file, "r", encoding="utf-8") as f:
            eval_data = [json.loads(line) for line in f]
        eval_dataset = InputOutputDataset(eval_data, tokenizer, data_args)

    # 实例化 Trainer 对象，用于训练和评估。传入模型、分词器、数据规整器、训练参数以及（如果启用训练或评估）数据集
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=data_collator,
        args=training_args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
    )

    # 启用梯度检查点来降低显存使用，并开启输入梯度需求，以便更高效的梯度计算
    if training_args.do_train:
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
        trainer.train()

    # 如果启用评估标志，调用 trainer.evaluate() 执行评估
    if training_args.do_eval:
        trainer.evaluate()

if __name__ == "__main__":
    main()
