#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Input mined pairs file"
    )

    parser.add_argument(
        "--output_dir",
        required=True,
        help="Output directory"
    )

    parser.add_argument(
        "--prefix",
        default="my-vi",
        help="Output prefix"
    )

    parser.add_argument(
        "--min_score",
        type=float,
        default=0.2,
        help="Minimum score threshold"
    )

    parser.add_argument(
        "--max_length",
        type=int,
        default=128,
        help="Maximum sentence token length"
    )

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    tokens_path = os.path.join(
        args.output_dir,
        f"{args.prefix}.tokens"
    )

    alignments_path = os.path.join(
        args.output_dir,
        f"{args.prefix}.alignments"
    )

    kept = 0
    skipped = 0
    malformed = 0
    empty_alignment = 0
    out_of_bounds = 0

    with open(args.input, "r", encoding="utf-8") as fin, \
         open(tokens_path, "w", encoding="utf-8") as ftok, \
         open(alignments_path, "w", encoding="utf-8") as falign:

        for line_num, line in enumerate(fin, 1):

            line = line.strip()

            if not line:
                skipped += 1
                continue

            parts = line.split(" ||| ")

            # expected:
            # src ||| trg ||| align ||| score
            if len(parts) != 4:
                skipped += 1
                malformed += 1
                continue

            src, trg, align, score = parts

            # parse score
            try:
                score = float(score)
            except:
                skipped += 1
                malformed += 1
                continue

            # score threshold
            if score < args.min_score:
                skipped += 1
                continue

            src_tokens = src.split()
            trg_tokens = trg.split()

            src_len = len(src_tokens)
            trg_len = len(trg_tokens)

            # sentence length filtering
            if src_len == 0 or trg_len == 0:
                skipped += 1
                continue

            if src_len > args.max_length or trg_len > args.max_length:
                skipped += 1
                continue

            # empty alignment
            if not align.strip():
                skipped += 1
                empty_alignment += 1
                continue

            clean_pairs = []

            seen_src = set()
            seen_trg = set()

            valid = True

            for pair in align.split():

                # must contain "-"
                if "-" not in pair:
                    valid = False
                    malformed += 1
                    break

                try:
                    s, t = pair.split("-")

                    s = int(s)
                    t = int(t)

                except:
                    valid = False
                    malformed += 1
                    break

                # non-negative
                if s < 0 or t < 0:
                    valid = False
                    out_of_bounds += 1
                    break

                # alignment must exist inside token range
                if s >= src_len or t >= trg_len:
                    valid = False
                    out_of_bounds += 1
                    break

                # enforce 1-to-1 alignment
                if s in seen_src:
                    continue

                if t in seen_trg:
                    continue

                seen_src.add(s)
                seen_trg.add(t)

                clean_pairs.append(f"{s}-{t}")

            # skip malformed examples
            if not valid:
                skipped += 1
                continue

            # skip if all alignments removed
            if len(clean_pairs) == 0:
                skipped += 1
                empty_alignment += 1
                continue

            # write sentence pair
            ftok.write(f"{src} ||| {trg}\n")

            # write cleaned alignments
            falign.write(" ".join(clean_pairs) + "\n")

            kept += 1

    print("Done.")
    print(f"Kept: {kept}")
    print(f"Skipped: {skipped}")
    print(f"Malformed: {malformed}")
    print(f"Empty alignments: {empty_alignment}")
    print(f"Out-of-bounds: {out_of_bounds}")
    print(f"Tokens file: {tokens_path}")
    print(f"Alignments file: {alignments_path}")


if __name__ == "__main__":
    main()