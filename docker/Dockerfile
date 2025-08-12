# emr-docker/Dockerfile

# Use a slim Python 3.10 base image
FROM python:3.10-slim AS base

# Install system packages needed for SSL compilation, fasttext, and jusText
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    build-essential \
    libffi-dev \
    libssl-dev \
    tzdata \
    clang \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip && \
    pip install \
    numpy==1.24.4 \
    requests==2.31.0 \
    warcio==1.7.4 \
    hydra-core==1.3.2 \
    "smart_open[s3]" \
    fasttext \
    justext \
    lxml \
    detoxify \
    torch \
    transformers \
    datasketch

# Set working directory
WORKDIR /app

# Copy entire build context into the image
COPY . .

CMD ["echo", "Define script & args at runtime"]

# ---------- Text Ingest Target ----------
# FROM base AS ingest
# CMD ["python", "ingestion/text_ingest.py"]

# ---------- Text Filter Target ----------
# FROM base AS filter
# CMD ["python", "filtering/text_filter.py"]

# ---------- Toxicity Filter Target ----------
# FROM base AS toxicity
# CMD ["python", "filtering/toxicity_filter.py"]

# ---------- Deduplication Target ----------
# FROM base AS dedup
# CMD ["python", "deduplication/deduplicate.py"]

# ---------- Global Deduplication Target ----------
# FROM base AS global
# CMD ["python", "deduplication/global_deduplicate.py"]

# ---------- Normalize Target ----------
# FROM base AS normalize
# CMD ["python", "normalization/text_normalize.py"]

# ---------- Tokenization Target ----------
# FROM base AS tokenize
# CMD ["python", "tokenization/tokenize_llama.py"]
