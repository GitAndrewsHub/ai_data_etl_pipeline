"""
Module: toxicity_filter.py

Filters out toxic text lines from deduplicated data using Detoxify.
Uses a single toxicity threshold and saves only safe lines.
"""

from detoxify import Detoxify
import boto3
from smart_open import open as s3_open

# Load Detoxify model
model = Detoxify('original')

# S3 configuration
s3 = boto3.client('s3')
BUCKET = "my-cc-pipeline-s3"
FILTERED_PREFIX = "filtered/"
DETOXIFIED_PREFIX = "detoxified/"


# Parameters
TOXICITY_THRESHOLD = 0.5


def is_special_line(line):
    return line.strip() == "[DOC_START]" or line.startswith("URL:")


def filter_toxicity(s3_key):
    """
    Filters toxic lines using Detoxify. Only saves safe lines.

    Filters toxic lines from a single deduped file on S3.
    """
    input_path = f"s3://{BUCKET}/{s3_key}"
    output_key = s3_key.replace(FILTERED_PREFIX, DETOXIFIED_PREFIX).replace("_filtered", "_detoxified")
    output_path = f"s3://{BUCKET}/{output_key}"

    kept = 0
    removed = 0

    with s3_open(input_path, 'r', encoding='utf-8') as fin, \
         s3_open(output_path, 'w', encoding='utf-8') as fout:

        for line in fin:
            text = line.strip()
            if not text:
                continue

            if is_special_line(text):
                fout.write(line)
                kept += 1
                continue


            try:
                score = model.predict(text)["toxicity"]
            except Exception as e:
                removed += 1
                continue

            if score < TOXICITY_THRESHOLD:
                fout.write(line)
                kept += 1
            else:
                removed += 1


    log_path = "s3://my-cc-pipeline-s3/logs/toxicity_log.txt"
    log_entry = f"{output_key} | Safe: {kept}, Removed: {removed}\n"

    with s3_open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(log_entry)

    print(f"✅ Done: {output_key} | Safe lines: {kept}, Removed: {removed}")


def main():
    """
    Iterate over all deduped files in S3 and run toxicity filtering.
    """
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=FILTERED_PREFIX)
    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        if s3_key.endswith("_filtered.txt"):
            filter_toxicity(s3_key)


if __name__ == "__main__":
    main()
