from datasets import load_dataset

ds = load_dataset(
    "oscar",
    "unshuffled_deduplicated_vi",
    split="train"
)

with open("data/vietnamese_corpus.txt", "w", encoding="utf-8") as f:
    for x in ds:
        text = x.get("text", "").strip()
        if len(text) > 0:
            f.write(text.replace("\n", " ") + "\n")

