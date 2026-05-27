import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

client = InferenceClient(api_key=HUGGINGFACE_API_KEY)


def extract_resume_info(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured information from resume using Llama LLM.
    Returns: Dictionary with name, skills, experience, strengths, missing_requirements
    NOTE: Name, email, phone are extracted but not sent back to LLM for scoring (PII protection)
    """

    prompt = f"""You are an expert recruiter. Extract the following information from the resume below and return ONLY a valid JSON object with no additional text.

IMPORTANT: Extract ALL information including name/email/phone for internal use.
However, ensure the extraction is accurate for technical fields (skills, experience, education).

Resume:
{resume_text}

Return a JSON object with exactly this structure (no markdown, no extra text):
{{
    "name": "Full name of the person",
    "email": "Email if available, else null",
    "phone": "Phone number if available, else null",
    "skills": ["skill1", "skill2", "skill3"],
    "experience_years": number or null,
    "experience_summary": "Brief summary of experience",
    "strengths": ["strength1", "strength2"],
    "education": "Highest qualification",
    "certifications": ["cert1", "cert2"] or empty array
}}"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.2
        )

        generated_text = response.choices[0].message.content

        # Remove markdown code blocks if present
        if "```json" in generated_text:
            generated_text = generated_text.split("```json")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].split("```")[0].strip()

        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = generated_text[json_start:json_end]
            extracted_data = json.loads(json_str)

            # Ensure required fields exist
            if "name" not in extracted_data:
                extracted_data["name"] = "Unknown"
            if "skills" not in extracted_data:
                extracted_data["skills"] = []
            if "experience_years" not in extracted_data:
                extracted_data["experience_years"] = None
            if "experience_summary" not in extracted_data:
                extracted_data["experience_summary"] = "No summary available"
            if "education" not in extracted_data:
                extracted_data["education"] = "Not specified"
            if "strengths" not in extracted_data:
                extracted_data["strengths"] = []
            if "certifications" not in extracted_data:
                extracted_data["certifications"] = []

            return extracted_data
        else:
            print(f"[ERROR] Could not extract JSON. Raw response: {generated_text[:200]}")
            return {
                "error": "Could not extract JSON from response",
                "raw_response": generated_text[:500]
            }

    except json.JSONDecodeError as je:
        print(f"[ERROR] JSON decode failed: {str(je)}")
        return {"error": f"Invalid JSON in response: {str(je)}"}
    except Exception as e:
        print(f"[ERROR] API request failed: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}
