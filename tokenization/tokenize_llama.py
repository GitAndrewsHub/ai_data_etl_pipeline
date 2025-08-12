"""
Module: tokenize_llama.py

Tokenizes normalized text files using Hugging Face's LLaMA tokenizer.
Outputs JSONL files: {"tokens": [...], "doc_id": "..."}
"""

import boto3
from smart_open import open as s3_open
import json
from transformers import LlamaTokenizerFast


s3 = boto3.client('s3')
bucket = "my-cc-pipeline-s3"
input_key = "normalized/normalized.txt"
output_key = "tokenized/global_tokenized.jsonl"

input_path = f"s3://{bucket}/{input_key}"
output_path = f"s3://{bucket}/{output_key}"

# Initialize LLaMA tokenizer
tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")

# Initialize doc_id properly before main()
doc_id = 0


def main():
    global doc_id
    current_doc_lines = []

    with s3_open(input_path, 'r', encoding='utf-8') as fin, \
         s3_open(output_path, 'w', encoding='utf-8') as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue

            if line == "[DOC_START]":
                # Emit previous doc if exists
                if current_doc_lines:
                    emit_doc(current_doc_lines, fout)
                    current_doc_lines = []
                continue

            if line.startswith("URL:"):
                continue  # Skip metadata during tokenization, or keep if required.

            current_doc_lines.append(line)

        # Emit last doc if any
        if current_doc_lines:
            emit_doc(current_doc_lines, fout)

    print(f"✅ Tokenization complete: s3://{bucket}/{output_key}")

    log_path = "s3://my-cc-pipeline-s3/logs/tokenized_log.txt"
    with s3_open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"{output_key} | Total documents tokenized: {doc_id}\n")


def emit_doc(doc_lines, fout):
    global doc_id
    text = " ".join(doc_lines)
    tokens = tokenizer.encode(text, add_special_tokens=False)

    record = {
        "id": doc_id,
        "tokens": tokens
    }
    fout.write(json.dumps(record) + "\n")
    doc_id += 1


if __name__ == "__main__":
    main()
