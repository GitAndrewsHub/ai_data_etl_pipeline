"""
Module: global_deduplicate.py

Globally deduplicates across all deduped files by combining them
and applying MinHash/LSH deduplication.
"""

import hashlib
from datasketch import MinHash, MinHashLSH
import boto3
from smart_open import open as s3_open

# S3 config
BUCKET = "my-cc-pipeline-s3"
DEDUPED_PREFIX = "deduplicated/"
FINAL_OUTPUT_KEY = "final/global_deduplicated.txt"
FINAL_OUTPUT_PATH = f"s3://{BUCKET}/{FINAL_OUTPUT_KEY}"

s3 = boto3.client('s3')

# Parameters
NUM_PERM = 128
SIMILARITY_THRESHOLD = 0.8

# Utility
def get_minhash(text):
    m = MinHash(num_perm=NUM_PERM)
    for word in text.split():
        m.update(word.encode('utf-8'))
    return m

def is_special_line(line):
    return line.startswith("[DOC_START]") or line.startswith("URL:")

# Initialize LSH
lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=NUM_PERM)

kept = 0
skipped = 0

with s3_open(FINAL_OUTPUT_PATH, 'w', encoding='utf-8') as fout:
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=DEDUPED_PREFIX)

    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        if not s3_key.endswith("_deduped.txt"):
            continue

        input_path = f"s3://{BUCKET}/{s3_key}"

        with s3_open(input_path, 'r', encoding='utf-8') as fin:

            doc_lines = []
            metadata_lines = []

            for line in fin:
                line = line.strip()
                if not line:
                    continue

                if line == "[DOC_START]":

                    if doc_lines:
                        text = " ".join(doc_lines)
                        minhash = get_minhash(text)
                        key = hashlib.md5(text.encode('utf-8')).hexdigest()

                        if not lsh.query(minhash):
                            lsh.insert(key, minhash)
                            for meta in metadata_lines:
                                fout.write(meta + "\n")
                            for content_line in doc_lines:
                                fout.write(content_line + "\n")
                            fout.write("\n")
                            kept += 1
                        else:
                            skipped += 1

                    metadata_lines = [line]
                    doc_lines = []

                elif line.startswith("URL:"):
                    metadata_lines.append(line)

                else:
                    doc_lines.append(line)

            # Handle last doc in file
            if doc_lines:
                text = " ".join(doc_lines)
                minhash = get_minhash(text)
                key = hashlib.md5(text.encode('utf-8')).hexdigest()

                if not lsh.query(minhash):
                    lsh.insert(key, minhash)
                    for meta in metadata_lines:
                        fout.write(meta + "\n")
                    for content_line in doc_lines:
                        fout.write(content_line + "\n")
                    fout.write("\n")
                    kept += 1
                else:
                    skipped += 1

print(f"✅ Global deduplication complete: s3://{BUCKET}/{FINAL_OUTPUT_KEY}")

# Write log to S3
log_path = "s3://my-cc-pipeline-s3/logs/global_deduplicated_log.txt"
log_entry = f"{FINAL_OUTPUT_KEY} | Unique docs: {kept}, Duplicates removed: {skipped}\n"

with s3_open(log_path, 'w', encoding='utf-8') as log_file:
    log_file.write(log_entry)


