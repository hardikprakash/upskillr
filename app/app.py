from resume_parser.pdf_parsing import load_pdf
from resume_parser.detail_extraction import extract_education_skills_name
from rag_components.retriever import JobRetriever
from rag_components.generator import recommend_skills


from pathlib import Path
import os
from dotenv import load_dotenv

def main():
    if not os.getenv("PRODUCTION"):
        load_dotenv()

    API_URL = os.getenv("API_URL", None)
    API_KEY = os.getenv("API_KEY", None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)

    
    resume_text = load_pdf(Path(os.getcwd()) / 'data' / 'hardiks_resume.pdf')

    current_skills_dict = extract_education_skills_name(resume_text, API_KEY, MODEL_NAME, API_URL)

    USER_NAME = None
    USER_ROLE = None
    USER_EDUCATION_LIST = []
    USER_EXPERIENCE_LIST = []
    USER_SKILL_LIST = []

    if current_skills_dict and current_skills_dict.get('name') is not None:
        USER_NAME = current_skills_dict['name']

    if current_skills_dict and current_skills_dict.get('job_role') is not None:
        USER_ROLE = current_skills_dict['job_role']
    
    if current_skills_dict and current_skills_dict.get('education') and len(current_skills_dict['education']) > 0:
        USER_EDUCATION_LIST = current_skills_dict['education']
    
    if current_skills_dict and current_skills_dict.get('experience') and len(current_skills_dict['experience']) > 0:
        USER_EXPERIENCE_LIST = current_skills_dict['experience']
    
    if current_skills_dict and current_skills_dict.get('skills') and len(current_skills_dict['skills']) > 0:
        USER_SKILL_LIST = current_skills_dict['skills']

    skills_str = ", ".join(USER_SKILL_LIST) if USER_SKILL_LIST else "Not specified"
    education_str = " | ".join(USER_EDUCATION_LIST) if USER_EDUCATION_LIST else "Not specified"
    experience_str = " | ".join(USER_EXPERIENCE_LIST) if USER_EXPERIENCE_LIST else "Not specified"
    job_role_str = USER_ROLE if USER_ROLE else "Not specified"

    retriever = JobRetriever(top_k=5)
    
    results = retriever.retrieve_similar_jobs(
        job_role_str=job_role_str,
        skills_str=skills_str,
        education_str=education_str,
        experience_str=experience_str
    )

    retrieved_job_listings = []

    for doc in results['documents'][0]:
        retrieved_job_listings.append(doc)

    recommended_skills_json = recommend_skills(
        user_skills=USER_SKILL_LIST,
        user_education=USER_EDUCATION_LIST,
        user_experience=USER_EXPERIENCE_LIST,
        job_postings=retrieved_job_listings,
        API_KEY=API_KEY,
        API_URL= API_URL,
        MODEL_NAME=MODEL_NAME
    )

    print(recommended_skills_json['recommended_skills'])



if __name__ == '__main__':
    main()