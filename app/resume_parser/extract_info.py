try:
    from resume_parser.parse_pdf import load_pdf
    from resume_parser.llm_prompt import system_prompt_content, user_prompt_template
    from resume_parser.llm_prompt import skills_gap_prompt_template
except ModuleNotFoundError:
    from llm_prompt import system_prompt_content, user_prompt_template
    from llm_prompt import skills_gap_prompt_template
    from parse_pdf import load_pdf

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

def recommend_skills_llama_cpp(user_skills, user_education, user_experience, job_postings):
    """
    Given user's skills, education, experience, and relevant job postings,
    calls the LLM to recommend new skills as a JSON list.
    """
    headers = {"Content-Type": "application/json"}

    # Prepare strings for prompt
    skills_str = ", ".join(user_skills) if user_skills else "Not specified"
    education_str = " | ".join(user_education) if user_education else "Not specified"
    experience_str = " | ".join(user_experience) if user_experience else "Not specified"
    job_postings_str = "\n\n".join(job_postings) if job_postings else "Not available"

    user_message_content = skills_gap_prompt_template.format(
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
        response = requests.post(LLAMA_CPP_URL, headers=headers, json=payload, timeout=60)
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
        print(f"Error making request to {LLAMA_CPP_URL}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":

    # pdf_file_paths = [load_pdf(Path(os.getcwd()) / 'data' / 'areebs_resume.pdf'), load_pdf(Path(os.getcwd()) / 'data' /'hardiks_resume.pdf')]

    # for resume_text in pdf_file_paths:
        
    #     print("\n--- Calling Llama.cpp API ---")
    #     extracted_data = extract_education_skills_name_llama_cpp(resume_text)
    #     print("\n--- Extracted Data ---")
        
    #     if extracted_data:
    #         # Print formatted JSON
    #         print(json.dumps(extracted_data, indent=2))
    #     else:
    #         print("Failed to extract data.")


    user_skills = ['C', 'C++', 'JavaScript', 'TypeScript', 'Python', 'ReactJS', 'NextJS', 'Astro', 'ExpressJS', 'TailwindCSS', 'NodeJS', 'Flask', 'Docker', 'GIT', 'PostgreSQL', 'MySQL', 'MongoDB', 'Firebase', 'Prisma', 'Figma', 'Adobe Photoshop', 'Adobe Illustrator']
    user_education = ["B.Tech., Galgotias College of Engineering and Technology, Greater Noida, India (November 2021 - July 2025), GPA: 7.12', '10+2, Kiddy Public School, Patna, India (April 2020 - April 2021), GPA: 6.5", "Matriculation, St. Karen's Secondary School, Patna, India (April 2018 - April 2019), GPA: 8.4"]
    user_experience = ["Full Stack Developer (Intern) at Tapti (Nov 2024 - Present): Joined as an early engineer and built the product from scratch, now nearing release. Worked with NestJS, Next.js, and Serverless Functions to develop APIs and the platform. Developed APIs for social media integration.", "Freelancer - Web Development Projects (July 2022 - Present): Built and deployed responsive websites for businesses using Next.js, Astro.js, and TailwindCSS. Redesigned Prakhar Travels website, improving reach by 20% and enhancing UI/UX."]
    job_postings = ["Manager/Senior Manager, Strategic Partnerships & Business Development | BUSINESS-DEVELOPMENT: to get the best candidate experience, please consider applying for a maximum of 3 roles within 12 months to ensure you are not duplicating efforts.job categorydevelopment & strategyjob detailsabout salesforcewe're salesforce, the customer company, inspiring the future of business with ai+ data +crm. leading with our core values, we help companies across every industry blaze new trails and connect with customers in a whole new way. and, we empower you to be a trailblazer, too - driving your performance and career growth, charting new paths, and improving the state of the world. if you believe in business as the greatest platform for change and in companies doing well and doing good - you've come to the right place.about salesforcewe're salesforce, the customer company, inspiring the future of business with ai+ data +crm. leading with our core values, we help companies across every industry blaze new trails and connect with customers in a whole new way. and, we empower you to be a trailblazer, too - driving your performance and career growth, charting new paths, and improving the state of the world. if you believe in business as the greatest platform for change and in companies doing well and doing good - you've come to the right place.role descriptionthe global technology partnerships team is looking for a dedicated individual to join the product business development team. this is a unique opportunity to join a centralized team that develops and drives new strategic partnership initiatives aligned to our top corporate and product priorities across all of salesforce. these strategic partnerships and initiatives drive revenue, increase customer success, deliver on our product roadmap, elevate our brand, and differentiate our company.as a member of the product business development team, you will be a highly visible leader responsible for generating, managing, and driving some of salesforce's most complex and high-impact partnership activities. this includes generating partnership strategy, leading financial analysis, and handling relationships and negotiations for partnership deals which can be non-traditional in nature, require sophisticated stakeholder management, and have broad strategic implications for salesforce. the role will require concurrently driving multiple deals or initiatives that can involve many parts of our product and technology portfolio and require working seamlessly with cross-functional stakeholders in product, engineering, marketing, distribution, procurement, finance, operations and legal.your impactbuild out new partnership strategies, financial analyses, product strategies, and integration plans for our product business development initiativesevangelize strategies, both quantitatively and"]

    skills_str = ", ".join(user_skills) if user_skills else "Not specified"
    education_str = " | ".join(user_education) if user_education else "Not specified"
    experience_str = " | ".join(user_experience) if user_experience else "Not specified"
    job_postings_str = "\n\n".join(job_postings) if job_postings else "Not available"

    user_message_content = skills_gap_prompt_template.format(
        user_skills=skills_str,
        user_education=education_str,
        user_experience=experience_str,
        job_postings=job_postings_str
    )

    # print(user_message_content)

    print("\n--- Calling Llama.cpp API ---")
    extracted_recommended_skills = extract_education_skills_name_llama_cpp(user_message_content)
    print("\n--- Extracted Data ---")

    if extracted_recommended_skills:
        # Print formatted JSON
        print(json.dumps(extracted_recommended_skills, indent=2))
    else:
        print("Failed to extract data.")