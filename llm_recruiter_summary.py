import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
BART_MODEL_ID = "facebook/bart-large-cnn"

client = InferenceClient(
    provider="hf-inference",
    api_key=HUGGINGFACE_API_KEY,
)


def generate_recruiter_summary(
    extracted_resume: Dict[str, Any],
    analysis: Dict[str, Any],
    job_title: str
) -> Dict[str, Any]:
    """
    Generate a comprehensive summary for the recruiter using BART summarization.
    Summarizes the candidate profile and analysis into a concise recruiter summary.
    """

    candidate_name = extracted_resume.get('name', 'Unknown')
    match_score = analysis.get('match_score', 0)
    is_qualified = analysis.get('is_qualified', False)
    recommendation = "QUALIFIED" if is_qualified else "NOT QUALIFIED"

    text_to_summarize = f"""
Candidate: {candidate_name}
Position: {job_title}

Profile Summary:
Name: {extracted_resume.get('name', 'Unknown')}
Email: {extracted_resume.get('email', 'N/A')}
Phone: {extracted_resume.get('phone', 'N/A')}
Skills: {', '.join(extracted_resume.get('skills', []))}
Experience Years: {extracted_resume.get('experience_years', 'Not specified')}
Experience Summary: {extracted_resume.get('experience_summary', 'Not specified')}
Education: {extracted_resume.get('education', 'Not specified')}
Strengths: {', '.join(extracted_resume.get('strengths', []))}

Match Analysis:
Overall Match Score: {match_score}%
Qualification Status: {recommendation}
Analysis Summary: {analysis.get('analysis_summary', 'No summary available')}
Matching Skills: {', '.join(analysis.get('matching_skills', []))}
Missing Skills: {', '.join(analysis.get('missing_skills', []))}

Interview Status: {"Qualified for interview" if is_qualified else "Needs improvement"}
"""

    try:
        try:
            # Try to get BART summarization (may timeout)
            summary_result = client.summarization(
                text_to_summarize,
                model=BART_MODEL_ID,
                timeout=10  # 10 second timeout
            )

            summary_text = "No summary available"

            if isinstance(summary_result, list):
                if len(summary_result) > 0 and isinstance(summary_result[0], dict):
                    summary_text = summary_result[0].get('summary_text', 'No summary available')
            elif isinstance(summary_result, dict):
                if 'summary_text' in summary_result:
                    summary_text = summary_result['summary_text']
            elif isinstance(summary_result, str):
                summary_text = summary_result

        except Exception as bart_error:
            # BART failed or timed out - use fallback summary
            print(f"[FALLBACK] BART summarization unavailable: {str(bart_error)}")
            summary_text = f"Candidate match score: {match_score}%. Status: {recommendation}. {analysis.get('analysis_summary', 'Evaluation based on resume analysis.')}"

        return {
            "executive_summary": str(summary_text),
            "key_highlights": extracted_resume.get('strengths', []),
            "recommendation": "RECOMMEND" if is_qualified else "DO NOT RECOMMEND",
            "recommendation_reason": analysis.get('analysis_summary', 'Based on match analysis'),
            "next_steps": ["Schedule interview"] if is_qualified else ["Request improvements", "Suggest skill development"],
            "interview_complexity": analysis.get('interview_complexity', 'INTERMEDIATE'),
            "expected_salary_range_note": "Based on experience level and qualifications"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Summarization failed: {str(e)}"}
