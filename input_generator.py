import json

base = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-21/segments/1746990412205.50/wet/"
prefix = "CC-MAIN-20250512011722-20250512041722-"
suffix = ".warc.wet.gz"

urls = [
    f"{base}{prefix}{str(i).zfill(5)}{suffix}"
    for i in range(100)
]

with open("input.json", "w") as f:
    json.dump({"warc_urls": urls}, f, indent=2)

print("✅ input.json created with 100 WARC URLs")
