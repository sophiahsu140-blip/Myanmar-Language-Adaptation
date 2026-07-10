
#!/usr/bin/env python3

import argparse
import torch
from simalign import SentenceAligner

device = "cuda" if torch.cuda.is_available() else "cpu"


def main():
    parser = argparse.ArgumentParser(
        description="Generate word alignments using SimAlign"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input .tokens file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output .alignments file"
    )

    parser.add_argument(
        "--model",
        default="bert",
        help="Embedding model: bert, mbert, xlm-roberta"
    )

    args = parser.parse_args()

    aligner = SentenceAligner(
    model=args.model,
    token_type="bpe",
    matching_methods=["i"],
    device=device,
    )

    total = 0

    with open(args.input, "r", encoding="utf-8") as fin, \
         open(args.output, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()

            if not line:
                fout.write("\n")
                continue

            if "|||" not in line:
                print(f"Skipping malformed line: {line}")
                continue

            src_sent, trg_sent = line.split("|||", 1)

            src_sent = src_sent.strip()
            trg_sent = trg_sent.strip()

            src_words = src_sent.split()
            trg_words = trg_sent.split()

            try:
                alignments = aligner.get_word_aligns(
                    src_words,
                    trg_words
                )

                # Print available alignment methods once
                if total == 0:
                    print("Available alignment methods:", alignments.keys())

                # Use itermax (recommended)
                pairs = alignments["itermax"]

                # Sort alignments
                pairs = sorted(list(pairs))

                alignment_str = " ".join(
                    f"{src_idx}-{trg_idx}"
                    for src_idx, trg_idx in pairs
                )

                fout.write(alignment_str + "\n")
                total += 1

            except Exception as e:
                print(f"Error on line {total}: {e}")
                fout.write("\n")

    print(f"Saved alignments to: {args.output}")
    print(f"Processed sentence pairs: {total}")


if __name__ == "__main__":
    main()