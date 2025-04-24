import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
import math

# Handle PyTorch modules properly for Streamlit
if hasattr(st, "_is_running_with_streamlit"):
    # Import torch first before modifying sys.modules
    import torch
    # Nullify problematic torch modules
    sys.modules["torch._C"] = None
    sys.modules["torch.classes"] = None
    sys.modules["torch._classes"] = None

# Now import the rest of your modules
from resume_parser.parse_pdf import load_pdf
from resume_parser.extract_info import extract_education_skills_name_llama_cpp, recommend_skills_llama_cpp
from rag_pipeline.retriever import JobRetriever
from resume_parser.llm_prompt import skills_gap_prompt_template, JOB_QUERY_PROMPT_TEMPLATE

DEFAULT_PDF_PATH = Path(os.getcwd()) / 'data' /'hardiks_resume.pdf'

def create_grid_layout(items, cols=3):
    """Create a grid layout for displaying items"""
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

def process_resume(pdf_path):
    st.info("Processing your resume...")
    
    # Loading the resume
    with st.spinner("Loading resume..."):
        resume_text = load_pdf(pdf_path)
    
    # Extracting information
    with st.spinner("Extracting information from your resume..."):
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

    # Prepare for job retrieval
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

    # Retrieving similar jobs (hidden from display but still used for recommendations)
    with st.spinner("Finding relevant job matches..."):
        retriever = JobRetriever(top_k=2)
        results = retriever.retrieve_similar_jobs(query_prompt)

    RAG_RETRIEVED_JOB_DATA = []
    for doc in results['documents'][0]:
        RAG_RETRIEVED_JOB_DATA.append(doc)

    # Generating skill recommendations
    with st.spinner("Generating skill recommendations..."):
        recommended_skills_json = recommend_skills_llama_cpp(
            USER_SKILL_LIST,
            USER_EDUCATION_LIST,
            USER_EXPERIENCE_LIST,
            RAG_RETRIEVED_JOB_DATA
        )

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
    st.set_page_config(page_title="UpskillR", page_icon="📝", layout="wide")
    
    st.title("UpskillR - Resume Analyzer")
    st.write("Upload your resume and get personalized skill recommendations")
    
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Process the resume
        process_resume(tmp_path)
        
        # Clean up the temporary file
        os.unlink(tmp_path)
    else:
        st.info("Please upload your resume to get started.")

if __name__ == '__main__':
    main()