
import sys
from pathlib import Path
# Add parent directory to path to import prompts
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompts import user_resume_template, system_prompt
from models import ResumeData
from openai import OpenAI
from typing import Optional
import json

def extract_education_skills_name(resume_text: str, API_KEY: str, MODEL_NAME: str, API_URL: str, FALLBACK_MODEL: Optional[str] = None):
    """
    Extracts education, experience, and skills from resume text using
    OpenRouter API with OpenAI client and structured outputs.
    Supports fallback model if primary model fails.
    """
    client = OpenAI(
        base_url=API_URL.replace("/chat/completions", ""),  # Remove endpoint from base URL
        api_key=API_KEY,
        default_headers={
            "HTTP-Referer": "https://github.com/hardikprakash/upskillr",
            "X-Title": "Upskillr"
        }
    )

    user_resume_prompt = user_resume_template.format(resume_text=resume_text)

    # Try primary model first
    result = _make_llm_request(client, MODEL_NAME, system_prompt, user_resume_prompt)
    
    # If primary model fails and fallback is available, try fallback
    if result is None and FALLBACK_MODEL:
        print(f"Primary model ({MODEL_NAME}) failed. Trying fallback model ({FALLBACK_MODEL})...")
        result = _make_llm_request(client, FALLBACK_MODEL, system_prompt, user_resume_prompt)
    
    return result


def _make_llm_request(client: OpenAI, model_name: str, system_prompt: str, user_prompt: str):
    """
    Helper function to make a request to the LLM API using OpenAI client.
    Returns parsed ResumeData on success, None on failure.
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # Enforce JSON response
            temperature=0.2,
            max_tokens=4096,
            timeout=360
        )

        result_string = response.choices[0].message.content.strip()

        try:
            # Parse JSON string to dict
            result_dict = json.loads(result_string)
            
            # Validate with Pydantic model
            resume_data = ResumeData(**result_dict)
            
            # Return as dict for backward compatibility
            return resume_data.model_dump()
            
        except json.JSONDecodeError as json_err:
            print(f"Error: Failed to decode JSON response from LLM ({model_name}).")
            print(f"LLM raw output:\n---\n{result_string}\n---")
            print(f"JSONDecodeError: {json_err}")
            return None
        
        except Exception as e:
            print(f"An unexpected error occurred during JSON parsing ({model_name}): {e}")
            print(f"LLM raw output:\n---\n{result_string}\n---")
            return None

    except Exception as e:
        error_msg = str(e)
        
        # Check for specific error types
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            print(f"⚠️ OpenRouter API rate limit reached for {model_name}. Please try again later or upgrade your plan.")
        elif "insufficient" in error_msg.lower() or "402" in error_msg:
            print(f"⚠️ OpenRouter API credits exhausted for {model_name}. Please add credits to your account.")
        elif "400" in error_msg:
            print(f"⚠️ Bad request for {model_name}: {error_msg}")
        else:
            print(f"Error making request with {model_name}: {error_msg}")
        
        return None
