import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

client = InferenceClient(api_key=HUGGINGFACE_API_KEY)


def analyze_resume_vs_jd(extracted_resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Compare extracted resume data with job description.
    Generates score, interview questions or rejection reasons based on score.
    If score > 70%: Returns advanced interview questions
    If score <= 70%: Returns rejection reasons and improvement suggestions
    """

    resume_json = json.dumps(extracted_resume, indent=2)

    prompt = f"""You are an expert HR analyst. Analyze the following resume against the job description. Calculate a match score and provide appropriate feedback.

RESUME DATA:
{resume_json}

JOB DESCRIPTION:
{job_description}

ANALYSIS INSTRUCTIONS:
1. Calculate match_score (0-100) based on:
   - Skills match (does resume have required skills?)
   - Experience match (does resume have required years/experience?)
   - Education match (does resume meet education requirements?)

2. IF match_score > 70:
   - Set is_qualified = true
   - Generate 5 ADVANCED technical interview questions (very specific to the role)
   - Leave rejection_reasons and improvement_suggestions as empty arrays

3. IF match_score <= 70:
   - Set is_qualified = false
   - List 2-3 rejection_reasons (specific gaps)
   - List 3-4 improvement_suggestions (actionable steps to improve)
   - Leave interview_questions as empty array

Return ONLY valid JSON (no markdown, no explanations):
{{
    "match_score": <0-100 number>,
    "score_breakdown": {{
        "skills_match": <0-100>,
        "experience_match": <0-100>,
        "education_match": <0-100>
    }},
    "is_qualified": <true or false>,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "interview_questions": ["Q1", "Q2", "Q3", "Q4", "Q5"] or [],
    "rejection_reasons": ["reason1", "reason2"] or [],
    "improvement_suggestions": ["suggestion1", "suggestion2", "suggestion3"] or [],
    "analysis_summary": "Brief summary of match"
}}"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )

        generated_text = response.choices[0].message.content

        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = generated_text[json_start:json_end]
            analysis_data = json.loads(json_str)
            return analysis_data
        else:
            return {"error": "Could not extract JSON from response", "raw_response": generated_text}

    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}
