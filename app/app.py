__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import torch
torch.classes.__path__ = []

import streamlit as st
import tempfile
import math
import os
import time
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

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

def start_azure_vm(subscription_id, resource_group, vm_name, tenant_id, client_id, client_secret):
    """Start the Azure VM and return the compute client"""
    try:
        # Use service principal authentication
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        compute_client = ComputeManagementClient(credential, subscription_id)
        
        st.info(f"Starting the Azure VM: {vm_name}...")
        compute_client.virtual_machines.begin_start(resource_group, vm_name)
        
        return compute_client
    except Exception as e:
        st.error(f"Failed to start Azure VM: {str(e)}")
        return None

def display_countdown_timer(seconds):
    """Display a countdown timer in the Streamlit app"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(seconds, 0, -1):
        progress_bar.progress((seconds - i) / seconds)
        status_text.text(f"VM starting up... {i} seconds remaining")
        time.sleep(1)
    
    progress_bar.progress(1.0)
    status_text.text("VM startup completed!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

def process_resume(pdf_path, API_URL, API_KEY, MODEL_NAME, subscription_id, resource_group, vm_name, tenant_id, client_id, client_secret):
    st.info("Processing your resume...")
    
    # Start Azure VM and display countdown timer
    compute_client = start_azure_vm(subscription_id, resource_group, vm_name, tenant_id, client_id, client_secret)
    if compute_client:
        with st.expander("Azure VM Startup", expanded=True):
            st.info("The LLM server needs to start up before processing can begin. This will take 120 seconds.")
            display_countdown_timer(120)
    else:
        st.error("Unable to start the Azure VM. Please try again later.")
        return False
    
    # Notice about processing time
    st.warning("⏳ Note: Extracting information and generating skill recommendations may take 4-5 minutes to complete due to Azure compute limitations. Please be patient.")
    
    with st.spinner("Loading Resume..."):
        resume_text = load_pdf(pdf_path)
    
    with st.spinner("Extracting information from your resume..."):
        data_dict = extract_education_skills_name(resume_text, API_KEY, MODEL_NAME, API_URL)

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

    with st.spinner("Generating skill recommendations..."):
        recommended_skills_json = recommend_skills(
            user_skills=USER_SKILL_LIST,
            user_education=USER_EDUCATION_LIST,
            user_experience=USER_EXPERIENCE_LIST,
            job_postings=retrieved_job_listings,
            API_KEY=API_KEY,
            API_URL= API_URL,
            MODEL_NAME=MODEL_NAME
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
    if not os.getenv("PRODUCTION"):
        load_dotenv()

    API_URL = os.getenv("API_URL", None)
    API_KEY = os.getenv("API_KEY", None)
    MODEL_NAME = os.getenv("MODEL_NAME", None)
    
    # Azure VM configuration
    AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", None)
    AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", None)
    AZURE_VM_NAME = os.getenv("AZURE_VM_NAME", None)
    
    # Azure service principal credentials
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", None)
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", None)
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", None)

    st.set_page_config(page_title="UpskillR", page_icon="📝", layout="wide")
    
    st.title("UpskillR")
    st.write("Upload your resume and get personalized skill recommendations")
    
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Process the resume
        process_resume(
            tmp_path, 
            API_URL=API_URL, 
            API_KEY=API_KEY, 
            MODEL_NAME=MODEL_NAME,
            subscription_id=AZURE_SUBSCRIPTION_ID,
            resource_group=AZURE_RESOURCE_GROUP,
            vm_name=AZURE_VM_NAME,
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET
        )
        
        # Clean up the temporary file
        os.unlink(tmp_path)
    else:
        st.info("Please upload your resume to get started.")

if __name__ == '__main__':
    main()