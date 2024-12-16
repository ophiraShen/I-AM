#! /usr/bin/env bash

# 设置环境变量
export CUDA_VISIBLE_DEVICES=0,1,2
export TORCH_DISTRIBUTED_DEBUG=INFO
export NCCL_DEBUG=INFO
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_LAUNCH_BLOCKING=1

set -ex

# 基础配置
LR=1e-4
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=soul_chat2
OUTPUT_DIR=output/${RUN_NAME}-${DATESTR}
mkdir -p $OUTPUT_DIR

# 模型路径
MODEL_PATH="/root/autodl-fs/modelscope/glm_4_9b_chat"

# DeepSpeed 训练启动命令
accelerate launch \
    --config_file /root/autodl-tmp/I-AM/glm_4_9b_chat/default_config.yaml \
    train.py \
    # 训练模式设置
    --do_train \
    --do_eval \
    --bf16 \

    # 数据配置
    --train_file ../data/train.jsonl \
    --validation_file ../data/val.jsonl \
    --prompt_column input \
    --response_column output \
    --max_source_length 1024 \
    --max_target_length 256 \

    # 模型配置
    --model_name_or_path "${MODEL_PATH}" \
    --output_dir $OUTPUT_DIR \

    # 训练超参数
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 8 \
    --gradient_accumulation_steps 4 \
    --learning_rate $LR \
    --num_train_epochs 3 \
    --weight_decay 0.01 \
    --warmup_ratio 0.1 \

    # LoRA 配置
    --lora_rank 4 \
    --lora_alpha 16 \
    --lora_dropout 0.1 \
    --target_modules "query_key_value" \

    # 检查点和评估策略
    --save_strategy "steps" \
    --save_steps 30 \
    --save_total_limit 3 \
    --eval_strategy steps \
    --eval_steps 20 \

    # 日志配置
    --logging_dir $OUTPUT_DIR/runs \
    --logging_strategy steps \
    --logging_steps 10 \
    --report_to tensorboard \
    2>&1 | tee ${OUTPUT_DIR}/train.log