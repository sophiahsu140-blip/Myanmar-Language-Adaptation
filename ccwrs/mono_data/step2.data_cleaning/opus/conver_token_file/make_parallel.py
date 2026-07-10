import re
import sys

TARGET_SIZE = 20106

MIN_CHARS = 15
MAX_CHARS = 300

# =====================================================
# CLEANING
# =====================================================

def clean_text(text):

    text = text.strip()

    # remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =====================================================
# SUBTITLE NOISE DETECTION
# =====================================================

def is_subtitle_noise(text):

    text = text.strip()

    if not text:
        return True

    # music symbols
    if re.search(r'[♪♫♬♩]', text):
        return True

    # punctuation only
    if re.fullmatch(r'[\.\,\!\?\-–—…:;،۔ ]+', text):
        return True

    # (laughing), (music), (door opens), etc.
    if re.fullmatch(r'\([^)]{1,50}\)', text):
        return True

    # [laughing], [music], etc.
    if re.fullmatch(r'\[[^\]]{1,50}\]', text):
        return True

    return False


# =====================================================
# VALIDATION
# =====================================================

def valid_pair(src, tgt):

    if not src or not tgt:
        return False

    if is_subtitle_noise(src):
        return False

    if is_subtitle_noise(tgt):
        return False

    # character length filter
    if len(src) < MIN_CHARS:
        return False

    if len(tgt) < MIN_CHARS:
        return False

    if len(src) > MAX_CHARS:
        return False

    if len(tgt) > MAX_CHARS:
        return False

    # token ratio filter
    src_tokens = max(len(src.split()), 1)
    tgt_tokens = max(len(tgt.split()), 1)

    ratio = src_tokens / tgt_tokens

    if ratio > 4:
        return False

    if ratio < 0.25:
        return False

    return True


# =====================================================
# DEDUP
# =====================================================

def normalize(text):

    text = text.lower()

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =====================================================
# MAIN
# =====================================================

def create_parallel(src_file, tgt_file, output_file):

    seen = set()

    kept = 0
    total = 0

    with open(src_file, encoding="utf-8") as fs, \
         open(tgt_file, encoding="utf-8") as ft, \
         open(output_file, "w", encoding="utf-8") as out:

        for src, tgt in zip(fs, ft):

            total += 1

            src = clean_text(src)
            tgt = clean_text(tgt)

            if not valid_pair(src, tgt):
                continue

            key = normalize(src) + " ||| " + normalize(tgt)

            if key in seen:
                continue

            seen.add(key)

            out.write(f"{src} ||| {tgt}\n")

            kept += 1

            if kept >= TARGET_SIZE:
                break

    print("=" * 60)
    print(f"Pairs checked : {total}")
    print(f"Pairs saved   : {kept}")
    print(f"Output file   : {output_file}")
    print("=" * 60)


# =====================================================
# ENTRY
# =====================================================

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(
            "Usage:\n"
            "python make_parallel.py source.txt target.txt output.tokens"
        )
        sys.exit(1)

    create_parallel(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]
    )