import pymupdf
import os 
import re
import unicodedata
from pathlib import Path


def clean_text(raw_text: str) -> str:
    text = unicodedata.normalize("NFKD", raw_text)

    # Remove invisible Unicode chars (zero-width, non-breaking spaces, etc.)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Replace common bullets with "-"
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]', '-', text)
    text = text.replace('•', '-')

    # Collapse excessive whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)

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
    print(str(path))
    path = path / 'data' / 'hardiks_old_resume.pdf'
    print(load_pdf(path))