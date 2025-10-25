import sys
from pathlib import Path
# Add parent directory to path to import prompts
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import json
from typing import Optional
from prompts import recommend_skills_prompt_template

def build_headers(API_KEY):
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hardikprakash/upskillr",
        "X-Title": "Upskillr"
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers

def recommend_skills(user_skills: list, user_education: list, user_experience: list, job_postings: list, API_KEY: str, MODEL_NAME: str, API_URL: str, FALLBACK_MODEL: Optional[str] = None):
    """
    Given user's skills, education, experience, and relevant job postings,
    calls the LLM to recommend new skills as a JSON list.
    Supports fallback model if primary model fails.
    """
    headers = build_headers(API_KEY)

    # Prepare strings for prompt
    skills_str = ", ".join(user_skills) if user_skills else "Not specified"
    education_str = " | ".join(user_education) if user_education else "Not specified"
    experience_str = " | ".join(user_experience) if user_experience else "Not specified"
    job_postings_str = "\n\n".join(job_postings) if job_postings else "Not available"

    recommend_skills_prompt = recommend_skills_prompt_template.format(
        user_skills=skills_str,
        user_education=education_str,
        user_experience=experience_str,
        job_postings=job_postings_str
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": recommend_skills_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 512,
        "stream": False
    }

    # Try primary model first
    result = _make_llm_request(API_URL, headers, payload, MODEL_NAME)
    
    # If primary model fails and fallback is available, try fallback
    if result is None and FALLBACK_MODEL:
        print(f"Primary model ({MODEL_NAME}) failed. Trying fallback model ({FALLBACK_MODEL})...")
        payload["model"] = FALLBACK_MODEL
        result = _make_llm_request(API_URL, headers, payload, FALLBACK_MODEL)
    
    return result


def _make_llm_request(API_URL: str, headers: dict, payload: dict, model_name: str):
    """
    Helper function to make a request to the LLM API.
    Returns parsed JSON on success, None on failure.
    """
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=360)
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
                # Success, return JSON
                return result_json
            
            except json.JSONDecodeError as json_err:
                print(f"Error: Failed to decode JSON response from LLM ({model_name}).")
                print(f"LLM raw output:\n---\n{result_string}\n---")
                print(f"JSONDecodeError: {json_err}")
                return None
            
            except Exception as e:
                print(f"An unexpected error occurred during JSON parsing ({model_name}): {e}")
                print(f"LLM raw output:\n---\n{result_string}\n---")
                return None
        
        else:
            print(f"Error: 'choices' not found or empty in the response from {model_name}.")
            print(f"Full Response: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        # Check for rate limit errors
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 429:
                print(f"⚠️ OpenRouter API rate limit reached for {model_name}. Please try again later or upgrade your plan.")
                return None
            elif e.response.status_code == 402:
                print(f"⚠️ OpenRouter API credits exhausted for {model_name}. Please add credits to your account.")
                return None
        print(f"Error making request to {API_URL} with {model_name}: {error_msg}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred with {model_name}: {e}")
        return None
