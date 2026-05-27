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

    NOTE: Only sends non-PII data to LLM (no name, email, phone)
    """

    # Build anonymized candidate profile (no PII)
    anonymized_profile = {
        "skills": extracted_resume.get("skills", []),
        "experience_years": extracted_resume.get("experience_years"),
        "experience_summary": extracted_resume.get("experience_summary"),
        "education": extracted_resume.get("education"),
        "strengths": extracted_resume.get("strengths", []),
        "certifications": extracted_resume.get("certifications", [])
    }

    anonymized_json = json.dumps(anonymized_profile, indent=2)

    prompt = f"""You are an expert technical interviewer and hiring manager. Your role is to:
1. Analyze candidate profile against specific job requirements
2. Calculate a precise match score
3. IF qualified: Generate role-specific technical interview questions that assess candidate capability to handle THIS EXACT JOB

CRITICAL: Interview questions must be:
- Directly grounded in the job description's specific requirements
- Technical depth matching the role's seniority level
- Based on technologies, methodologies, or challenges explicitly mentioned in the JOB DESCRIPTION
- Questions that reveal whether candidate can handle ACTUAL JOB TASKS
- NOT generic "senior engineer" questions that apply to any role

CANDIDATE PROFILE (ANONYMIZED - NO PERSONAL DATA):
{anonymized_json}

JOB DESCRIPTION (USE THIS TO GROUND ALL DECISIONS):
{job_description}

ANALYSIS INSTRUCTIONS:

STEP 1 - Calculate match_score (0-100):
- Skills match: Do they have required tech stack? Check exact tech names in JD.
- Experience match: Do they have domain experience (specific years/type)?
- Education match: Does resume meet stated education requirements?

STEP 2 - IF match_score > 70 (QUALIFIED):
   Set is_qualified = true

   GENERATE 5 INTERVIEW QUESTIONS with these rules:

   Rule A: EXTRACT KEY JOB REQUIREMENTS FROM JD
   - Identify specific technologies mentioned (e.g., "Python 3.11", "FastAPI", "PostgreSQL", "AWS Lambda")
   - Identify specific challenges mentioned (e.g., "high-concurrency systems", "real-time processing")
   - Identify specific methodologies (e.g., "microservices architecture", "TDD", "event-driven")
   - Identify specific domain knowledge needed (e.g., "fintech", "healthcare compliance", "e-commerce at scale")

   Rule B: CREATE CONTEXTUAL QUESTIONS ONLY
   Q1: Ask about HANDS-ON EXPERIENCE with a specific tech from the JD
        Example: If JD mentions "FastAPI + PostgreSQL", ask about that specific combo, not generic REST APIs
   Q2: Ask about SOLVING A SPECIFIC CHALLENGE mentioned in JD
        Example: If JD mentions "handling 1M+ concurrent users", ask how they'd architect that
   Q3: Ask about DOMAIN-SPECIFIC knowledge needed for THIS JOB
        Example: If JD is for "fintech backend", ask about transaction handling, compliance, or payment systems
   Q4: Ask about ARCHITECTURAL DECISIONS relevant to JD tech stack
        Example: If JD mentions "microservices", ask about service boundaries, communication patterns, etc.
   Q5: Ask about SCALING or OPTIMIZATION for THIS JOB's specific use case
        Example: If JD mentions "real-time analytics", ask about data pipeline optimization

   Rule C: GROUND EVERY QUESTION IN JD
   - Before each question, reference the exact requirement from the job description
   - Question must assess if candidate can handle that specific requirement
   - Avoid questions that would apply to ANY senior engineer role

   DO NOT GENERATE:
   ✗ "Tell me about a challenging project" (too generic)
   ✗ "What's your leadership style?" (not technical)
   ✗ "How do you stay updated with tech?" (applies to everyone)
   ✓ "You mention needing 'real-time data processing' - how would you design the pipeline for 100K events/sec?"
   ✓ "The role requires AWS Lambda expertise - describe your experience with cold starts and function orchestration"

   LEAVE rejection_reasons and improvement_suggestions as empty arrays

STEP 3 - IF match_score <= 70 (NOT QUALIFIED):
   Set is_qualified = false
   List 2-3 specific rejection_reasons (reference missing skills/experience from JD)
   List 3-4 improvement_suggestions (actionable steps to get closer to JD requirements)
   LEAVE interview_questions as empty array

Return ONLY valid JSON (no markdown, no explanations, no preamble):
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
    "interview_questions": [
        "Q1 - [GROUNDED IN: specific JD requirement]...",
        "Q2 - [GROUNDED IN: specific JD requirement]...",
        "Q3 - [GROUNDED IN: specific JD requirement]...",
        "Q4 - [GROUNDED IN: specific JD requirement]...",
        "Q5 - [GROUNDED IN: specific JD requirement]..."
    ] or [],
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

        # Remove markdown code blocks if present
        if "```json" in generated_text:
            generated_text = generated_text.split("```json")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].split("```")[0].strip()

        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = generated_text[json_start:json_end]
            analysis_data = json.loads(json_str)

            # Ensure required fields exist
            if "match_score" not in analysis_data:
                analysis_data["match_score"] = 0
            if "is_qualified" not in analysis_data:
                analysis_data["is_qualified"] = analysis_data.get("match_score", 0) > 70
            if "interview_questions" not in analysis_data:
                analysis_data["interview_questions"] = []
            if "rejection_reasons" not in analysis_data:
                analysis_data["rejection_reasons"] = []
            if "improvement_suggestions" not in analysis_data:
                analysis_data["improvement_suggestions"] = []
            if "analysis_summary" not in analysis_data:
                analysis_data["analysis_summary"] = "Analysis complete"

            return analysis_data
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
