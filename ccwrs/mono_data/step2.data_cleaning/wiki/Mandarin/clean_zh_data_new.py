import re
import random
import sys
import unicodedata

# =========================================================
# CONFIGURATION
# =========================================================

MIN_CHARS = 8
MAX_CHARS = 200

TARGET_SENTENCES = 20000
RANDOM_SEED = 42

REMOVE_TEMPLATE_HEAVY = True
REMOVE_NEWSWIRE = True

# =========================================================
# SPAM / AD PATTERNS
# =========================================================

SPAM_PATTERNS = [
    r'招财带什么佛牌',
    r'佛牌绳哪里有卖',
    r'卍.*?卍',
]

AD_WORDS = [
    "优惠",
    "现车",
    "购车",
    "详询",
    "热线",
    "致电",
    "电话",
    "报价",
    "促销",
    "经销商",
    "4S店",
    "价格",
    "销售",
]

NEWS_PATTERNS = [
    r'新华社',
    r'中新网',
    r'人民网',
    r'本报讯',
    r'记者',
    r'日电',
]

# =========================================================
# CLEANING FUNCTION
# =========================================================

def clean_line(line):

    line = unicodedata.normalize("NFKC", line)

    line = line.strip()

    # Remove URLs
    line = re.sub(r'https?://\S+', ' ', line)
    line = re.sub(r'www\.\S+', ' ', line)

    # Remove HTML/XML tags
    line = re.sub(r'<.*?>', ' ', line)

    # Remove wiki references
    line = re.sub(r'\[\d+\]', ' ', line)

    # Remove empty brackets
    line = re.sub(r'[\(\[\{]\s*[\)\]\}]', ' ', line)

    # Remove known spam patterns
    for pattern in SPAM_PATTERNS:
        line = re.sub(pattern, ' ', line)

    # Keep Chinese + English + digits + common punctuation
    line = re.sub(
        r'[^\u4E00-\u9FFF\u3400-\u4DBF'
        r'0-9A-Za-z\s'
        r'。！？!?，、；：""''（）()\[\]{}\-:.,%]',
        ' ',
        line
    )

    # Normalize repeated punctuation
    line = re.sub(r'([。！？!?]){2,}', r'\1', line)

    # Normalize spaces
    line = re.sub(r'\s+', ' ', line)

    return line.strip()

# =========================================================
# SENTENCE SPLITTING
# =========================================================

def split_sentences(text):

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

    patterns = [
        r'位于',
        r'人口',
        r'面积',
        r'中华人民共和国',
        r'国家统计局',
        r'行政区划',
        r'根据.*年',
    ]

    hits = 0

    for p in patterns:
        if re.search(p, sentence):
            hits += 1

    return hits >= 3

# =========================================================
# VALIDATION
# =========================================================

def is_valid_sentence(sentence, stats=None):

    sentence = sentence.strip()

    if not sentence:
        if stats:
            stats["empty"] += 1
        return False

    chinese_chars = re.findall(
        r'[\u4E00-\u9FFF\u3400-\u4DBF]',
        sentence
    )

    num_chars = len(chinese_chars)

    if num_chars < MIN_CHARS:
        if stats:
            stats["short"] += 1
        return False

    if num_chars > MAX_CHARS:
        if stats:
            stats["long"] += 1
        return False

    # Chinese ratio
    if len(sentence) > 0:
        zh_ratio = num_chars / len(sentence)

        if zh_ratio < 0.60:
            if stats:
                stats["low_chinese_ratio"] += 1
            return False

    # Too much English
    english_words = re.findall(
        r'\b[A-Za-z]{3,}\b',
        sentence
    )

    if len(english_words) > 10:
        if stats:
            stats["english"] += 1
        return False

    # Excessive symbols
    symbol_count = len(
        re.findall(
            r'[^0-9A-Za-z\u4E00-\u9FFF\u3400-\u4DBF\s。！？，、；：()（）\-:.,%]',
            sentence
        )
    )

    if symbol_count / max(len(sentence), 1) > 0.20:
        if stats:
            stats["symbols"] += 1
        return False

    # Numeric only
    if re.fullmatch(r'[0-9\s\.,]+', sentence):
        if stats:
            stats["numeric"] += 1
        return False

    # Long phone numbers
    if re.search(r'\d{7,}', sentence):
        if stats:
            stats["phone"] += 1
        return False

    # Domain remnants
    if re.search(
        r'\.(com|net|org|cn|hk|tw)',
        sentence,
        flags=re.IGNORECASE
    ):
        if stats:
            stats["domain"] += 1
        return False

    # Repeated chars
    if re.search(r'(.)\1{6,}', sentence):
        if stats:
            stats["repeated"] += 1
        return False

    # Advertisement filtering
    ad_hits = sum(
        1 for word in AD_WORDS
        if word in sentence
    )

    if ad_hits >= 2:
        if stats:
            stats["advertisement"] += 1
        return False

    # Newswire filtering
    if REMOVE_NEWSWIRE:

        news_hits = sum(
            1 for p in NEWS_PATTERNS
            if re.search(p, sentence)
        )

        if news_hits >= 2:
            if stats:
                stats["newswire"] += 1
            return False

    # Template-heavy
    if REMOVE_TEMPLATE_HEAVY and is_template_heavy(sentence):
        if stats:
            stats["template"] += 1
        return False

    return True

# =========================================================
# DEDUPLICATION
# =========================================================

def normalize_for_dedup(sentence):

    s = unicodedata.normalize(
        "NFKC",
        sentence.lower()
    )

    s = re.sub(
        r'[^\u4E00-\u9FFF\u3400-\u4DBF0-9a-z\s]',
        '',
        s
    )

    s = re.sub(r'\s+', ' ', s)

    return s.strip()

# =========================================================
# MAIN
# =========================================================

def process_file(input_file, output_file):

    all_sentences = []
    seen = set()

    stats = {
        "empty": 0,
        "short": 0,
        "long": 0,
        "english": 0,
        "symbols": 0,
        "numeric": 0,
        "phone": 0,
        "domain": 0,
        "repeated": 0,
        "template": 0,
        "advertisement": 0,
        "newswire": 0,
        "low_chinese_ratio": 0,
        "duplicate": 0,
        "kept": 0,
    }

    total_lines = 0

    with open(input_file, "r", encoding="utf-8") as infile:

        for line in infile:

            total_lines += 1

            line = clean_line(line)

            if not line:
                continue

            sentences = split_sentences(line)

            for sent in sentences:

                if not is_valid_sentence(sent, stats):
                    continue

                norm = normalize_for_dedup(sent)

                if norm in seen:
                    stats["duplicate"] += 1
                    continue

                seen.add(norm)

                all_sentences.append(sent)

                stats["kept"] += 1

    random.seed(RANDOM_SEED)
    random.shuffle(all_sentences)

    sampled = all_sentences[:TARGET_SENTENCES]

    with open(output_file, "w", encoding="utf-8") as outfile:

        for sent in sampled:
            outfile.write(sent + "\n")

    print("=" * 60)
    print(f"Total lines read       : {total_lines}")
    print(f"Valid unique sentences : {len(all_sentences)}")
    print(f"Saved sentences        : {len(sampled)}")
    print(f"Output file            : {output_file}")
    print("=" * 60)

    print("\nFiltering statistics")
    print("=" * 60)

    for k, v in stats.items():
        print(f"{k:20s}: {v}")

    print("=" * 60)

# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "python preprocess_wiki_zh.py input.txt output.txt"
        )
        sys.exit(1)

    process_file(
        sys.argv[1],
        sys.argv[2]
    )