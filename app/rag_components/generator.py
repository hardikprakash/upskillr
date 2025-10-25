import sys
from pathlib import Path
# Add parent directory to path to import prompts
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import SkillRecommendations
from openai import OpenAI
import json
from typing import Optional
from prompts import recommend_skills_prompt_template

def recommend_skills(user_skills: list, user_education: list, user_experience: list, job_postings: list, API_KEY: str, MODEL_NAME: str, API_URL: str, FALLBACK_MODEL: Optional[str] = None):
    """
    Given user's skills, education, experience, and relevant job postings,
    calls the LLM to recommend new skills as a JSON list.
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

    # Try primary model first
    result = _make_llm_request(client, MODEL_NAME, recommend_skills_prompt)
    
    # If primary model fails and fallback is available, try fallback
    if result is None and FALLBACK_MODEL:
        print(f"Primary model ({MODEL_NAME}) failed. Trying fallback model ({FALLBACK_MODEL})...")
        result = _make_llm_request(client, FALLBACK_MODEL, recommend_skills_prompt)
    
    return result


def _make_llm_request(client: OpenAI, model_name: str, user_prompt: str):
    """
    Helper function to make a request to the LLM API using OpenAI client.
    Returns parsed SkillRecommendations on success, None on failure.
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # Enforce JSON response
            temperature=0.2,
            max_tokens=1024,  # Shorter for recommendations
            timeout=360
        )

        result_string = response.choices[0].message.content.strip()

        try:
            # Parse JSON string to dict
            result_dict = json.loads(result_string)
            
            # Validate with Pydantic model
            skill_recommendations = SkillRecommendations(**result_dict)
            
            # Return as dict for backward compatibility
            return skill_recommendations.model_dump()
            
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
