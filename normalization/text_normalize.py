"""
Module: text_normalize.py

Normalizes deduplicated text files:
- Preserves [DOC_START] markers.
- Normalizes unicode punctuation (quotes, dashes, ellipsis).
- Collapses excess whitespace.
- Removes trailing spaces.

Output:
- Normalized files saved to `normalized/`.
"""

import boto3
from smart_open import open as s3_open
import unicodedata
import re

# S3 config
s3 = boto3.client('s3')
BUCKET = "my-cc-pipeline-s3"
INPUT_KEY = "final/global_deduplicated.txt"
OUTPUT_KEY = "normalized/normalized.txt"
INPUT_PATH = f"s3://{BUCKET}/{INPUT_KEY}"
OUTPUT_PATH = f"s3://{BUCKET}/{OUTPUT_KEY}"

# Cleaning patterns
url_pattern = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)
non_printable_pattern = re.compile(r'[^\x20-\x7E]+')


def clean_unicode(text):
    text = text.replace('\u2028', ' ').replace('\u2029', ' ')
    text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    text = text.replace("–", "-").replace("—", "-")
    return unicodedata.normalize('NFKC', text)


def normalize_line(line):
    text = clean_unicode(line)
    text = url_pattern.sub('', text)
    text = non_printable_pattern.sub('', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_special_line(line):
    return line == "[DOC_START]" or line.startswith("URL:")


def main():
    kept = 0
    removed = 0

    with s3_open(INPUT_PATH, 'r', encoding='utf-8') as fin, \
         s3_open(OUTPUT_PATH, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                removed += 1
                continue

            if is_special_line(line):
                fout.write(line + '\n')
                kept += 1
                continue

            normalized = normalize_line(line)
            if normalized:
                fout.write(normalized + '\n')
                kept += 1
            else:
                removed += 1

    print(f"✅ Normalization complete: s3://{BUCKET}/{OUTPUT_KEY}")

    log_path = "s3://my-cc-pipeline-s3/logs/normalized_log.txt"
    log_entry = f"{OUTPUT_KEY} | Kept: {kept}, Removed: {removed}\n"

    with s3_open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(log_entry)


if __name__ == "__main__":
    main()
