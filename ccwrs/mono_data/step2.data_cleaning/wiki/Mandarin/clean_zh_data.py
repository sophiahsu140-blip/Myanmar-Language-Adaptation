import re
import random
import sys
import unicodedata

# =========================================================
# CONFIGURATION
# =========================================================

MIN_TOKENS = 4
MAX_TOKENS = 120
TARGET_SENTENCES = 20000
RANDOM_SEED = 42

REMOVE_TEMPLATE_HEAVY = True

# =========================================================
# CLEANING FUNCTION
# =========================================================

def clean_line(line):

    # Unicode normalization (important for Chinese full-width variants)
    line = unicodedata.normalize("NFKC", line)

    line = line.strip()

    # Remove URLs
    line = re.sub(r'http\S+|www\S+', '', line)

    # Remove HTML/XML tags
    line = re.sub(r'<.*?>', '', line)

    # Remove Wikipedia references [1], [23]
    line = re.sub(r'\[\d+\]', '', line)

    # Remove empty brackets
    line = re.sub(r'[\(\[\{]\s*[\)\]\}]', ' ', line)

    # Keep Chinese + English + numbers + basic punctuation
    line = re.sub(
        r'[^\u4E00-\u9FFF\u3400-\u4DBF'   # CJK Unified + Extension A
        r'0-9A-Za-z\s'
        r'。！？!?，、；：""''（）()\[\]{}\-:.,%]',
        ' ',
        line
    )

    # Normalize punctuation repetition
    line = re.sub(r'([。！？!?]){2,}', r'\1', line)

    # Normalize whitespace
    line = re.sub(r'\s+', ' ', line)

    return line.strip()


# =========================================================
# SENTENCE SEGMENTATION
# =========================================================

def split_sentences(text):

    # Chinese sentence boundaries
    raw_sentences = re.split(r'(?<=[。！？!?])', text)

    sentences = []

    for sent in raw_sentences:
        sent = sent.strip()
        if sent:
            sentences.append(sent)

    return sentences


# =========================================================
# TEMPLATE DETECTION (Wikipedia boilerplate filtering)
# =========================================================

def is_template_heavy(sentence):

    template_patterns = [
        r'位于',
        r'人口',
        r'面积',
        r'中华人民共和国',
        r'国家统计局',
        r'行政区划',
        r'根据.*年',
    ]

    hits = 0

    for p in template_patterns:
        if re.search(p, sentence):
            hits += 1

    return hits >= 3


# =========================================================
# VALIDATION
# =========================================================

def is_valid_sentence(sentence):

    sentence = sentence.strip()

    if not sentence:
        return False

    # Tokenization approximation for Chinese
    tokens = re.findall(
        r'[\u4E00-\u9FFF\u3400-\u4DBF]+|[A-Za-z0-9]+',
        sentence
    )

    if len(tokens) < MIN_TOKENS:
        return False

    if len(tokens) > MAX_TOKENS:
        return False

    # Too much English
    english_words = re.findall(r'\b[A-Za-z]{3,}\b', sentence)

    if len(english_words) > max(3, len(tokens) * 0.4):
        return False

    # Symbol ratio check
    symbol_count = len(re.findall(
        r'[^0-9A-Za-z\u4E00-\u9FFF\u3400-\u4DBF\s。！？，、；：()（）\-:.,%]',
        sentence
    ))

    if symbol_count / max(len(sentence), 1) > 0.20:
        return False

    # Numeric-only line removal
    if re.fullmatch(r'[0-9\s\.,]+', sentence):
        return False

    # Repeated character noise
    if re.search(r'(.)\1{6,}', sentence):
        return False

    # Template-heavy filtering
    if REMOVE_TEMPLATE_HEAVY and is_template_heavy(sentence):
        return False

    return True


# =========================================================
# DEDUPLICATION
# =========================================================

def normalize_for_dedup(sentence):

    s = unicodedata.normalize("NFKC", sentence.lower())

    # Remove punctuation
    s = re.sub(r'[^\u4E00-\u9FFF\u3400-\u4DBF0-9a-z\s]', '', s)

    # Normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    return s


# =========================================================
# MAIN PROCESS
# =========================================================

def process_file(input_file, output_file):

    all_sentences = []
    seen = set()

    total_lines = 0

    with open(input_file, "r", encoding="utf-8") as infile:

        for line in infile:

            total_lines += 1

            line = clean_line(line)

            if not line:
                continue

            sentences = split_sentences(line)

            for sent in sentences:

                sent = sent.strip()

                if not is_valid_sentence(sent):
                    continue

                norm = normalize_for_dedup(sent)

                if norm in seen:
                    continue

                seen.add(norm)
                all_sentences.append(sent)

    # Shuffle
    random.seed(RANDOM_SEED)
    random.shuffle(all_sentences)

    # Sample
    sampled = all_sentences[:TARGET_SENTENCES]

    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        for s in sampled:
            f.write(s + "\n")

    # Stats
    print("=" * 50)
    print(f"Total lines read       : {total_lines}")
    print(f"Valid unique sentences : {len(all_sentences)}")
    print(f"Saved sentences        : {len(sampled)}")
    print(f"Output file            : {output_file}")
    print("=" * 50)


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("python preprocess_wiki_zh.py input.txt output.txt")
        sys.exit(1)

    process_file(sys.argv[1], sys.argv[2])