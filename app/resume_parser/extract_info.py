from resume_parser.parse_pdf import load_pdf
from resume_parser.llm_prompt import system_prompt_content, user_prompt_template
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
import json


load_dotenv()

LLAMA_CPP_URL = os.getenv('LLAMA_CPP_URL')
MODEL_NAME = os.getenv('MODEL_NAME')

def extract_education_skills_name_llama_cpp(resume_text: str):
    """
    Extracts education, experience, and skills from resume text using
    a llama.cpp server with the OpenAI API format.
    """
    headers = {"Content-Type": "application/json"}

    user_message_content = user_prompt_template.format(resume_text=resume_text)

    payload = {
        "model": MODEL_NAME, 
        "messages": [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": user_message_content}
        ],
        "temperature": 0.2,  
        "max_tokens": 2048,
        "stream": False
    }

    try:
        response = requests.post(LLAMA_CPP_URL, headers=headers, json=payload, timeout=120) # Added timeout
        response.raise_for_status()

        response_json = response.json()

        if "choices" in response_json and len(response_json["choices"]) > 0:
            
            message = response_json["choices"][0].get("message", {})
            result_string = message.get("content", "").strip()

            if result_string.startswith("```json"):
                result_string = result_string[7:]
            
            if result_string.endswith("```"):
                result_string = result_string[:-3]
            
            result_string = result_string.strip()

            try:
                result_json = json.loads(result_string.strip())
                # Sucess, return JSON
                return result_json
            
            except json.JSONDecodeError as json_err:
                print(f"Error: Failed to decode JSON response from LLM.")
                print(f"LLM raw output:\n---\n{result_string}\n---")
                print(f"JSONDecodeError: {json_err}")
                return None
            
            except Exception as e:
                 print(f"An unexpected error occurred during JSON parsing: {e}")
                 print(f"LLM raw output:\n---\n{result_string}\n---")
                 return None

        else:
            print("Error: 'choices' not found or empty in the response.")
            print(f"Full Response: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error making request to {LLAMA_CPP_URL}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":

    pdf_file_paths = [load_pdf(Path(os.getcwd()) / 'data' / 'areebs_resume.pdf'), load_pdf(Path(os.getcwd()) / 'data' /'hardiks_resume.pdf')]

    for resume_text in pdf_file_paths:
        print("\n--- Calling Llama.cpp API ---")
        extracted_data = extract_education_skills_name_llama_cpp(resume_text)

        print("\n--- Extracted Data ---")
        if extracted_data:
            # Print formatted JSON
            print(json.dumps(extracted_data, indent=2))
        else:
            print("Failed to extract data.")
