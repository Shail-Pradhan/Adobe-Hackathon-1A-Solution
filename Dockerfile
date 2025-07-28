FROM --platform=linux/amd64 python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY pdf_processor.py .
COPY src/ ./src/

# Create mount points for input and output
# Input directory is read-only, output directory needs write access
RUN mkdir -p /app/input && \
    mkdir -p /app/output && \
    chmod 555 /app/input && \
    chmod 777 /app/output

# Environment vars
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Optional: switch to non-root user (if host file permissions are safe)
# RUN groupadd -r processor && useradd -r -g processor processor
# USER processor

# Run the processor
CMD ["python", "-u", "pdf_processor.py"]
