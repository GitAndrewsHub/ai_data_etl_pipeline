"""
Module: deduplicate.py

Removes near-duplicate lines from filtered text files using MinHash and
Locality Sensitive Hashing (LSH). This helps reduce redundancy before
training language models.
"""

import hashlib
import string
from collections import defaultdict
from datasketch import MinHash, MinHashLSH
from hydra import initialize, compose
import boto3
from smart_open import open as s3_open

# Load config
with initialize(config_path="../configs", version_base=None):
    cfg = compose(config_name="config")

# S3 setup
s3 = boto3.client('s3')
BUCKET = "my-cc-pipeline-s3"
DETOXIFIED_PREFIX = "detoxified/"
DEDUPED_PREFIX = "deduplicated/"

# Initialize filter counts
filter_counts = defaultdict(int)

# Parameters
MIN_WORD_COUNT = cfg.filters.min_word_count
PUNCTUATION_THRESHOLD = cfg.filters.punctuation_ratio_threshold
BOILERPLATE_PHRASES = [phrase.lower() for phrase in cfg.filters.boilerplate_phrases]
SIMILARITY_THRESHOLD = cfg.deduplication.similarity_threshold
NUM_PERM = cfg.deduplication.num_perm


def get_minhash(text: str) -> MinHash:
    """
    Generate a MinHash signature for a given text line.

    Args:
        text (str): The input line of text.

    Returns:
        MinHash: The MinHash signature object.
    """
    m = MinHash(num_perm=NUM_PERM)
    for word in text.split():
        m.update(word.encode('utf-8'))
    return m


def is_low_value_line(line):
    """
    Applies aggressive multi-layered filtering using regex patterns and heuristics.
    """
    if len(line.split()) < MIN_WORD_COUNT:
        return True

    if is_high_punctuation_ratio(line):
        return True

    if any(phrase in line.lower() for phrase in BOILERPLATE_PHRASES):
        return True

    return False


def is_high_punctuation_ratio(line):
    words = line.split()
    if not words:
        return False

    punctuation_count = sum(1 for char in line if char in string.punctuation)
    word_count = len(words)

    return (punctuation_count / word_count) > PUNCTUATION_THRESHOLD


def is_special_line(line):
    return line == "[DOC_START]" or line.startswith("URL: ")


def deduplicate_file(s3_key: str, lsh: MinHashLSH):
    """
    Deduplicates a single file based on MinHash similarity.

    Args:
        file_path (Path): Path to the input filtered file.
        lsh (MinHashLSH): Global LSH index for duplicate detection.
    """
    input_path = f"s3://{BUCKET}/{s3_key}"
    output_key = s3_key.replace(DETOXIFIED_PREFIX, DEDUPED_PREFIX).replace("_detoxified", "_deduped")
    output_path = f"s3://{BUCKET}/{output_key}"

    kept = 0
    skipped = 0

    with s3_open(input_path, 'r', encoding='utf-8') as fin, \
         s3_open(output_path, 'w', encoding='utf-8') as fout:

        for i, line in enumerate(fin):
            line = line.strip()
            if not line:
                continue

            # Always keep special metadata lines
            if is_special_line(line):
                fout.write(line + "\n")
                continue

            if is_low_value_line(line):
                skipped += 1
                continue


            minhash = get_minhash(line)
            key = hashlib.md5(line.encode('utf-8')).hexdigest()

            # Check for duplicates
            if not lsh.query(minhash):
                lsh.insert(key, minhash)
                fout.write(line + "\n")
                kept += 1
            else:
                skipped += 1

        # S3 log write
    log_path = "s3://my-cc-pipeline-s3/logs/deduplicated_log.txt"
    log_entry = f"{output_key} | Kept: {kept}, Removed: {skipped}\n"

    with s3_open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(log_entry)


    print(f"✅ Done: {output_key} | Kept: {kept}, Removed: {skipped}")


def main():
    lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=NUM_PERM)
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=DETOXIFIED_PREFIX)

    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        if s3_key.endswith("_detoxified.txt"):
            deduplicate_file(s3_key, lsh)



if __name__ == "__main__":
    main()
