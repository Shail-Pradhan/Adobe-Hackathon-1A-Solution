"""Common text patterns used for identifying form fields and headings."""

# Form field patterns
FORM_PATTERNS = [
    r'^signature\s+of\b',  # Signature lines
    r'^designation\b',      # Designation lines
    r'^\s*date\s*:?\s*$',  # Date fields
    r'^name\s*:?$',        # Name fields
    r'^address\s*:?$',     # Address fields
    r'^place\s*:?$',       # Place fields
    r'^remarks?\s*:?$',    # Remarks fields
    r'^phone\s*(no\.)?\s*:?$',  # Phone number fields
    r'^email\s*:?$',       # Email fields
    r'^\s*department\s*:?$',  # Department fields
    r'^approved\s+by\b',   # Approval lines
    r'^verified\s+by\b',   # Verification lines
    r'^submitted\s+by\b',  # Submission lines
]

# Non-title patterns
SKIP_TITLE_PATTERNS = [
    r'^\d+$',  # Just numbers
    r'^page\s+\d+$',  # Page numbers
    r'^\s*$',  # Empty strings
    r'^[©®™]',  # Copyright symbols etc.
]

# Heading patterns with their levels
NUMBERED_HEADING_PATTERNS = [
    (r'^(\d+\.)\s+([A-Za-z].{3,})', 1),  # "1. Title" (must have actual text)
    (r'^(\d+\.\d+\.?)\s+([A-Za-z].{3,})', 2),  # "1.1 Title"
    (r'^(\d+\.\d+\.\d+\.?)\s+([A-Za-z].{3,})', 3),  # "1.1.1 Title"
    (r'^(\d+\.\d+\.\d+\.\d+\.?)\s+([A-Za-z].{3,})', 4),  # "1.1.1.1 Title"
]
