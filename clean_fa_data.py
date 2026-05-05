import re
import sys
import random
import unicodedata

# --------------------
# Input / Output
# --------------------
if len(sys.argv) != 3:
    print("Usage: python clean_fa_data.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# --------------------
# Settings
# --------------------
MIN_TOKENS = 4
MAX_TOKENS = 120

TARGET_SENTENCES = 20000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# --------------------
# Persian normalization
# --------------------
CHAR_MAP = {
    'ي': 'ی',
    'ك': 'ک',
    'ة': 'ه',
    'ۀ': 'ه',
}

DIACRITICS = re.compile(r'[\u064B-\u065F\u0670]')
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
HTML_PATTERN = re.compile(r'<.*?>')
MULTISPACE = re.compile(r'\s+')

def normalize_persian(text):
    text = unicodedata.normalize('NFKC', text)

    for src, tgt in CHAR_MAP.items():
        text = text.replace(src, tgt)

    text = DIACRITICS.sub('', text)

    return text

def clean_text(text):
    text = URL_PATTERN.sub(' ', text)
    text = HTML_PATTERN.sub(' ', text)

    text = normalize_persian(text)

    text = re.sub(
        r'[^0-9A-Za-z\u0600-\u06FF\s\.,!?؛،:%()\-\"]+',
        ' ',
        text
    )

    text = MULTISPACE.sub(' ', text).strip()

    return text

# --------------------
# Cleaning
# --------------------
cleaned_lines = []
seen = set()

with open(input_file, "r", encoding="utf-8") as fin:
    for line in fin:
        line = clean_text(line)

        tokens = line.split()

        if len(tokens) < MIN_TOKENS:
            continue

        if len(tokens) > MAX_TOKENS:
            continue

        if line in seen:
            continue

        seen.add(line)
        cleaned_lines.append(line)

# Random sampling
if len(cleaned_lines) > TARGET_SENTENCES:
    cleaned_lines = random.sample(
        cleaned_lines,
        TARGET_SENTENCES
    )

with open(output_file, "w", encoding="utf-8") as fout:
    for line in cleaned_lines:
        fout.write(line + "\n")

print(f"Saved {len(cleaned_lines)} cleaned sentences.")