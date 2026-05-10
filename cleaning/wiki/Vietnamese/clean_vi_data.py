import re
import random
import sys

# =========================================================
# VIETNAMESE WIKIPEDIA CLEANER
# =========================================================

MIN_TOKENS = 4
MAX_TOKENS = 120

TARGET_SENTENCES = 10000
RANDOM_SEED = 42

# =========================================================
# CLEANING
# =========================================================

def clean_line(line):

    line = line.strip()

    # Remove URLs
    line = re.sub(r'http\S+|www\S+', '', line)

    # Remove HTML/XML tags
    line = re.sub(r'<.*?>', '', line)

    # Remove empty brackets
    line = re.sub(r'\(\s*\)', ' ', line)

    # Keep Vietnamese characters, numbers, punctuation
    line = re.sub(
        r'[^A-Za-zÀ-ỹ0-9\s\.,!?()\-:;/%]',
        ' ',
        line
    )

    # Normalize repeated punctuation
    line = re.sub(r'([.!?]){2,}', r'\1', line)

    # Normalize spaces
    line = re.sub(r'\s+', ' ', line)

    return line.strip()

# =========================================================
# SENTENCE SPLITTING
# =========================================================

def split_sentences(text):

    raw_sentences = re.split(r'[.!?]+', text)

    sentences = []

    for sent in raw_sentences:

        sent = sent.strip()

        if sent:
            sentences.append(sent + ".")

    return sentences

# =========================================================
# VALIDATION
# =========================================================

def is_valid_sentence(sentence):

    sentence = sentence.strip()

    if not sentence:
        return False

    tokens = sentence.split()

    # Too short
    if len(tokens) < MIN_TOKENS:
        return False

    # Too long
    if len(tokens) > MAX_TOKENS:
        return False

    # Remove numeric-only lines
    if re.fullmatch(r'[0-9\s\.,]+', sentence):
        return False

    # Remove repetitive garbage
    if re.search(r'(.)\1{6,}', sentence):
        return False

    # Too many symbols
    symbol_count = len(
        re.findall(r'[^A-Za-zÀ-ỹ0-9\s\.,!?()%\-]', sentence)
    )

    if symbol_count / max(len(sentence), 1) > 0.20:
        return False

    return True

# =========================================================
# DEDUPLICATION
# =========================================================

def normalize_for_dedup(sentence):

    s = sentence.lower()

    # Remove punctuation
    s = re.sub(r'[^A-Za-zÀ-ỹ0-9\s]', '', s)

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

            # Split sentences
            sentences = split_sentences(line)

            for sent in sentences:

                sent = sent.strip()

                # Validate
                if not is_valid_sentence(sent):
                    continue

                # Deduplicate
                norm = normalize_for_dedup(sent)

                if norm in seen:
                    continue

                seen.add(norm)

                all_sentences.append(sent)

    # Shuffle
    random.seed(RANDOM_SEED)
    random.shuffle(all_sentences)

    # Sample
    sampled_sentences = all_sentences[:TARGET_SENTENCES]

    # Save
    with open(output_file, "w", encoding="utf-8") as outfile:

        for sentence in sampled_sentences:
            outfile.write(sentence + "\n")

    # Statistics
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
        print("python preprocess_vi.py input.txt output.txt")

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_file(input_path, output_path)