__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import torch
torch.classes.__path__ = []

import streamlit as st
import tempfile
import math
import os
from dotenv import load_dotenv

from resume_parser.pdf_parsing import load_pdf
from resume_parser.detail_extraction import extract_education_skills_name
from rag_components.retriever import JobRetriever
from rag_components.generator import recommend_skills

def create_grid_layout(items, cols=3):
    rows = math.ceil(len(items) / cols)
    grid = []
    item_idx = 0
    
    for _ in range(rows):
        row_items = []
        for _ in range(cols):
            if item_idx < len(items):
                row_items.append(items[item_idx])
                item_idx += 1
            else:
                row_items.append("")
        grid.append(row_items)
    
    return grid

def process_resume(pdf_path, API_URL, API_KEY, MODEL_NAME, FALLBACK_MODEL):
    st.info("Processing your resume...")
    
    with st.spinner("Loading Resume..."):
        try:
            resume_text = load_pdf(pdf_path)
            if not resume_text or len(resume_text.strip()) < 50:
                st.error("Failed to extract text from PDF. The file might be:")
                st.error("• Empty or corrupted")
                st.error("• Password protected")
                st.error("• An image-based PDF (needs OCR)")
                st.info("Please ensure your resume is a text-based PDF with at least 50 characters.")
                return False
        except Exception as e:
            st.error(f"❌ Error loading PDF file: {str(e)}")
            st.error("Please ensure the file is a valid PDF document.")
            return False
    
    with st.spinner("Extracting information from your resume..."):
        data_dict = extract_education_skills_name(resume_text, API_KEY, MODEL_NAME, API_URL, FALLBACK_MODEL)
    
    # Check if extraction failed
    if data_dict is None:
        st.error("❌ Failed to extract information from your resume. This could be due to:")
        st.error("• OpenRouter API rate limits reached")
        st.error("• API credits exhausted") 
        st.error("• Network connectivity issues")
        st.info("Please try again later or check your OpenRouter API status at https://openrouter.ai/")
        return False

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

    
    # Display extracted information
    st.subheader("Your Resume Information")
    st.write(f"**Name:** {USER_NAME if USER_NAME else 'Not specified'}")
    st.write(f"**Job Role:** {USER_ROLE if USER_ROLE else 'Not specified'}")
    
    if USER_EDUCATION_LIST:
        st.write("**Education:**")
        for edu in USER_EDUCATION_LIST:
            st.write(f"- {edu}")
    
    if USER_EXPERIENCE_LIST:
        st.write("**Experience:**")
        for exp in USER_EXPERIENCE_LIST:
            st.write(f"- {exp}")
    
    # Display skills in a grid layout
    if USER_SKILL_LIST:
        st.write("**Skills:**")
        skill_grid = create_grid_layout(USER_SKILL_LIST, cols=4)
        
        for row in skill_grid:
            cols = st.columns(4)
            for i, skill in enumerate(row):
                if skill:  # Skip empty cells
                    cols[i].markdown(f"• {skill}")
    
    skills_str = ", ".join(USER_SKILL_LIST) if USER_SKILL_LIST else "Not specified"
    education_str = " | ".join(USER_EDUCATION_LIST) if USER_EDUCATION_LIST else "Not specified"
    experience_str = " | ".join(USER_EXPERIENCE_LIST) if USER_EXPERIENCE_LIST else "Not specified"
    job_role_str = USER_ROLE if USER_ROLE else "Not specified"

    with st.spinner("Finding relevant job matches..."):
        try:
            retriever = JobRetriever(top_k=5)
        
            results = retriever.retrieve_similar_jobs(
                job_role_str=job_role_str,
                skills_str=skills_str,
                education_str=education_str,
                experience_str=experience_str
            )
        except Exception as e:
            st.warning(f"Could not retrieve job matches: {str(e)}")
            st.info("Continuing with skill recommendations based on your profile...")
            results = {'documents': [[]]}  # Empty results to continue
    
    retrieved_job_listings = []

    if results and 'documents' in results and len(results['documents']) > 0:
        for doc in results['documents'][0]:
            retrieved_job_listings.append(doc)
    
    # Warn if no jobs found (but continue with recommendation)
    if not retrieved_job_listings:
        st.warning("No matching job postings found in the database. Recommendations will be based on your profile only.")

    with st.spinner("Generating skill recommendations..."):
        recommended_skills_json = recommend_skills(
            user_skills=USER_SKILL_LIST,
            user_education=USER_EDUCATION_LIST,
            user_experience=USER_EXPERIENCE_LIST,
            job_postings=retrieved_job_listings,
            API_KEY=API_KEY,
            API_URL= API_URL,
            MODEL_NAME=MODEL_NAME,
            FALLBACK_MODEL=FALLBACK_MODEL
        )
    
    # Check if recommendation generation failed
    if recommended_skills_json is None:
        st.error("❌ Failed to generate skill recommendations. This could be due to:")
        st.error("• OpenRouter API rate limits reached")
        st.error("• API credits exhausted")
        st.error("• Network connectivity issues")
        st.info("Please try again later or check your OpenRouter API status at https://openrouter.ai/")
        return False
    
    # Display recommended skills in a grid layout with colored boxes
    st.subheader(f"Recommended Skills for {USER_NAME if USER_NAME else 'You'}")
    
    if recommended_skills_json and 'recommended_skills' in recommended_skills_json:
        rec_skills = recommended_skills_json['recommended_skills']
        rec_skills_grid = create_grid_layout(rec_skills, cols=3)
        
        for row in rec_skills_grid:
            cols = st.columns(3)
            for i, skill in enumerate(row):
                if skill:  # Skip empty cells
                    with cols[i]:
                        st.info(f"**{skill}**")

    return True

def main():
    if not os.getenv("PRODUCTION"):
        load_dotenv()

    API_URL = os.getenv("API_URL", None)
    API_KEY = os.getenv("OPENROUTER_API_KEY", None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL_NAME", None)

    st.set_page_config(page_title="UpskillR", page_icon="📝", layout="wide")
    
    st.title("UpskillR")
    st.write("Upload your resume and get personalized skill recommendations")
    
    # Validate required environment variables
    if not API_KEY or not API_URL or not MODEL_NAME:
        st.error("**Configuration Error**: Missing required environment variables!")
        st.error("Please ensure the following are set in your `.env` file:")
        if not API_KEY:
            st.error("• `OPENROUTER_API_KEY` - Your OpenRouter API key")
        if not API_URL:
            st.error("• `API_URL` - OpenRouter API endpoint")
        if not MODEL_NAME:
            st.error("• `MODEL_NAME` - Primary model name")
        st.info("Copy `.env.example` to `.env` and add your API key. See QUICKSTART.md for help.")
        return
    
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Process the resume
            process_resume(
                tmp_path, 
                API_URL=API_URL, 
                API_KEY=API_KEY, 
                MODEL_NAME=MODEL_NAME,
                FALLBACK_MODEL=FALLBACK_MODEL
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.error("Please try again or contact support if the issue persists.")
        finally:
            # Clean up the temporary file (always executes)
            try:
                os.unlink(tmp_path)
            except Exception:
                pass  # Ignore cleanup errors
    else:
        st.info("Please upload your resume to get started.")

if __name__ == '__main__':
    main()