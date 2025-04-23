from resume_parser.parse_pdf import load_pdf
from resume_parser.extract_info import extract_education_skills_name_llama_cpp
from rag_pipeline.retriever import JobRetriever
from pathlib import Path
import os

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

    # print(USER_NAME, USER_ROLE, USER_EDUCATION_LIST, USER_EXPERIENCE_LIST, USER_SKILL_LIST)

    JOB_QUERY_PROMPT_TEMPLATE = """
Find job postings suitable for a candidate with the following qualifications:
Target Job Role: {job_role}
Key Skills: {skills}
Educational Background: {education}
Experience: {experience}
"""

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

    # print(query_prompt)

    retriever = JobRetriever()
    results = retriever.retrieve_similar_jobs(query_prompt)

    for i, doc in enumerate(results['documents'][0]):
        print(f"\nResult {i+1}")
        print("Text:", doc)
        print("Metadata:", results['metadatas'][0][i])
if __name__ == '__main__':
    main()