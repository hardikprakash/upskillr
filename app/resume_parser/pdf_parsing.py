import pymupdf
import os 
import re
import unicodedata
from pathlib import Path


def clean_text(raw_text: str) -> str:
    
    headings = [
        "Education",
        "Work Experience",
        "Experience",
        "Professional Experience",
        "Skills",
        "Projects",
        "Certifications",
        "Achievements",
        "Languages",
        "Interests",
        "Summary",
        "Objective",
        "Publications"
    ]
    
    text = unicodedata.normalize("NFKD", raw_text)

    # Remove invisible Unicode chars (zero-width, non-breaking spaces, etc.)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    # Remove control chars except newlines (\x0A, \x0D) and tabs (\x09)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1f\x7f-\x9f]', '', text)

    # Collapse excessive whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)

    # Replace common bullets with "-"
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]', '\n-', text)
    text = text.replace('•', '\n-')
    text = re.sub(r'\so\s', '\n-', text)

        # Improved heading detection - more aggressive approach
    for heading in headings:
        # Look for common heading formats with stronger pattern matching
        patterns = [
            # ALL CAPS with or without colon
            re.compile(fr'\b{re.escape(heading.upper())}\b:?', re.MULTILINE),
            # Title Case with or without colon
            # re.compile(fr'\b{re.escape(heading.title())}\b:?', re.MULTILINE),
            # Bold formatting often indicated by repeated characters
            re.compile(fr'\b{re.escape(heading.upper())}\s*\n', re.MULTILINE),
        ]
        
        # Apply each pattern
        for pattern in patterns:
            # Replace with newlines before and after
            text = pattern.sub(f'\n\n\\g<0>\n', text)
    
    # Ensure clean separation between sections
    text = re.sub(r'\n{3,}', '\n\n', text)  # No more than double newlines

    # Optional: strip non-ASCII if needed
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()


def load_pdf(path: str) -> str:

    text=""
    doc = pymupdf.open(path)

    for page in doc:
        text += page.get_text()
    
    cleaned = clean_text(text)

    return cleaned

if __name__ == '__main__':
    path = Path(os.getcwd())
    path = path / 'data' / 'areebs_resume.pdf'
    print(load_pdf(path))