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