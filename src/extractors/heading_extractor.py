"""Heading extraction and classification."""
import re
from ..utils.text_patterns import FORM_PATTERNS, NUMBERED_HEADING_PATTERNS

class HeadingExtractor:
    @staticmethod
    def classify_heading(span, body_font, body_size):
        """Classify a span as a heading and determine its level."""
        text = span['text'].strip()
        size = span['size']
        is_bold = bool(span['flags'] & 2**4)  # Check if text is bold
        
        # Skip empty or too-short text
        if not text or len(text) < 2:
            return None
            
        # Skip version numbers, dates, and small texts
        if re.match(r'^v\d+(\.\d+)*$', text, re.I):  # Version numbers
            return None
        if re.match(r'^version\s+\d+(\.\d+)*$', text, re.I):  # Version text
            return None
        if len(text) < 5 and not re.match(r'^\d+\.$', text):  # Short text unless it's a numbered heading
            return None
            
        # Convert text to lowercase for pattern matching
        text_lower = text.lower()
        
        # Skip if matches any form pattern
        if any(re.search(pattern, text_lower) for pattern in FORM_PATTERNS):
            return None
            
        # Skip form labels and short meta information
        if text.lower().endswith(':') or text.lower().startswith('version'):  
            return None
            
        # Check for copyright notices or standard footers
        if any(x in text_lower for x in ['©', 'copyright', 'all rights reserved']):
            return None
            
        # Check for numbered headings - careful handling of section numbers
        for pattern, level in NUMBERED_HEADING_PATTERNS:
            match = re.match(pattern, text)
            if match:
                # For section numbers, include the number in the heading
                return f'H{level}', text.strip()
        
        # Size and style-based classification (only for text that looks like a heading)
        # Must contain actual words, not just numbers or symbols
        if re.search(r'[A-Za-z]{3,}', text):
            size_diff = size - body_size
            
            # Position check - reject items too close to bottom of page
            y_pos = span['bbox'][1]
            page_height = 792  # Standard letter page height
            if y_pos > page_height * 0.85:  # Skip if in footer area
                return None
                
            # Check character count - avoid very short or very long text
            char_count = len(text)
            if 4 <= char_count <= 100:  # Reasonable heading length
                if size_diff >= 4 or (size_diff >= 3 and is_bold):
                    return 'H1', text
                elif size_diff >= 3 or (size_diff >= 2 and is_bold):
                    return 'H2', text
                elif size_diff >= 2 or (size_diff >= 1 and is_bold):
                    return 'H3', text
                elif size_diff >= 1 and is_bold and char_count > 10:
                    return 'H4', text
        
        return None
        
    @staticmethod
    def validate_hierarchy(outline):
        """Ensure heading hierarchy is valid (no sudden jumps)."""
        if not outline:
            return outline
            
        validated = []
        current_level = 0
        
        for item in outline:
            level_num = int(item['level'][1])
            
            # Don't allow skipping levels
            if level_num > current_level + 1:
                level_num = current_level + 1
                item['level'] = f'H{level_num}'  # Use uppercase like in sample
                
            current_level = level_num
            validated.append(item)
            
        return validated
