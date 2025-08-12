"""
Module: text_ingest.py

Ingests and filters web pages from Common Crawl WET files, input dynamically.
Aggressively filters based on domain, URL patterns, and required page keywords
for medical imaging relevance.
"""

import argparse
from pathlib import Path
from io import StringIO
import requests
from warcio.archiveiterator import ArchiveIterator
from hydra import initialize, compose
from smart_open import open as s3_open


# Load Hydra config
with initialize(config_path="../configs", version_base=None):
    cfg = compose(config_name="config")

# Paths
raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

# Filters
domain_whitelist = cfg.filters.domain_whitelist
url_includes = cfg.filters.url_includes
required_page_keywords = cfg.filters.required_page_keywords


def contains_required_keywords(text):
    """
    Checks if the page content contains at least one required keyword.
    """
    return any(keyword.lower() in text.lower() for keyword in required_page_keywords)


def download_and_process_wet(url, save_dir):
    """
    Downloads the WET file and extracts relevant web pages.
    """

    response = requests.get(url, stream=True)
    filename = save_dir / Path(url).name

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    s3_output_path = f"s3://my-cc-pipeline-s3/extracted/{filename.stem}_extracted.txt"
    s3_log_path = "s3://my-cc-pipeline-s3/logs/extraction_log.txt"
    extract_relevant_pages(filename, s3_output_path, s3_log_path)


def extract_relevant_pages(wet_file_path, s3_output_path, s3_log_path):
    """
    Parses WET file and saves relevant web pages to the raw directory.
    Applies domain, content keyword, and URL keyword filters with smart
    matching. Logs detailed reasons for keeping or skipping pages.
    """

    kept_pages = 0
    skipped_pages = 0
    total_records = 0
    buffer = StringIO()

    with open(wet_file_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            total_records += 1
            if record.rec_type != 'conversion':
                continue

            url = record.rec_headers.get_header('WARC-Target-URI')
            if not url:
                skipped_pages += 1
                continue

            try:
                content = record.content_stream().read().decode('utf-8', errors='ignore')
            except Exception as e:
                skipped_pages += 1
                continue

            if not content.strip():
                skipped_pages += 1
                continue

            url_lower = url.lower()
            url_normalized = url_lower.replace('_', ' ').replace('-', ' ')
            content_lower = content.lower()

            # URL include check
            url_include_match = None
            for keyword in cfg.filters.url_includes:
                if keyword.lower() in url_normalized:
                    url_include_match = keyword
                    break
            if not url_include_match:
                skipped_pages += 1
                continue

            # URL exclude check
            url_exclude_trigger = None
            for keyword in cfg.filters.url_excludes:
                if keyword.lower() in url_normalized:
                    url_exclude_trigger = keyword
                    break
            if url_exclude_trigger:
                skipped_pages += 1
                continue

            # Required page keyword check (must match all)
            if not all(kw.lower() in content_lower for kw in cfg.filters.required_page_keywords):
                skipped_pages += 1
                continue

            # Exclude page keywords check
            exclude_page_trigger = None
            for keyword in cfg.filters.exclude_page_keywords:
                if keyword.lower() in content_lower:
                    exclude_page_trigger = keyword
                    break
            if exclude_page_trigger:
                skipped_pages += 1
                continue


            buffer.write("[DOC_START]\n")
            buffer.write(f"URL: {url}\n")
            buffer.write(f"{content.strip()}\n\n")
            kept_pages += 1

    # Upload only if buffer is non-empty and pages were kept
    if kept_pages > 0 and buffer.getvalue().strip():
        with s3_open(s3_output_path, 'w', encoding='utf-8') as fout:
            fout.write(buffer.getvalue())
        upload_status = "✅ Uploaded"
    else:
        upload_status = "⚠️ Skipped upload (no valid content)"


    # Read existing log contents if file exists
    try:
        with s3_open(s3_log_path, 'r', encoding='utf-8') as existing_log:
            previous_logs = existing_log.read()
    except Exception:
        previous_logs = ""


    # Always log
    log_entry = (
        f"File: {wet_file_path.name}\n"
        f"Total records: {total_records}\n"
        f"Pages kept: {kept_pages}\n"
        f"Pages skipped: {skipped_pages}\n\n"
    )

    # Write full updated log to S3
    with s3_open(s3_log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(previous_logs + log_entry)

    print(f"\n📊 WET file summary:")
    print(f"  Total records processed: {total_records}")
    print(f"  Pages kept: {kept_pages}")
    print(f"  Pages skipped: {skipped_pages}")
    print(f"{upload_status}: {s3_output_path if kept_pages > 0 else 'N/A'}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--warc_url", required=True, help="Full WET file URL to ingest")
    args = parser.parse_args()

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    download_and_process_wet(args.warc_url, raw_dir)

if __name__ == "__main__":
    main()
