"""Text extraction utilities for title and other components."""

class TextExtractor:
    @staticmethod
    def extract_title(spans, top_n_lines=5):
        """
        Extracts the document title by grouping top text spans by Y-position and size.
        Assumes title is in the top 25% of the first page and uses the largest font.
        """
        if not spans:
            return ""

        # Standard US letter page height (can be adjusted based on document)
        page_height = 792
        top_spans = [s for s in spans if s['y_pos'] < page_height * 0.25]

        if not top_spans:
            return ""

        # Group spans by font size
        size_groups = {}
        for span in top_spans:
            size = round(span['size'], 1)
            size_groups.setdefault(size, []).append(span)

        if not size_groups:
            return ""

        # Select the group with the largest font size
        max_size = max(size_groups.keys())
        candidate_spans = sorted(size_groups[max_size], key=lambda s: s['y_pos'])

        # Group spans into lines by similar Y-position
        lines = []
        current_line_y = None
        line_buffer = []

        for span in candidate_spans:
            if current_line_y is None or abs(span['y_pos'] - current_line_y) < 5:
                line_buffer.append(span['text'])
                current_line_y = span['y_pos']
            else:
                lines.append(" ".join(line_buffer))
                line_buffer = [span['text']]
                current_line_y = span['y_pos']

        if line_buffer:
            lines.append(" ".join(line_buffer))

        # Join top N lines with double space (matching target format)
        title = "  ".join(lines[:top_n_lines]).strip()
        return title
