import re
import random
import sys
import unicodedata

# =========================================================
# CONFIGURATION
# =========================================================

MIN_TOKENS = 4
MAX_TOKENS = 120
TARGET_SENTENCES = 40000
RANDOM_SEED = 42

REMOVE_TEMPLATE_HEAVY = True

# =========================================================
# CLEANING FUNCTION
# =========================================================

def clean_line(line):

    # Unicode normalization
    line = unicodedata.normalize("NFKC", line)

    line = line.strip()

    # Remove URLs
    line = re.sub(r'http\S+|www\S+', '', line)

    # Remove HTML/XML tags
    line = re.sub(r'<.*?>', '', line)

    # Remove Wikipedia citations [1], [23]
    line = re.sub(r'\[\d+\]', '', line)

    # Remove empty brackets
    line = re.sub(r'[\(\[\{]\s*[\)\]\}]', ' ', line)

    # Remove weird symbols / malformed characters
    line = re.sub(
        r'[^\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uFF66-\uFF9F'
        r'0-9A-Za-z\s。、！？「」『』（）()\[\]\-:;%.,]',
        ' ',
        line
    )

    # Normalize repeated punctuation
    line = re.sub(r'([。！？!?]){2,}', r'\1', line)

    # Normalize spaces
    line = re.sub(r'\s+', ' ', line)

    return line.strip()


# =========================================================
# SENTENCE SEGMENTATION
# =========================================================

def split_sentences(text):

    # Japanese sentence splitting
    raw_sentences = re.split(r'(?<=[。！？!?])', text)

    sentences = []

    for sent in raw_sentences:

        sent = sent.strip()

        if sent:
            sentences.append(sent)

    return sentences


# =========================================================
# TEMPLATE DETECTION
# =========================================================

def is_template_heavy(sentence):

    template_patterns = [
        r'人口',
        r'面積',
        r'総務省',
        r'国勢調査',
        r'に位置する',
        r'都道府県',
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

    # Japanese token approximation
    tokens = re.findall(
        r'[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]+|[A-Za-z0-9]+',
        sentence
    )

    if len(tokens) < MIN_TOKENS:
        return False

    if len(tokens) > MAX_TOKENS:
        return False

    # Too many English words
    english_words = re.findall(r'\b[A-Za-z]{3,}\b', sentence)

    if len(english_words) > max(3, len(tokens) * 0.4):
        return False

    # Too many symbols
    symbol_count = len(re.findall(
        r'[^0-9A-Za-z'
        r'\u3040-\u30FF'
        r'\u3400-\u4DBF'
        r'\u4E00-\u9FFF'
        r'\s。、！？「」『』（）()]',
        sentence
    ))

    if symbol_count / max(len(sentence), 1) > 0.20:
        return False

    # Remove numeric-only lines
    if re.fullmatch(r'[0-9\s\.,]+', sentence):
        return False

    # Remove repetitive characters
    if re.search(r'(.)\1{6,}', sentence):
        return False

    # Remove template-heavy location/census data
    if REMOVE_TEMPLATE_HEAVY and is_template_heavy(sentence):
        return False

    return True


# =========================================================
# DEDUPLICATION
# =========================================================

def normalize_for_dedup(sentence):

    s = unicodedata.normalize("NFKC", sentence.lower())

    # Remove punctuation
    s = re.sub(
        r'[^\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF0-9a-z\s]',
        '',
        s
    )

    # Normalize spaces
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

            # Clean
            line = clean_line(line)

            if not line:
                continue

            # Segment
            sentences = split_sentences(line)

            for sent in sentences:

                sent = sent.strip()

                if not is_valid_sentence(sent):
                    continue

                # Deduplicate
                norm = normalize_for_dedup(sent)

                if norm in seen:
                    continue

                seen.add(norm)

                all_sentences.append(sent)

    # =====================================================
    # SHUFFLE
    # =====================================================

    random.seed(RANDOM_SEED)
    random.shuffle(all_sentences)

    # =====================================================
    # SAMPLE
    # =====================================================

    sampled_sentences = all_sentences[:TARGET_SENTENCES]

    # =====================================================
    # SAVE
    # =====================================================

    with open(output_file, "w", encoding="utf-8") as outfile:

        for sentence in sampled_sentences:
            outfile.write(sentence + "\n")

    # =====================================================
    # STATS
    # =====================================================

    print("=" * 50)
    print(f"Total lines read       : {total_lines}")
    print(f"Valid unique sentences : {len(all_sentences)}")
    print(f"Saved sentences        : {len(sampled_sentences)}")
    print(f"Output file            : {output_file}")
    print("=" * 50)


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("python preprocess_wiki_ja.py input.txt output.txt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_file(input_path, output_path)