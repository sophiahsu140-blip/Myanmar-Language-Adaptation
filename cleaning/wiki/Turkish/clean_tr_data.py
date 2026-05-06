# preprocess_turkish.py

import re
import random
import sys

# =========================================================
# CONFIGURATION
# =========================================================

MIN_TOKENS = 4
MAX_TOKENS = 120
TARGET_SENTENCES = 20000
RANDOM_SEED = 42

# Remove repetitive Wikipedia/template-heavy sentences
REMOVE_TEMPLATE_HEAVY = True

# =========================================================
# CLEANING FUNCTION
# =========================================================

def clean_line(line):

    line = line.strip()

    # -----------------------------------------------------
    # Remove URLs and domains
    # -----------------------------------------------------

    line = re.sub(
        r'http\S+|www\S+|\S+\.com|\S+\.net|\S+\.org',
        '',
        line
    )

    # -----------------------------------------------------
    # Remove HTML/XML tags
    # -----------------------------------------------------

    line = re.sub(r'<.*?>', '', line)

    # -----------------------------------------------------
    # Remove empty brackets
    # -----------------------------------------------------

    line = re.sub(r'\(\s*\)', ' ', line)

    # -----------------------------------------------------
    # Remove forum emojis/styles
    # Example: :iyi:
    # -----------------------------------------------------

    line = re.sub(r':\w+:', ' ', line)

    # -----------------------------------------------------
    # Remove Wikipedia references
    # Example: [1]
    # -----------------------------------------------------

    line = re.sub(r'\[\d+\]', ' ', line)

    # -----------------------------------------------------
    # Remove metadata patterns
    # -----------------------------------------------------

    metadata_patterns = [
        r'Boyut:',
        r'Boyutu:',
        r'Telif:',
        r'Hit:',
        r'KB',
        r'MB',
        r'Download',
        r'İndir',
    ]

    for p in metadata_patterns:
        line = re.sub(p, ' ', line, flags=re.IGNORECASE)

    # -----------------------------------------------------
    # Normalize malformed Turkish suffix spacing
    # Example:
    # Türkiye ye -> Türkiye'ye
    # -----------------------------------------------------

    line = re.sub(
        r'\b([A-ZÇĞİÖŞÜa-zçğıöşü]+)\s+(ye|ya|de|da|den|dan)\b',
        r"\1'\2",
        line
    )

    # -----------------------------------------------------
    # Remove weird symbols
    # Preserve Turkish characters
    # -----------------------------------------------------

    line = re.sub(
        r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s\.,!?()\-:;/%\'"]',
        ' ',
        line
    )

    # -----------------------------------------------------
    # Normalize repeated punctuation
    # -----------------------------------------------------

    line = re.sub(r'([.!?,]){2,}', r'\1', line)

    # -----------------------------------------------------
    # Normalize spaces
    # -----------------------------------------------------

    line = re.sub(r'\s+', ' ', line)

    return line.strip()


# =========================================================
# SENTENCE SEGMENTATION
# =========================================================

def split_sentences(text):

    raw_sentences = re.split(r'(?<=[.!?])\s+', text)

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

        # Wikipedia/location style
        r'nüfusu',
        r'ilçesine bağlıdır',
        r'köyüdür',
        r'belediyesi',
        r'Türkiye İstatistik Kurumu',
        r'yer almaktadır',
        r'ilinde bulunmaktadır',

        # spam/metadata style
        r'Boyut',
        r'Telif',
        r'Hit',
    ]

    hits = 0

    for p in template_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            hits += 1

    return hits >= 3


# =========================================================
# VALIDATION
# =========================================================

def is_valid_sentence(sentence):

    sentence = sentence.strip()

    if not sentence:
        return False

    # -----------------------------------------------------
    # Token count
    # -----------------------------------------------------

    tokens = sentence.split()

    if len(tokens) < MIN_TOKENS:
        return False

    if len(tokens) > MAX_TOKENS:
        return False

    # -----------------------------------------------------
    # Extremely long sentence
    # -----------------------------------------------------

    if len(sentence) > 400:
        return False

    # -----------------------------------------------------
    # Too many numbers
    # -----------------------------------------------------

    numbers = re.findall(r'\d+', sentence)

    if len(numbers) > max(5, len(tokens) * 0.4):
        return False

    # -----------------------------------------------------
    # Spam / SEO patterns
    # -----------------------------------------------------

    spam_patterns = [

        r'para kazan',
        r'site site gezdim',
        r'download',
        r'tıkla',
        r'reklam',
        r'üyelik',
        r'bedava',
        r'hemen indir',
    ]

    for p in spam_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Product / ecommerce patterns
    # -----------------------------------------------------

    product_patterns = [

        r'kılıf',
        r'silikon kapak',
        r'desenli',
        r'iphone',
        r'samsung',
        r'huawei',
        r'xiaomi',
        r'\(\d+\)$',
    ]

    for p in product_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Gambling / betting patterns
    # -----------------------------------------------------

    betting_patterns = [

        r'bahis',
        r'kupon',
        r'canlı sunum',
        r'casino',
        r'jackpot',
        r'bonus',
    ]

    for p in betting_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Metadata-heavy lines
    # -----------------------------------------------------

    metadata_hits = 0

    metadata_patterns = [

        r'Boyut',
        r'Telif',
        r'Hit',
        r'KB',
        r'MB',
    ]

    for p in metadata_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            metadata_hits += 1

    if metadata_hits >= 2:
        return False

    # -----------------------------------------------------
    # Excessive uppercase ratio
    # -----------------------------------------------------

    uppercase_chars = sum(1 for c in sentence if c.isupper())

    if uppercase_chars / max(len(sentence), 1) > 0.35:
        return False

    # -----------------------------------------------------
    # Extremely long bureaucratic phrases
    # -----------------------------------------------------

    if len(tokens) > 40 and uppercase_chars > 30:
        return False

    # -----------------------------------------------------
    # Too many ALL-CAPS words
    # -----------------------------------------------------

    all_caps_words = re.findall(
        r'\b[A-ZÇĞİÖŞÜ]{4,}\b',
        sentence
    )

    if len(all_caps_words) >= 4:
        return False

    # -----------------------------------------------------
    # OCR corruption detection
    # -----------------------------------------------------

    weird_fragments = [

        r'mahl k',
        r'\bk d r\b',
        r'\ba m l\b',
    ]

    for p in weird_fragments:

        if re.search(p, sentence, re.IGNORECASE):
            return False
        
    # -----------------------------------------------------

    # OCR corruption
    # -----------------------------------------------------

    ocr_patterns = [

        r'\bhuz\s+r\b',
        r'\bkg\s*/\s*cm\b',
    ]

    for p in ocr_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False


    # -----------------------------------------------------
    # Emoticons / social emoji text
    # -----------------------------------------------------

    if re.search(r'[:;=8][-~]?[)\](DPp]', sentence):
        return False


    # -----------------------------------------------------
    # Broken medical/forum formatting
    # Example:
    # ( /- 2 gün sapabilir)
    # -----------------------------------------------------

    if re.search(r'\(/\-\s*\d+', sentence):
        return False

    # -----------------------------------------------------
    # Social media hash garbage
    # -----------------------------------------------------

    if re.search(r'/[A-Za-z0-9]{8,}$', sentence):
        return False

    # -----------------------------------------------------
    # Broken concatenated words
    # Example:
    # Ahmet Oturganİşletmeler
    # -----------------------------------------------------

    if re.search(r'[a-zçğıöşü][A-ZÇĞİÖŞÜ]', sentence):
        return False

    # -----------------------------------------------------
    # Duplicate news-title style
    # -----------------------------------------------------

    duplicate_news_patterns = [

        r'Haberleri .* Haber',
        r'Son Dakika',
        r'Günün Haberleri',
    ]

    for p in duplicate_news_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False
        
    # -----------------------------------------------------
    # Profanity / toxic filtering
    # -----------------------------------------------------

    profanity_patterns = [
        r'amina',
        r'ebenin',
        r'siktir',
    ]

    for p in profanity_patterns:
        if re.search(p, sentence, re.IGNORECASE):
            return False


    # -----------------------------------------------------
    # Code / programming snippets
    # -----------------------------------------------------

    if re.search(r'\breturn\b.*;', sentence):
        return False

    if re.search(r'//', sentence):
        return False


    # -----------------------------------------------------
    # Business directory / company listings
    # -----------------------------------------------------

    if re.search(r'ltd\.?\s*şti', sentence, re.IGNORECASE):
        return False


    # -----------------------------------------------------
    # List / enumeration patterns
    # Example: 4) Yat Çekek Yeri:
    # -----------------------------------------------------

    if re.match(r'^\d+\)', sentence):
        return False


    # -----------------------------------------------------
    # Severe OCR corruption (very light)
    # -----------------------------------------------------

    if re.search(r'\bbulunn\b', sentence):
        return False

    # -----------------------------------------------------
    # Course/catalog/tabular style
    # -----------------------------------------------------

    tabular_patterns = [

        r'\bTS-\d+\b',
        r'\bMF-\d+\b',
        r'\bTM-\d+\b',
        r'\d+-\d+ gün',
        r'Numune Alma',
        r'Analizler için',
    ]

    for p in tabular_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Excessive standalone numbers
    # -----------------------------------------------------

    standalone_numbers = re.findall(r'\b\d+\b', sentence)

    if len(standalone_numbers) >= 6:
        return False

    # -----------------------------------------------------
    # Currency/course fee style
    # -----------------------------------------------------

    if re.search(r'ücreti\s+\d', sentence, re.IGNORECASE):
        return False

    # -----------------------------------------------------
    # Hit counter / index patterns
    # -----------------------------------------------------

    if re.search(r'\(hit\s*-\s*\d+\)', sentence, re.IGNORECASE):
        return False

    # -----------------------------------------------------
    # Filmography / media listing style
    # -----------------------------------------------------

    media_patterns = [

        r'Seslendirme',
        r'Sinema Filmi',
        r'TV Dizisi',
        r'Yapım Yılı',
    ]

    for p in media_patterns:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Broken OCR endings
    # -----------------------------------------------------

    broken_endings = [

        r'\sildi\.',
        r'\salmaktad',
        r'\sbulunmaktad',
    ]

    for p in broken_endings:

        if re.search(p, sentence, re.IGNORECASE):
            return False

    # -----------------------------------------------------
    # Too many short informal/chat words
    # -----------------------------------------------------

    informal_words = [

        r'\bbi\b',
        r'\bbunla\b',
        r'\bacaba\b',
    ]

    informal_hits = 0

    for p in informal_words:

        if re.search(p, sentence, re.IGNORECASE):
            informal_hits += 1

    if informal_hits >= 2:
        return False

    # -----------------------------------------------------
    # Excessive parentheses
    # -----------------------------------------------------

    if sentence.count("(") >= 2:
        return False

    # -----------------------------------------------------
    # Too many symbols
    # -----------------------------------------------------

    symbol_count = len(
        re.findall(
            r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s\.,!?()\-:;/%\'"]',
            sentence
        )
    )

    if symbol_count / max(len(sentence), 1) > 0.20:
        return False

    # -----------------------------------------------------
    # Numeric-only lines
    # -----------------------------------------------------

    if re.fullmatch(r'[0-9\s\.,]+', sentence):
        return False

    # -----------------------------------------------------
    # Repetitive character noise
    # -----------------------------------------------------

    if re.search(r'(.)\1{6,}', sentence):
        return False

    # -----------------------------------------------------
    # Template-heavy Wikipedia lines
    # -----------------------------------------------------

    if REMOVE_TEMPLATE_HEAVY and is_template_heavy(sentence):
        return False

    return True


# =========================================================
# DEDUPLICATION
# =========================================================

def normalize_for_dedup(sentence):

    s = sentence.lower()

    # Remove punctuation
    s = re.sub(r'[^a-z0-9çğıöşü\s]', '', s)

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

            # Clean line
            line = clean_line(line)

            if not line:
                continue

            # Sentence segmentation
            sentences = split_sentences(line)

            for sent in sentences:

                sent = sent.strip()

                # Validation
                if not is_valid_sentence(sent):
                    continue

                # Deduplication
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
        print("python preprocess_turkish.py input.txt output.txt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_file(input_path, output_path)