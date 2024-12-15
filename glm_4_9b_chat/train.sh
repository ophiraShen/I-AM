#! /usr/bin/env bash

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

# 使用 DeepSpeed 进行训练
accelerate launch \
    --config_file /root/autodl-tmp/I-AM/glm_4_9b_chat/default_config.yaml \
    train.py \
    --do_train \
    --do_eval \
    --train_file ../data/train.jsonl \
    --validation_file ../data/val.jsonl \
    --prompt_column input \
    --response_column output \
    --model_name_or_path "${MODEL_PATH}" \
    --output_dir $OUTPUT_DIR \
    --max_source_length 512 \
    --max_target_length 128 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --eval_strategy steps \
    --eval_steps 88 \
    --num_train_epochs 1 \
    --logging_steps 20 \
    --logging_dir $OUTPUT_DIR/logs \
    --save_steps 88 \
    --learning_rate $LR \
    --warmup_ratio 0.1 \
    --lora_rank 4 \
    --lora_alpha 16 \
    --lora_dropout 0.1 \
    --target_modules "query_key_value" \
    --weight_decay 0.01 \
    --logging_dir $OUTPUT_DIR/runs \
    --logging_strategy steps \
    --logging_steps 20 \
    --report_to tensorboard \
    --bf16 \
    2>&1 | tee ${OUTPUT_DIR}/train.log