import spacy
from parse_pdf import load_pdf
from pathlib import Path
import os
import requests
from llm_prompt import prompt
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
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response.")
            return None
        return result

    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    path = Path(os.getcwd())
    
    path = path / 'data' / 'hardiks_old_resume.pdf'
    resume = load_pdf(path)
    
    # print(extract_name(resume))
    print(extract_education_skills(resume))