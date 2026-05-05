import re
import unicodedata

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

    # Keep Persian chars, English chars, digits, punctuation
    text = re.sub(
        r'[^0-9A-Za-z\u0600-\u06FF\s\.,!?؛،:%()\-\"]+',
        ' ',
        text
    )

    text = MULTISPACE.sub(' ', text).strip()

    return text