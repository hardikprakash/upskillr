import spacy
from parse_pdf import load_pdf
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_URL')

# print(OLLAMA_URL)

nlp = spacy.load('en_core_web_sm')

def extract_name(text: str) -> str:
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent
            break
    return name


def extract_education_skills(resume_text: str):
    
    HEADERS = {"Content-Type": "application/json"}

    prompt = f"""
    You are an expert assistant that extracts structured information from resumes. Your task is to extract the following fields:

    1. education – list of degrees, institutions, and years
    2. experience – list of professional or academic experiences
    3. skills – list of technical and soft skills mentioned

    Return your output in this JSON format:
    {{
      "education": [...],
      "experience": [...],
      "skills": [...]
    }}

    Here are a few examples:

    Example 1:
    Resume:
    "John Doe completed his B.Tech in Computer Science from IIT Delhi in 2020. He worked at Google as a Software Engineer from 2020 to 2023. His skills include Python, JavaScript, and Kubernetes."
    Output:
    {{
      "education": ["B.Tech in Computer Science, IIT Delhi (2020)"],
      "experience": ["Software Engineer at Google (2020–2023)"],
      "skills": ["Python", "JavaScript", "Kubernetes"]
    }}

    Example 2:
    Resume:
    "Jane Smith studied MBA at Stanford in 2018. She worked at Amazon in product management. She's skilled in SQL, Excel, team leadership, and agile workflows."
    Output:
    {{
      "education": ["MBA, Stanford University (2018)"],
      "experience": ["Product Manager at Amazon"],
      "skills": ["SQL", "Excel", "Team Leadership", "Agile Workflows"]
    }}

    Example 3:
    Resume:
    "Hardik Prakash hardikprakash.official@gmail.com   +918130841139   Delhi, India   GitHub WORK EXPERIENCE FutureSoft June 2024   January 2025 SDE Intern Remote 
-FutureSoft India is a software consulting and technology services company specializing in industry-specific solutions, strategic outsourcing and integration services. 
-Anti-Poaching Surveillance System:
-Contributed to developing a forest surveillance system by integrating YOLOv8 for real-time detection of humans and vehicles and building a React.js dashboard for live streams and automated alerts. Designed efficient backend APIs with FastAPI and implemented a lightweight logging system with SQLite to store alert history and system events.
-Stack: JavaScript (React); Python (FastAPI + Flask); YOLOv8 (Object Recognition); SQLite 
-Developed predictive models to analyze power usage trends for grid companies using Pandas, NumPy, and SciKit-Learn. Created interactive data visualizations with Seaborn and deployed APIs to provide real-time insights, achieving a 5% improvement in forecast accuracy.
-Stack: Python (PANDAS + NumPy + Seaborn +SciKit Learn) EDUCATION A.P.J. Abdul Kalam University 2021- 2025 B. Tech, Computer Science and Artificial Intelligence Noida, India 
-Maintained the ICAC3N Portal, facilitating registrations for over 1,000 participants attending the International Conference on Advances in Computing, Communication Control, and Networking. 
-Active member of GCELI2 (Galgotias Center for Experiential Learning, Innovation, and Incubation), collaborating on innovative projects and prototypes. 
-Participated in Hackathons -Technovation Hackathon (Sharda University), Code-O-Fiesta Hackathon (ITS College), Hack-a-preneur Hackathon (NSUT). CERTIFICATIONS, SKILLS & INTERESTS 
-Certifications:
-Deep Learning Specialization (Coursera): 
-Convolutional Neural Networks 
-Sequence Models 
-Improving Deep Neural Networks: Hyperparameter Tuning, Regularization and Optimization 
-Structuring Machine Learning Projects 
-Neural Networks and Deep Learning
-Microsoft Certified (Microsoft): 
-Azure Fundamentals 
-Azure Data Fundamentals 
-Skills:
-Data Science & ML Tools: Pandas, NumPy, SciKit-Learn, Seaborn, YOLOv8
-Backend & Dev Tools: FastAPI, Flask, PostgreSQL, Microsoft Azure, Supabase
-Frontend & Web Development: React, Next.js, Prisma, NextAuth.js 
-Interests: Music; Reading; Homelab; Hiking; Cooking"
    Output:
    {{
      "education": ["B. Tech, A.P.J. Abdul Kalam University (2025)"],
      "experience": ["Product Manager at Amazon"],
      "skills": ["SQL", "Excel", "Team Leadership", "Agile Workflows"]
    }}

    Now extract the information from this resume:
    {resume_text}
    """
    
    payload = {
        "model": "dolphin3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, headers=HEADERS, data=json.dumps(payload))

    if response.status_code == 200:
        # print(response)
        response_json = response.json()
        result = response_json.get("response", "").strip()
        print(result)
        # ADD RETURN VALUE


    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    path = Path(os.getcwd())
    
    path = path / 'data' / 'hardiks_old_resume.pdf'
    resume = load_pdf(path)
    
    # print(extract_name(resume))
    print(extract_education_skills(resume))