#!/usr/bin/env python3

import re
import argparse


def clean_line(line):
    """
    Remove ALT sentence IDs like:
    SNT.80188.1<TAB>sentence
    """
    line = line.strip()

    # Remove leading sentence ID
    line = re.sub(r"^SNT\.\d+\.\d+\s+", "", line)

    return line.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Convert ALT parallel files into .tokens format"
    )

    parser.add_argument(
        "--src",
        required=True,
        help="Source language file (e.g. data_my.txt)"
    )

    parser.add_argument(
        "--trg",
        required=True,
        help="Target language file (e.g. data_vi.txt)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output .tokens file"
    )

    args = parser.parse_args()

    with open(args.src, "r", encoding="utf-8") as f_src, \
         open(args.trg, "r", encoding="utf-8") as f_trg, \
         open(args.output, "w", encoding="utf-8") as fout:

        src_lines = f_src.readlines()
        trg_lines = f_trg.readlines()

        assert len(src_lines) == len(trg_lines), \
            f"Line count mismatch: {len(src_lines)} vs {len(trg_lines)}"

        written = 0

        for src_line, trg_line in zip(src_lines, trg_lines):

            src_sent = clean_line(src_line)
            trg_sent = clean_line(trg_line)

            # Skip empty lines
            if not src_sent or not trg_sent:
                continue

            fout.write(f"{src_sent} ||| {trg_sent}\n")
            written += 1

    print(f"Saved to: {args.output}")
    print(f"Total sentence pairs: {written}")


if __name__ == "__main__":
    main()