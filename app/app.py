from resume_parser.parse_pdf import load_pdf
from resume_parser.extract_info import extract_education_skills_name_llama_cpp
from rag_pipeline.retriever import JobRetriever
from pathlib import Path
import os

DEFAULT_PDF_PATH = Path(os.getcwd()) / 'data' /'siddharthas_resume.pdf'

def main(pdf_path: str= DEFAULT_PDF_PATH):
    resume_text = load_pdf(pdf_path)
    # print(pdf_text)

    data_dict = extract_education_skills_name_llama_cpp(resume_text)
    # print(type(data_dict), "\n", data_dict)

    print("Hi, {data_dict[name]}")
    
    if data_dict[job_role] is not None:
        print("Here is your (inferred) preferred job role: {data_dict[job_role]}")
    else:
        print("Couldn't infer your job role.")

    if 

if __name__ == '__main__':
    main()