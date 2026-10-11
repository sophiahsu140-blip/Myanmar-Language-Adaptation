#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <untokenized_file.txt>"
    exit 1
fi

set -x

PYTHON="${PYTHON:-python}"
INPUT_FILE=$1

OUTPUT_DIR='output'
BASE_MODEL_DIR=$OUTPUT_DIR/mbert_ne_extended_base
INIT_MODEL_DIR=$OUTPUT_DIR/mbert_initialized
MLM_MODEL_DIR=$OUTPUT_DIR/mbert_ne_extended

mkdir -p $OUTPUT_DIR

# =========================================================
# STEP 1: VOCABULARY EXTENSION (eBERT BASE STEP)
# =========================================================
echo "=== Step 1: Vocabulary Extension ==="

$PYTHON bert_vocabulary_extender.py \
    --model_path bert-base-multilingual-cased \
    --model_type bert \
    --train_data $INPUT_FILE \
    --vocab_size 10000 \
    --output $BASE_MODEL_DIR

echo "Vocabulary extension completed -> $BASE_MODEL_DIR"
