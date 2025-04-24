
from app.resume_parser.pdf_parsing import load_pdf
from app.prompts import user_resume_template, system_prompt, recommended_skills_prompt_template
from pathlib import Path
# import os
import requests
import json

def build_headers(API_KEY):
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers

def extract_education_skills_name_llama_cpp(resume_text: str, API_KEY: str, MODEL_NAME:str, API_URL: str):
    """
    Extracts education, experience, and skills from resume text using
    a llama.cpp server with the OpenAI API format.
    """
    headers = build_headers(API_KEY)

    user_resume_prompt = user_resume_template.format(resume_text=resume_text)

    payload = {
        "model": MODEL_NAME, 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_resume_prompt}
        ],
        "temperature": 0.2,  
        "max_tokens": 2048,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
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

def recommend_skills_llama_cpp(user_skills: list, user_education: list, user_experience: list, job_postings: list, API_KEY: str, MODEL_NAME:str, API_URL: str):
    """
    Given user's skills, education, experience, and relevant job postings,
    calls the LLM to recommend new skills as a JSON list.
    """
    headers = build_headers()

    # Prepare strings for prompt
    skills_str = ", ".join(user_skills) if user_skills else "Not specified"
    education_str = " | ".join(user_education) if user_education else "Not specified"
    experience_str = " | ".join(user_experience) if user_experience else "Not specified"
    job_postings_str = "\n\n".join(job_postings) if job_postings else "Not available"

    user_message_content = recommended_skills_prompt_template.format(
        user_skills=skills_str,
        user_education=education_str,
        user_experience=experience_str,
        job_postings=job_postings_str
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": user_message_content}
        ],
        "temperature": 0.2,
        "max_tokens": 512,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
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
                result_json = json.loads(result_string)
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
        print(f"Error making request to {API_URL}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None