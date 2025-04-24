from resume_parser.parse_pdf import load_pdf
from resume_parser.extract_info import extract_education_skills_name_llama_cpp, recommend_skills_llama_cpp
from rag_pipeline.retriever import JobRetriever
from pathlib import Path
import os
from resume_parser.llm_prompt import skills_gap_prompt_template, JOB_QUERY_PROMPT_TEMPLATE

DEFAULT_PDF_PATH = Path(os.getcwd()) / 'data' /'areebs_resume.pdf'

def main(pdf_path: str= DEFAULT_PDF_PATH):
    resume_text = load_pdf(pdf_path)
    data_dict = extract_education_skills_name_llama_cpp(resume_text)

    USER_NAME = None
    USER_ROLE = None
    USER_EDUCATION_LIST = []
    USER_EXPERIENCE_LIST = []
    USER_SKILL_LIST = []

    if data_dict and data_dict.get('name') is not None:
        USER_NAME = data_dict['name']

    if data_dict and data_dict.get('job_role') is not None:
        USER_ROLE = data_dict['job_role']
    
    if data_dict and data_dict.get('education') and len(data_dict['education']) > 0:
        USER_EDUCATION_LIST = data_dict['education']
    
    if data_dict and data_dict.get('experience') and len(data_dict['experience']) > 0:
        USER_EXPERIENCE_LIST = data_dict['experience']
    
    if data_dict and data_dict.get('skills') and len(data_dict['skills']) > 0:
        USER_SKILL_LIST = data_dict['skills']



    skills_str = ", ".join(USER_SKILL_LIST) if USER_SKILL_LIST else "Not specified"
    education_str = " | ".join(USER_EDUCATION_LIST) if USER_EDUCATION_LIST else "Not specified"
    experience_str = " | ".join(USER_EXPERIENCE_LIST) if USER_EXPERIENCE_LIST else "Not specified"
    job_role_str = USER_ROLE if USER_ROLE else "Not specified"

    query_prompt = JOB_QUERY_PROMPT_TEMPLATE.format(
        job_role=job_role_str,
        skills=skills_str,
        education=education_str,
        experience=experience_str
    )

    retriever = JobRetriever(top_k=2)
    results = retriever.retrieve_similar_jobs(query_prompt)

    RAG_RETRIEVED_JOB_DATA = []
    for doc in results['documents'][0]:
        RAG_RETRIEVED_JOB_DATA.append(doc)

    recommended_skills_json = recommend_skills_llama_cpp(
        USER_SKILL_LIST,
        USER_EDUCATION_LIST,
        USER_EXPERIENCE_LIST,
        RAG_RETRIEVED_JOB_DATA
    )

    print(f"Hey {USER_NAME}, you should learn these skills:")
    for i in recommended_skills_json['recommended_skills']:
        print(i)

if __name__ == '__main__':
    main()