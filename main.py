from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from llm_resume_extractor import extract_resume_info
from llm_matcher_scorer import analyze_resume_vs_jd
from llm_recruiter_summary import generate_recruiter_summary
from pdf_generator import generate_resume_summary_pdf

app = FastAPI(title="Resume Screening & Interview Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScreeningRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str




@app.post("/api/screen-resume")
async def screen_resume(
    resumeFile: UploadFile = File(...),
    jobDescription: str = Form(...),
    jobTitle: str = Form(...)
) -> Dict[str, Any]:
    """
    Main endpoint that orchestrates the entire screening process.
    1. Extracts resume information using Llama
    2. Analyzes and scores against JD using Llama
    3. Generates recruiter summary using Llama
    """

    try:
        resume_text = await resumeFile.read()
        resume_text = resume_text.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading resume file: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume file is empty")

    if not jobDescription.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    print("\n=== STEP 1: Extracting Resume Information (LLM 1: Llama) ===")
    extracted_data = extract_resume_info(resume_text)
    if "error" in extracted_data:
        raise HTTPException(status_code=500, detail=f"Resume extraction failed: {extracted_data['error']}")

    print(f"[STEP 1] Extracted candidate: {extracted_data.get('name', 'Unknown')}")
    print(f"[STEP 1] Skills found: {len(extracted_data.get('skills', []))} items")

    print("\n=== STEP 2: Analyzing & Scoring (LLM 2: Llama) ===")
    analysis_data = analyze_resume_vs_jd(extracted_data, jobDescription)
    if "error" in analysis_data:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {analysis_data['error']}")

    match_score = analysis_data.get("match_score", 0)
    is_qualified = analysis_data.get("is_qualified", match_score > 70)
    print(f"[STEP 2] Match Score: {match_score}%")
    print(f"[STEP 2] Qualified: {'YES' if is_qualified else 'NO'}")

    if is_qualified:
        print(f"[STEP 2] Generated {len(analysis_data.get('interview_questions', []))} interview questions")
    else:
        print(f"[STEP 2] Identified {len(analysis_data.get('rejection_reasons', []))} rejection reasons")
        print(f"[STEP 2] Generated {len(analysis_data.get('improvement_suggestions', []))} improvement suggestions")

    print("\n=== STEP 3: Generating Recruiter Summary (LLM 3: BART) ===")
    summary_data = generate_recruiter_summary(extracted_data, analysis_data, jobTitle)
    print(f"[STEP 3] Summary data structure: {type(summary_data)}")
    print(f"[STEP 3] Summary keys: {summary_data.keys() if isinstance(summary_data, dict) else 'Not a dict'}")
    if "error" in summary_data:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {summary_data['error']}")

    print(f"[STEP 3] Summary generated")
    print(f"[STEP 3] Executive Summary: {summary_data.get('executive_summary', 'N/A')}")
    print(f"[STEP 3] Recommendation: {summary_data.get('recommendation', 'N/A')}")

    result = {
        "status": "success",
        "candidate_name": extracted_data.get("name", "Unknown"),
        "extracted_resume": extracted_data,
        "analysis": analysis_data,
        "recruiter_summary": summary_data,
        "job_title": jobTitle,
        "process_stage": "completed"
    }

    return result


@app.post("/api/screen-resume-text")
async def screen_resume_text(request: ScreeningRequest) -> Dict[str, Any]:
    """
    Alternative endpoint that accepts resume text directly instead of file upload.
    Same orchestration as /api/screen-resume
    """

    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required")

    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    print("\n=== STEP 1: Extracting Resume Information (LLM 1: Llama) ===")
    extracted_data = extract_resume_info(request.resume_text)
    if "error" in extracted_data:
        raise HTTPException(status_code=500, detail=f"Resume extraction failed: {extracted_data['error']}")

    print(f"✓ Extracted candidate: {extracted_data.get('name', 'Unknown')}")

    print("\n=== STEP 2: Analyzing & Scoring (LLM 2: Llama) ===")
    analysis_data = analyze_resume_vs_jd(extracted_data, request.job_description)
    if "error" in analysis_data:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {analysis_data['error']}")

    print(f"[STEP 2] Match Score: {analysis_data.get('match_score', 0)}%")

    print("\n=== STEP 3: Generating Recruiter Summary (LLM 3: Llama) ===")
    summary_data = generate_recruiter_summary(extracted_data, analysis_data, request.job_title)
    if "error" in summary_data:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {summary_data['error']}")

    result = {
        "status": "success",
        "candidate_name": extracted_data.get("name", "Unknown"),
        "extracted_resume": extracted_data,
        "analysis": analysis_data,
        "recruiter_summary": summary_data,
        "job_title": request.job_title,
        "process_stage": "completed"
    }

    return result


@app.post("/api/download-pdf")
async def download_pdf(request: Dict[str, Any]) -> StreamingResponse:
    """
    Generate and download PDF summary of the screening results.
    Accepts the complete screening results and returns PDF file.
    """
    try:
        candidate_name = request.get("candidate_name", "Unknown")
        job_title = request.get("job_title", "Position")
        extracted_resume = request.get("extracted_resume", {})
        analysis = request.get("analysis", {})
        recruiter_summary = request.get("recruiter_summary", {})

        pdf_buffer = generate_resume_summary_pdf(
            candidate_name=candidate_name,
            job_title=job_title,
            extracted_resume=extracted_resume,
            analysis=analysis,
            recruiter_summary=recruiter_summary
        )

        filename = f"Resume_Screening_{candidate_name.replace(' ', '_')}.pdf"

        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Resume Screening API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
