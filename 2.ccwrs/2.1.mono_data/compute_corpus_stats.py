"""
Compute Avg. Length and Vocabulary Size for each monolingual corpus,
using the same mBERT WordPiece tokenizer already used elsewhere in the
CCWR pipeline (see tokenization_with_mbert.py). This keeps the numbers
comparable across languages regardless of each language's own word-
boundary conventions (e.g. Japanese/Chinese have no whitespace between
words; Burmese segmentation is itself an open problem).

Usage:
    python compute_corpus_stats.py

Expects files named data/mono/wiki_{lang}_cleaned_20k.txt for each
language code below. Adjust LANG_FILES to match your actual filenames
if they differ.
"""

from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

# Map: display name -> (language code used in your filenames, file path)
LANG_FILES = {
    "Burmese":    "data/mono/wiki_my_cleaned_20k.txt",
    "Vietnamese": "data/mono/wiki_vi_cleaned_20k.txt",
    "Japanese":   "data/mono/wiki_ja_cleaned_20k.txt",
    "Chinese":    "data/mono/wiki_zh_cleaned_20k.txt",
    "Turkish":    "data/mono/wiki_tr_cleaned_20k.txt",
    "Persian":    "data/mono/wiki_fa_cleaned_20k.txt",
}

print(f"{'Language':<12} {'#Sentences':>10} {'Avg. Length':>12} {'Vocab Size':>11}")
print("-" * 48)

for lang_name, path in LANG_FILES.items():
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{lang_name:<12} FILE NOT FOUND: {path}")
        continue

    total_tokens = 0
    vocab = set()

    for line in lines:
        tokens = tokenizer.tokenize(line)
        total_tokens += len(tokens)
        vocab.update(tokens)

    n_sentences = len(lines)
    avg_length = total_tokens / n_sentences if n_sentences else 0

    print(f"{lang_name:<12} {n_sentences:>10} {avg_length:>12.1f} {len(vocab):>11}")