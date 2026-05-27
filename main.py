import io
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from llm_matcher_scorer import analyze_resume_vs_jd
from llm_recruiter_summary import generate_recruiter_summary
from llm_resume_extractor import extract_resume_info
from pdf_generator import generate_resume_summary_pdf
from pii_consent import consent_handler


def _decode_resume_bytes(file_bytes: bytes) -> str:
    """
    Safely decode resume file bytes with encoding fallback.

    Reads bytes only once and attempts decoding with multiple encodings.
    Ensures no duplicate IO operations.

    Args:
        file_bytes: Raw bytes from uploaded file (single read)

    Returns:
        Decoded text string

    Raises:
        HTTPException: If file cannot be decoded with any supported encoding
    """
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Resume file is empty")

    encodings = ["utf-8", "utf-16", "latin-1", "cp1252", "iso-8859-1"]

    for encoding in encodings:
        try:
            decoded = file_bytes.decode(encoding)
            if decoded.strip():
                return decoded
        except (UnicodeDecodeError, LookupError):
            continue

    raise HTTPException(
        status_code=400,
        detail=f"Unable to decode resume file. Tried: {', '.join(encodings)}. "
        "Please ensure file is in a standard text encoding (UTF-8, Latin-1, etc.)",
    )


def _validate_input(
    resume_text: str, job_description: str, job_title: str
) -> None:
    """
    Validate all input lengths before LLM processing.

    Ensures inputs are within safe limits to prevent LLM API errors
    and unexpected behavior.

    Args:
        resume_text: Resume content
        job_description: Job description content
        job_title: Job title

    Raises:
        HTTPException: If any input violates length constraints
    """
    resume_len = len(resume_text.strip()) if resume_text else 0
    jd_len = len(job_description.strip()) if job_description else 0
    jt_len = len(job_title.strip()) if job_title else 0

    if resume_len < 10:
        raise HTTPException(
            status_code=400,
            detail="Resume text is too short (minimum 10 characters)",
        )
    if resume_len > 50000:
        raise HTTPException(
            status_code=400,
            detail=f"Resume text is too long ({resume_len} chars, maximum 50000)",
        )

    if jd_len < 10:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short (minimum 10 characters)",
        )
    if jd_len > 10000:
        raise HTTPException(
            status_code=400,
            detail=f"Job description is too long ({jd_len} chars, maximum 10000)",
        )

    if jt_len < 1:
        raise HTTPException(
            status_code=400,
            detail="Job title is required",
        )
    if jt_len > 200:
        raise HTTPException(
            status_code=400,
            detail=f"Job title is too long ({jt_len} chars, maximum 200)",
        )


def _mask_pii_in_extracted_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask PII fields in extracted resume data.
    Removes name, email, phone from response to user.
    """
    masked = extracted_data.copy()
    masked['name'] = "[Candidate Information Masked]"
    masked['email'] = None
    masked['phone'] = None
    return masked


def _detect_prompt_injection(
    resume_text: str, job_description: str, job_title: str
) -> None:
    """
    Lightweight prompt injection detection.

    Detects common prompt injection patterns and blocks malicious inputs
    before they reach the LLM APIs. Uses fast string matching (no regex).

    Args:
        resume_text: Resume content
        job_description: Job description content
        job_title: Job title

    Raises:
        HTTPException: If suspicious patterns are detected
    """
    dangerous_patterns = [
        "ignore previous",
        "ignore all",
        "forget",
        "system prompt",
        "reveal",
        "secret",
        "password",
        "api key",
        "token",
        "act as",
        "pretend",
        "bypass",
        "ignore restrictions",
        "override",
        "jailbreak",
        "prompt injection",
        "sql injection",
        "drop table",
        "delete from",
        "update set",
        "execute",
        "eval(",
        "exec(",
        "import os",
        "subprocess",
        "shell",
        "bash",
        "cmd /c",
        "powershell",
    ]

    combined_text = (
        f"{resume_text} {job_description} {job_title}".lower()
    )

    for pattern in dangerous_patterns:
        if pattern in combined_text:
            raise HTTPException(
                status_code=400,
                detail="Input contains suspicious patterns. Please ensure your resume and job description contain legitimate content only.",
            )


def _extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract resume text from uploaded file (.txt or .pdf).

    Supports both plain text and PDF files. Other formats are rejected.
    Handles corrupted PDFs and files with no extractable text gracefully.

    Args:
        file_bytes: Raw bytes from uploaded file (single read)
        filename: Original filename used to determine file type

    Returns:
        Extracted text string

    Raises:
        HTTPException: If file format unsupported or extraction fails
    """
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Resume file is empty")

    filename_lower = filename.lower().strip()

    if filename_lower.endswith(".txt"):
        return _decode_resume_bytes(file_bytes)

    elif filename_lower.endswith(".pdf"):
        try:
            import pdfplumber
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="PDF support not installed. Please install pdfplumber.",
            )

        try:
            pdf = pdfplumber.open(io.BytesIO(file_bytes))

            # Check if PDF has pages
            if not hasattr(pdf, 'pages') or not pdf.pages:
                pdf.close()
                raise HTTPException(
                    status_code=400,
                    detail="PDF file has no pages or is corrupted",
                )

            text = ""
            try:
                for idx, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_error:
                        print(f"[WARNING] Failed to extract page {idx}: {str(page_error)}")
                        continue
            finally:
                pdf.close()

            if not text or not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="PDF file contains no extractable text",
                )

            return text

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {str(e)}. Please upload a valid PDF or use a .txt file instead.",
            )

    else:
        ext = filename.split(".")[-1].lower() if "." in filename else "unknown"
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: .{ext}. Upload .txt or .pdf file.",
        )


app = FastAPI(
    title="Resume Screening & Interview Generator",
    version="1.0.0",
    description="AI-powered resume screening system using HuggingFace LLM models",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScreeningRequest(BaseModel):
    """Resume screening request with text input."""
    resume_text: str
    job_description: str
    job_title: str




@app.post("/api/screen-resume")
async def screen_resume(
    resumeFile: UploadFile = File(...),
    jobDescription: str = Form(...),
    jobTitle: str = Form(...),
    userConsent: bool = Form(default=False),
) -> Dict[str, Any]:
    """
    Main endpoint orchestrating the entire screening process.

    Steps:
    1. Validates user consent
    2. Extracts resume information using Llama
    3. Analyzes and scores against JD using Llama (anonymized data only)
    4. Generates recruiter summary using BART

    Args:
        resumeFile: Resume file upload (txt/pdf)
        jobDescription: Job description text
        jobTitle: Job title
        userConsent: User consent to send anonymized data to external LLM

    Returns:
        Screening results with extracted data, analysis, and recruiter summary
    """
    if not userConsent:
        raise HTTPException(
            status_code=400,
            detail="User consent required. Call /api/pii-disclosure for more info."
        )

    if not jobDescription.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    try:
        file_bytes = await resumeFile.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading resume file: {str(e)}",
        )

    resume_text = _extract_resume_text(file_bytes, resumeFile.filename)

    _validate_input(resume_text, jobDescription, jobTitle)

    _detect_prompt_injection(resume_text, jobDescription, jobTitle)

    print("\n=== STEP 1: Extracting Resume Information (LLM 1: Llama) ===")
    extracted_data = extract_resume_info(resume_text)
    if "error" in extracted_data:
        raise HTTPException(
            status_code=500,
            detail=f"Resume extraction failed: {extracted_data['error']}",
        )

    print(f"[STEP 1] Extracted candidate: {extracted_data.get('name', 'Unknown')}")
    print(f"[STEP 1] Skills found: {len(extracted_data.get('skills', []))} items")

    print("\n=== STEP 2: Analyzing & Scoring (LLM 2: Llama) ===")
    analysis_data = analyze_resume_vs_jd(extracted_data, jobDescription)
    if "error" in analysis_data:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {analysis_data['error']}",
        )

    match_score = analysis_data.get("match_score", 0)
    is_qualified = analysis_data.get("is_qualified", match_score > 70)
    print(f"[STEP 2] Match Score: {match_score}%")
    print(f"[STEP 2] Qualified: {'YES' if is_qualified else 'NO'}")

    if is_qualified:
        interview_questions = analysis_data.get("interview_questions", [])
        print(f"[STEP 2] Generated {len(interview_questions)} interview questions")
    else:
        rejection_reasons = analysis_data.get("rejection_reasons", [])
        improvement_suggestions = analysis_data.get("improvement_suggestions", [])
        print(f"[STEP 2] Identified {len(rejection_reasons)} rejection reasons")
        print(
            f"[STEP 2] Generated {len(improvement_suggestions)} improvement suggestions"
        )

    print("\n=== STEP 3: Generating Recruiter Summary (LLM 3: BART) ===")
    summary_data = generate_recruiter_summary(
        extracted_data, analysis_data, jobTitle
    )
    if "error" in summary_data:
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {summary_data['error']}",
        )

    print("[STEP 3] Summary generated successfully")
    print(f"[STEP 3] Recommendation: {summary_data.get('recommendation', 'N/A')}")

    # Mask PII before returning to frontend
    masked_extracted_data = _mask_pii_in_extracted_data(extracted_data)

    return {
        "status": "success",
        "candidate_name": "[Candidate Information Masked]",
        "extracted_resume": masked_extracted_data,
        "analysis": analysis_data,
        "recruiter_summary": summary_data,
        "job_title": jobTitle,
        "process_stage": "completed",
    }


@app.post("/api/screen-resume-text")
async def screen_resume_text(request: ScreeningRequest) -> Dict[str, Any]:
    """
    Alternative endpoint accepting resume text directly instead of file upload.

    Same orchestration as /api/screen-resume but with text input instead of file.

    Args:
        request: ScreeningRequest with resume_text, job_description, job_title

    Returns:
        Screening results with extracted data, analysis, and recruiter summary
    """
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required")

    if not request.job_description.strip():
        raise HTTPException(
            status_code=400, detail="Job description is required"
        )

    _validate_input(request.resume_text, request.job_description, request.job_title)

    _detect_prompt_injection(request.resume_text, request.job_description, request.job_title)

    print("\n=== STEP 1: Extracting Resume Information (LLM 1: Llama) ===")
    extracted_data = extract_resume_info(request.resume_text)
    if "error" in extracted_data:
        raise HTTPException(
            status_code=500,
            detail=f"Resume extraction failed: {extracted_data['error']}",
        )

    print(f"✓ Extracted candidate: {extracted_data.get('name', 'Unknown')}")

    print("\n=== STEP 2: Analyzing & Scoring (LLM 2: Llama) ===")
    analysis_data = analyze_resume_vs_jd(
        extracted_data, request.job_description
    )
    if "error" in analysis_data:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {analysis_data['error']}",
        )

    print(f"[STEP 2] Match Score: {analysis_data.get('match_score', 0)}%")

    print("\n=== STEP 3: Generating Recruiter Summary (LLM 3: BART) ===")
    summary_data = generate_recruiter_summary(
        extracted_data, analysis_data, request.job_title
    )
    if "error" in summary_data:
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {summary_data['error']}",
        )

    # Mask PII before returning to frontend
    masked_extracted_data = _mask_pii_in_extracted_data(extracted_data)

    return {
        "status": "success",
        "candidate_name": "[Candidate Information Masked]",
        "extracted_resume": masked_extracted_data,
        "analysis": analysis_data,
        "recruiter_summary": summary_data,
        "job_title": request.job_title,
        "process_stage": "completed",
    }


@app.post("/api/download-pdf")
async def download_pdf(request: Dict[str, Any]) -> StreamingResponse:
    """
    Generate and download PDF summary of screening results.

    Args:
        request: Complete screening results dict with candidate_name, job_title,
                 extracted_resume, analysis, recruiter_summary

    Returns:
        PDF file as StreamingResponse with attachment disposition
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
            recruiter_summary=recruiter_summary,
        )

        filename = f"Resume_Screening_{candidate_name.replace(' ', '_')}.pdf"

        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"PDF generation failed: {str(e)}"
        )


@app.get("/api/pii-disclosure")
async def get_pii_disclosure() -> Dict[str, Any]:
    """
    Get PII handling disclosure before screening.
    Show recruiter what data will/won't be sent to external LLM.
    """
    return {
        "status": "ok",
        "disclosure": {
            "title": "🔒 Screening Privacy Notice",
            "description": "Candidate screening uses AI. Here's how we handle data:",
            "data_sent_to_llm": {
                "title": "✅ Data Shared with AI",
                "items": [
                    "Technical skills (Python, AWS, etc.)",
                    "Years of experience (number only)",
                    "Education level (degree type)",
                    "Professional summary",
                    "Certifications"
                ],
                "privacy_link": "https://huggingface.co/privacy"
            },
            "data_not_sent": {
                "title": "❌ Data NOT Shared",
                "items": [
                    "Candidate name",
                    "Candidate email",
                    "Candidate phone number",
                    "Full resume text",
                    "Personal identifying details"
                ]
            },
            "data_retention": "Candidate data is deleted immediately after screening (not stored)",
            "why_needed": "AI needs technical skills to match against job requirements"
        }
    }


@app.post("/api/consent/record")
async def record_consent(user_consent: bool = Form(...)) -> Dict[str, Any]:
    """Record that user consented to PII processing."""
    return consent_handler.record_consent(user_consent)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "Resume Screening API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
