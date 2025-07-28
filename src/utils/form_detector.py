"""Form structure detection utilities."""
import re

class FormDetector:
    @staticmethod
    def is_table_block(block):
        """Detect if a block represents tabular or form content."""
        if "lines" not in block:
            return False
            
        # Check for potential heading in a box
        has_heading_text = False
        has_box_indicator = False
        total_spans = 0
        
        for line in block["lines"]:
            for span in line["spans"]:
                total_spans += 1
                text = span['text'].strip()
                # Check for form field indicators
                if re.match(r'^\d+[.:)]?\s*\w+', text):  # Numbered heading pattern
                    has_heading_text = True
                if re.match(r'^[_\.]{3,}$', text):  # Underline or dots
                    has_box_indicator = True
                    
        # If block looks like a heading in a box, don't treat as table
        if has_heading_text and total_spans <= 3:
            return False
                    
        # More detailed table structure check
        line_ypos = []
        line_heights = set()
        col_xpos = set()
        
        # Collect y-positions and x-positions
        for line in block["lines"]:
            y_pos = line["bbox"][1]  # Top y-coordinate
            height = line["bbox"][3] - line["bbox"][1]  # Height
            line_ypos.append(y_pos)
            line_heights.add(round(height, 1))
            
            # Collect x-positions of spans
            for span in line["spans"]:
                col_xpos.add(round(span["bbox"][0], 1))  # Left x-coordinate
                
        if len(line_ypos) < 2:
            return False
            
        # Check for consistent row heights
        row_spacing = []
        for i in range(1, len(line_ypos)):
            spacing = line_ypos[i] - line_ypos[i-1]
            if spacing > 0:  # Only consider positive spacing
                row_spacing.append(round(spacing, 1))
                
        # Consider the block's position on the page
        y_pos = block["bbox"][1]
        page_height = 792  # Standard letter page height
        is_footer = y_pos > page_height * 0.85  # Skip if in footer area
        
        # Detect form/table characteristics:
        # 1. Regular row spacing
        # 2. Consistent line heights
        # 3. Regular column positions
        # 4. More than one column
        has_regular_rows = len(set(row_spacing)) <= 2  # Allow max 2 different row spacings
        has_regular_heights = len(line_heights) <= 2  # Allow max 2 different line heights
        has_columns = len(col_xpos) >= 2  # At least 2 columns
        
        return (has_regular_rows and has_regular_heights and has_columns) or is_footer
