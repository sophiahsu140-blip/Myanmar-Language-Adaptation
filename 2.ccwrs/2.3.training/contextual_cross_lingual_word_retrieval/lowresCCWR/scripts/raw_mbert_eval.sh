#!/bin/bash

set -x

PYTHON="${PYTHON:-python}"

OUTPUT_DIR="output/raw_mbert_my_zh"
MODEL="bert-base-multilingual-cased"

mkdir -p $OUTPUT_DIR

$PYTHON run_align.py \
    --data_mode mining \
    --model_name_or_path $MODEL \
    --dataset_config_name my-zh \
    --mining_language_pairs my-zh,zh-my \
    --mining_dataset_dir data/mono \
    --mining_dataset_pattern_name "wiki_{}_cleaned_20k.txt" \
    --per_device_eval_batch_size 256 \
    --mining_src_batch_size 64 \
    --mining_trg_batch_size 64 \
    --output_dir $OUTPUT_DIR \
    --logging_dir $OUTPUT_DIR/log \
    --detailed_logging 0 \
    --do_eval \
    --do_test \
    --max_train_samples -1 \
    --max_eval_samples -1 \
    --max_mining_samples -1 \
    --src_mining_sample_per_step 500 \
    --trg_mining_sample_per_step 500 \
    --dataloader_num_workers 0 \
    --preprocessing_num_workers 2 \
    --do_mlm 0 \
    --src_mlm_weight 0.0 \
    --trg_mlm_weight 0.0 \
    --mining_threshold 0.2 \
    --mining_threshold_max 100.0 \
    --mining_k 1 \
    --mining_method forward \
    --align_method linear \
    --faiss_index_str none