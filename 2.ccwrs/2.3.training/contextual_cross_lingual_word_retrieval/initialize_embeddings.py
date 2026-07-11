import torch
from transformers import AutoTokenizer, AutoModel

MODEL_PATH = "output/mbert_ne_extended_base"
MINED_FILE = "your_mined_pairs.txt"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModel.from_pretrained(MODEL_PATH)

embeddings = model.get_input_embeddings().weight.data

# Step 1: Build mapping dictionary
mapping = {}

with open(MINED_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(" ||| ")
        if len(parts) < 3:
            continue

        src_sent, trg_sent, aligns = parts[:3]

        src_tokens = src_sent.split()
        trg_tokens = trg_sent.split()

        for pair in aligns.split():
            try:
                i, j = map(int, pair.split("-"))
                src_tok = src_tokens[i]
                trg_tok = trg_tokens[j]

                # store first match only
                if src_tok not in mapping:
                    mapping[src_tok] = trg_tok
            except:
                continue

# Step 2: Transfer embeddings
count = 0

for my_token, aligned_token in mapping.items():
    if my_token in tokenizer.get_vocab() and aligned_token in tokenizer.get_vocab():
        my_id = tokenizer.convert_tokens_to_ids(my_token)
        aligned_id = tokenizer.convert_tokens_to_ids(aligned_token)

        embeddings[my_id] = embeddings[aligned_id]
        count += 1

print(f"Initialized {count} tokens")

# Save model
model.save_pretrained("output/mbert_initialized")
tokenizer.save_pretrained("output/mbert_initialized")