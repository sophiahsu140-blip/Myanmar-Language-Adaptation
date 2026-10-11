#!/bin/bash

set -x

PYTHON="${PYTHON:-python}"

OUTPUT_DIR="output/raw_labse_my_tr"
#MODEL="bert-base-multilingual-cased"
MODEL="/storage/slurm/home/65070701701@cpe.kmutt.ac.th/hf/hub/models--sentence-transformers--LaBSE/snapshots/836121a0533e5664b21c7aacc5d22951f2b8b25b"


mkdir -p $OUTPUT_DIR

$PYTHON run_align.py \
    --data_mode mining \
    --model_name_or_path $MODEL \
    --dataset_config_name my-tr \
    --mining_language_pairs my-tr,tr-my \
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
