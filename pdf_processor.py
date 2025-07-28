"""Main PDF processing module using modular components."""
import json
import fitz  # PyMuPDF
import pytesseract
import logging
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from collections import Counter

from src.utils.form_detector import FormDetector
from src.extractors.text_extractor import TextExtractor
from src.extractors.heading_extractor import HeadingExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        # Ensure TESSDATA_PREFIX is set for Tesseract
        if 'TESSDATA_PREFIX' not in os.environ:
            os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'

    def extract_spans_from_page(self, pdf_path, page_num):
        """Extract text spans with their properties from a page."""
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            
            spans = []
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                if FormDetector.is_table_block(block):
                    continue
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span['text'].strip():
                            spans.append({
                                'text': span['text'].strip(),
                                'font': span['font'],
                                'size': span['size'],
                                'flags': span.get('flags', 0),
                                'bbox': span['bbox'],
                                'y_pos': span['bbox'][1],
                                'page': page_num  # ✅ zero-based indexing
                            })
            
            if not spans:
                logger.info(f"No text found on page {page_num}, attempting OCR")
                pix = page.get_pixmap()
                image = pix.tobytes("png")
                text = pytesseract.image_to_string(image)
                if text.strip():
                    spans.append({
                        'text': text.strip(),
                        'font': 'OCR',
                        'size': 12,
                        'flags': 0,
                        'bbox': page.rect,
                        'y_pos': 0,
                        'page': page_num  # ✅ zero-based indexing (OCR)
                    })
            
            doc.close()
            return spans

        except Exception as e:
            logger.error(f"Error processing page {page_num}: {str(e)}")
            return []

    def find_body_font(self, all_spans):
        """Determine the most common font and size combination."""
        font_sizes = Counter((span['font'], span['size']) for span in all_spans)
        if not font_sizes:
            return None, 12
        return max(font_sizes.items(), key=lambda x: x[1])[0]

    def process_pdf(self, pdf_path, output_path):
        """Process a single PDF file."""
        try:
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            doc.close()
            
            all_spans_lists = []
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.extract_spans_from_page, pdf_path, i) 
                           for i in range(num_pages)]
                all_spans_lists = [f.result() for f in futures]
            
            all_spans = [span for spans in all_spans_lists for span in spans]
            
            if not all_spans:
                raise ValueError("No text content found in PDF")
            
            body_font, body_size = self.find_body_font(all_spans)

            # ✅ Use page index 0 for title extraction
            page_1_spans = [s for s in all_spans if s['page'] == 0]
            title = TextExtractor.extract_title(page_1_spans)
            
            outline = []
            seen_headings = set()
            sorted_spans = sorted(all_spans, key=lambda x: (x['page'], x['y_pos']))

            for span in sorted_spans:
                heading_info = HeadingExtractor.classify_heading(span, body_font, body_size)
                if heading_info:
                    level, text = heading_info

                    title_words = set(title.lower().split())
                    text_words = set(text.lower().split())
                    if title_words == text_words or text.strip() == title.strip():
                        continue

                    heading_key = f"{level}:{text}:{span['page']}"
                    if heading_key not in seen_headings:
                        outline.append({
                            "level": level,
                            "text": text,
                            "page": span['page']  # ✅ zero-based output
                        })
                        seen_headings.add(heading_key)

            outline = HeadingExtractor.validate_hierarchy(outline)

            result = {
                "title": title,
                "outline": outline
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"Successfully processed {pdf_path} → {output_path}")

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            raise

def process_pdfs():
    """Process all PDFs in the input directory."""
    processor = PDFProcessor()
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for pdf_file in input_dir.glob("*.pdf"):
        output_file = output_dir / f"{pdf_file.stem}.json"
        try:
            processor.process_pdf(pdf_file, output_file)
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")
            continue

if __name__ == "__main__":
    process_pdfs()
