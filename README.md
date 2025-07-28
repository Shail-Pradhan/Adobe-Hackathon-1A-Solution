# PDF Processing Solution

## Overview
This solution implements a high-performance PDF text extraction and document structure analysis system. It processes PDF documents to extract their title and outline structure, outputting the results in a standardized JSON format. The solution is containerized using Docker and optimized for AMD64 architecture.

## Technical Architecture

### Core Components
1. **PDF Processor** (`pdf_processor.py`)
   - Main processing pipeline
   - Handles multi-page document processing
   - Implements parallel processing for improved performance

2. **Extractors** (`src/extractors/`)
   - `text_extractor.py`: Handles text content extraction and title identification
   - `heading_extractor.py`: Identifies and classifies document headings

3. **Utilities** (`src/utils/`)
   - `form_detector.py`: Detects and handles form elements
   - `text_patterns.py`: Text analysis patterns and utilities

### Libraries Used
- **PyMuPDF (v1.23.6)**
  - Primary PDF processing engine
  - Handles text extraction and document structure analysis
  - Efficient memory management for large documents

- **Tesseract OCR**
  - Fallback OCR for images or unextractable text
  - Used with `pytesseract` (v0.3.10) Python wrapper

- **Additional Dependencies**
  - `numpy` (≥2.0.0): Numerical operations and data processing
  - `jsonschema` (v4.17.3): JSON validation against schema

## Implementation Details
### Text Extraction Strategy
1. **Primary Extraction using PyMuPDF**
   - Uses PyMuPDF's advanced text extraction engine to process PDFs
   - Extracts detailed text properties:
     * Font names, sizes, and styles
     * Exact text coordinates (x, y positions)
     * Character spacing and line heights
   - Preserves document structure through:
     * Block-level organization (paragraphs, sections)
     * Text flow analysis
     * Character encoding preservation
   - Maintains spatial relationships:
     * Column detection and handling
     * Text block boundaries
     * Reading order preservation

2. **Fallback OCR System**
   - Intelligent fallback mechanism:
     * Monitors text extraction success
     * Detects when pages contain no extractable text
     * Identifies scanned or image-based PDFs
   - Page-to-Image Conversion:
     * High-resolution pixmap generation (300 DPI)
     * Image preprocessing for OCR optimization
     * Color space management for better text detection
   - Tesseract OCR Integration:
     * Language-specific text recognition (English)
     * Character confidence scoring
     * Structural layout analysis
   - Seamless Results Integration:
     * Converts OCR results to match native extraction format
     * Preserves page coordinates and positioning
     * Maintains consistent data structure

### Document Structure Analysis
1. **Title Detection System**
   - First Page Analysis:
     * Prioritizes top section examination
     * Analyzes first 25% of page content
     * Identifies potential title candidates
   - Advanced Font Analysis:
     * Compares font sizes against document average
     * Identifies emphasized text (bold, large size)
     * Detects special formatting and styles
   - Intelligent Filtering:
     * Removes headers, footers, and page numbers
     * Filters out metadata and document properties
     * Excludes navigation elements
   - Validation Rules:
     * Checks title length and format
     * Verifies positioning on page
     * Confirms uniqueness in document

2. **Heading Classification Engine**
   - Hierarchical Structure Detection:
     * Analyzes font size relationships
     * Identifies consistent formatting patterns
     * Builds document outline tree
   - Font Characteristic Analysis:
     * Tracks font usage patterns
     * Identifies heading-specific fonts
     * Detects emphasis markers (bold, italics)
   - Position-Based Analysis:
     * Evaluates vertical spacing patterns
     * Analyzes indentation levels
     * Considers page section boundaries
   - Hierarchy Validation:
     * Ensures proper nesting (h1 → h2 → h3)
     * Fixes inconsistent level jumps
     * Maintains logical document structure
   - Normalization Process:
     * Standardizes heading levels (1-6)
     * Adjusts inconsistent formatting
     * Ensures consistent numbering

### Performance Optimizations
- Parallel processing of multiple pages
- Efficient memory management for large documents
- Binary-only package installations
- Minimal container size

## Docker Configuration

### Base Image
- Uses `python:3.10-slim` for minimal footprint
- AMD64 architecture support
- No unnecessary dependencies

### Environment Setup
```dockerfile
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
```

### Security Features
- Read-only input directory
- Controlled output permissions
- Optional non-root user execution

## Usage Instructions

### Building the Image
```bash
docker build --platform linux/amd64 -t pdf-processor .
```


# For local testing:
docker run --rm \
  -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
  -v "$(pwd)/sample_dataset/outputs:/app/output" \
  --network none \
  pdf-processor
```

### Input/Output
- **Input**: PDFs should be in `/app/input` inside the container
- **Output**: JSON files are generated in `/app/output` inside the container
- For challenge: Mount your input directory to `/app/input` and output to `/app/output`


## Output Format
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": 1,
      "text": "Heading Text",
      "page": 0
    }
  ]
}
```

## Performance Metrics
- Processing Time: < 10 seconds for 50-page documents
- Memory Usage: Within 16GB RAM limit
- CPU Utilization: Optimized for 8 cores
- No network access required during runtime

## Testing and Validation

### Test Cases
1. **Simple Documents**
   - Basic text-only PDFs
   - Single-column layouts

2. **Complex Documents**
   - Multi-column layouts
   - Mixed text and images
   - Various font styles

3. **Edge Cases**
   - Image-only PDFs (OCR fallback)
   - Non-standard fonts
   - Large documents (50+ pages)
