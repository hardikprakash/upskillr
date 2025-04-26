from resume_parser.pdf_parsing import load_pdf
from resume_parser.detail_extraction import extract_education_skills_name
from rag_components import retriever, generator

from pathlib import Path
import os

def main():
    resume_text = load_pdf(Path(os.getcwd()) / 'data' / 'areebs_resume.pdf')
    # print(resume_text)

    

if __name__ == '__main__':
    main()