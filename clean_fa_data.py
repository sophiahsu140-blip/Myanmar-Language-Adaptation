#python data/clean_fa_data.py data/mono/wiki_fa_clean.txt data/mono/wiki_fa_cleaned_20k_v4.txt
# 
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

BAD_PATTERNS = [
    "۰ نظر",
    "خبرگزاری",
    "ب.ظ",
    "ق.ظ",
]

SPAM_PATTERNS = [
    "ارائه خدمات",
    "نمونه کار رایگان",
    "در کنار شما",
    "آماده ارائه خدمات",
    "پیشنهاد می کنیم",
]

def normalize_persian(text):
    text = unicodedata.normalize('NFKC', text)

    text = text.replace('\u200c', ' ')
    text = text.replace('\u200f', '')
    text = text.replace('\u200e', '')

    for src, tgt in CHAR_MAP.items():
        text = text.replace(src, tgt)

    text = DIACRITICS.sub('', text)

    return text

def clean_text(text):
    # Remove URLs and HTML
    text = URL_PATTERN.sub(' ', text)
    text = HTML_PATTERN.sub(' ', text)

    # Normalize Persian text
    text = normalize_persian(text)

    # Keep Persian chars, English chars, digits, punctuation
    text = re.sub(
        r'[^0-9A-Za-z\u0600-\u06FF\s\.,!?؛،:%()\-\"]+',
        ' ',
        text
    )

    # Normalize spaces
    text = MULTISPACE.sub(' ', text).strip()

    return text

def is_low_quality(line):
    tokens = line.split()

    # Too many English tokens
    english_tokens = sum(
        1 for t in tokens
        if re.search(r'[A-Za-z]', t)
    )

    if english_tokens > len(tokens) * 0.3:
        return True

    # Repeated strange words
    strange_patterns = [
        "دانلود آهنگ",
        "تولدت مبارک",
        "Music",
    ]

    if any(p in line for p in strange_patterns):
        return True

    # Excessive punctuation/digits
    bad_chars = sum(
        1 for c in line
        if c.isdigit() or c in "[]{}|"
    )

    if bad_chars > len(line) * 0.2:
        return True

    return False

# --------------------
# Cleaning
# --------------------
cleaned_lines = []
seen = set()

with open(input_file, "r", encoding="utf-8") as fin:
    for line in fin:
        line = clean_text(line)

        # Skip empty lines
        if not line:
            continue

        # Remove metadata/news patterns
        if any(p in line for p in BAD_PATTERNS):
            continue

        if any(p in line for p in SPAM_PATTERNS):
            continue

        if is_low_quality(line):
            continue

        # Remove lines with too many digits
        digit_count = sum(c.isdigit() for c in line)

        if digit_count > 10:
            continue

        tokens = line.split()

        # Length filtering
        if len(tokens) < MIN_TOKENS:
            continue

        if len(tokens) > MAX_TOKENS:
            continue

        # Deduplication
        if line in seen:
            continue

        seen.add(line)
        cleaned_lines.append(line)

# --------------------
# Random sampling
# --------------------
if len(cleaned_lines) > TARGET_SENTENCES:
    cleaned_lines = random.sample(
        cleaned_lines,
        TARGET_SENTENCES
    )

# --------------------
# Save output
# --------------------
with open(output_file, "w", encoding="utf-8") as fout:
    for line in cleaned_lines:
        fout.write(line + "\n")

print(f"Saved {len(cleaned_lines)} cleaned sentences.")