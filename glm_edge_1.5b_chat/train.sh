#! /usr/bin/env bash

set -ex

# 基础配置
LR=8e-5

DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=glm_edge_1.5b_chat
OUTPUT_DIR=output/${RUN_NAME}-${DATESTR}
mkdir -p $OUTPUT_DIR

# 模型路径
MODEL_PATH="/root/autodl-fs/modelscope/glm-large-1.5b-chat"

CUDA_VISIBLE_DEVICES=0 python finetune.py \
    --do_train \
    --do_eval \
    --train_file ../data/train.jsonl \
    --validation_file ../data/val.jsonl \
    --prompt_column input \
    --response_column output \
    --model_name_or_path "${MODEL_PATH}" \
    --output_dir $OUTPUT_DIR \
    --max_source_length 1024 \
    --max_target_length 256 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 8 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy steps \
    --eval_steps 90 \
    --num_train_epochs 5 \
    --logging_steps 10 \
    --logging_dir $OUTPUT_DIR/logs \
    --save_steps 90 \
    --learning_rate $LR \
    # --warmup_ratio 0.15 \
    --lora_rank 16 \
    --lora_alpha 64 \
    --lora_dropout 0.1 \
    --target_modules q_proj,k_proj,v_proj \
    --fp16 2>&1 | tee ${OUTPUT_DIR}/fp16.log
