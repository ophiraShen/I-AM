#! /usr/bin/env bash

set -ex

# 基础配置
RUN_NAME=glm_edge_1.5b_chat
MODEL_PATH="/root/autodl-fs/modelscope"
CHECKPOINT_PATH="output/glm_edge_1.5b_chat-20241212-192015/checkpoint-450"
TEST_FILE="../data/val.jsonl"
LOG_DIR="eval_logs"

# 创建日志目录
mkdir -p $LOG_DIR

CUDA_VISIBLE_DEVICES=0 python evaluate.py \
    --model "${MODEL_PATH}" \
    --ckpt "${CHECKPOINT_PATH}" \
    --data "${TEST_FILE}" \
    2>&1 | tee ${LOG_DIR}/eval_results_$(date +%Y%m%d_%H%M%S).log