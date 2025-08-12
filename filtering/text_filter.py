"""
Module: text_filter.py

This module filters raw text files by language using a pre-trained fastText
model. It now cleans each line by removing URLs and code snippets instead
of skipping entire lines. The output is saved in the `data/filtered/`
directory for downstream preprocessing steps. Incorporate jusText to
retain main body content only.
"""

import unicodedata
import re
import fasttext
import justext
from hydra import initialize, compose
from smart_open import open as s3_open
import boto3

s3 = boto3.client('s3')
BUCKET = "my-cc-pipeline-s3"
EXTRACTED_PREFIX = "extracted/"
FILTERED_PREFIX = "filtered/"

# Load config
with initialize(config_path="../configs", version_base=None):
    cfg = compose(config_name="config")

# Load fastText language ID model
model = fasttext.load_model("models/lid.176.bin")

# Paths
S3_EXTRACTED_PREFIX = "s3://my-cc-pipeline-s3/extracted/"
S3_FILTERED_PREFIX = "s3://my-cc-pipeline-s3/filtered/"

# Parameters
TARGET_LANG = "en"
CONFIDENCE_THRESHOLD = 0.5
MIN_LENGTH = 5

# Cleaning patterns
url_pattern = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)
code_pattern = re.compile(r'`[^`]+`|```[\s\S]+?```', re.IGNORECASE)
html_tag_pattern = re.compile(r'<[^>]+>')
non_printable_pattern = re.compile(r'[^\x20-\x7E]+')
boilerplate_phrases = cfg.filters.boilerplate_phrases
section_cutoff_phrases = [phrase.lower() for phrase in cfg.filters.section_cutoff_phrases]


def check_section_cutoff(text):
    """
    Check if a line matches any of the cutoff phrases.
    """
    return any(text.lower().strip() == phrase for phrase in section_cutoff_phrases)


def detect_language(text):
    """
    Detects the language of a given text string using the fastText model.

    Args:
        text (str): The input text to detect language for.

    Returns:
        tuple: Detected language code and associated confidence probability.
    """
    label, prob = model.predict(text)
    lang = label[0].replace("__label__", "")
    return lang, prob[0]


def clean_unicode(text):
    """
    Cleans special Unicode separators and replaces exotic characters.

    Args:
        text (str): A line of text.

    Returns:
        str: Cleaned text.
    """
    text = text.replace('\u2028', ' ').replace('\u2029', ' ')
    text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    text = text.replace("–", "-").replace("—", "-")
    return unicodedata.normalize('NFKC', text)


def contains_boilerplate(text):
    """
    Checks if a line contains any boilerplate phrase.
    """
    return any(phrase.lower() in text.lower() for phrase in boilerplate_phrases)


def clean_line(text):
    """
    Cleans a text line by removing URLs and code snippets.

    Args:
        text (str): The input text.

    Returns:
        str: Cleaned text with unwanted elements removed.
    """
    text = url_pattern.sub('', text)
    text = code_pattern.sub('', text)
    text = html_tag_pattern.sub('', text)
    text = non_printable_pattern.sub('', text)
    text = ' '.join(text.split())

    if contains_boilerplate(text):
        return ''

    return text.strip()


def normalize_text(text):
    text = clean_unicode(text)
    text = url_pattern.sub('', text)
    text = html_tag_pattern.sub('', text)
    text = non_printable_pattern.sub('', text)
    text = ' '.join(text.split())
    text = text.lower().strip()
    return text


def extract_main_content(text):
    """
    Use jusText to extract the main body content from HTML/text.
    """
    paragraphs = justext.justext(text, justext.get_stoplist("English"))
    cleaned = "\n".join(p.text for p in paragraphs if not p.is_boilerplate)
    return cleaned.strip()


def is_special_line(line):
    return line == "[DOC_START]" or line.startswith("URL: ")


def filter_file(s3_key):
    """
    Filters and cleans lines in a file and saves the cleaned English lines.

    Args:
        file_path (Path): Path to the raw input text file.
    """
    input_path = f"s3://{BUCKET}/{s3_key}"
    output_key = s3_key.replace("extracted/", "filtered/").replace("_extracted", "_filtered")
    output_path = f"s3://{BUCKET}/{output_key}"

    kept = 0
    skipped = 0
    in_cutoff_section = False

    with s3_open(input_path, 'r', encoding='utf-8') as fin, \
         s3_open(output_path, 'w', encoding='utf-8') as fout:
        for i, line in enumerate(fin):
            line = clean_unicode(line.strip())
            if not line:
                continue

            if in_cutoff_section:
                skipped += 1
                continue

            # Preserve metadata lines as-is
            if is_special_line(line):
                fout.write(line + '\n')
                continue

            # Check for section cutoff phrase
            if check_section_cutoff(line):
                in_cutoff_section = True
                skipped += 1
                continue

            cleaned_line = clean_line(line)

            if not cleaned_line or len(cleaned_line) < MIN_LENGTH:
                skipped += 1
                continue

            lang, prob = detect_language(cleaned_line)
            if lang == TARGET_LANG and prob >= CONFIDENCE_THRESHOLD:
                fout.write(cleaned_line + '\n')
                kept += 1
            else:
                skipped += 1


    # ✅ Log to S3 after processing the entire file
    log_path = "s3://my-cc-pipeline-s3/logs/filtered_log.txt"
    log_entry = f"{s3_key} | Kept: {kept}, Skipped: {skipped}\n"

    with s3_open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(log_entry)

    print(f"✅ Done: {output_path} | Kept: {kept}, Skipped: {skipped}\n")


def main():
    """
    Main function to iterate over extracted raw text files and filter them.
    """
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=EXTRACTED_PREFIX)
    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        if s3_key.endswith('_extracted.txt'):
            filter_file(s3_key)


if __name__ == "__main__":
    main()
