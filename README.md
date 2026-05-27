# Resume Screening & Interview Generator

An AI-powered recruiter tool that automates candidate screening by analyzing resumes against job descriptions, generating match scores, and creating role-specific interview questions using advanced language models.

## Project Overview

**Resume Screening & Interview Generator** is a full-stack web application designed for hiring managers and recruiters to efficiently evaluate candidates. The system:

- **Analyzes resumes** (TXT/PDF formats) against job descriptions using LLM-powered analysis
- **Generates match scores** (0-100%) with detailed skill gap analysis
- **Creates role-specific interview questions** grounded in actual job requirements
- **Protects candidate privacy** through data anonymization before LLM processing
- **Provides recruiter recommendations** with summary reports and downloadable insights

The system leverages three separate LLM models to extract candidate information, analyze job fit, and generate executive summaries, ensuring nuanced evaluation beyond simple keyword matching.

### Key Use Case
Recruiters upload a candidate resume and job description. The system returns:
- Match score and qualification status
- Key strengths and skill gaps
- 5 role-specific interview questions (if qualified)
- Rejection feedback and improvement suggestions (if not qualified)
- Executive summary and recruiter recommendation

---

## Setup Instructions

### Prerequisites
- **Python 3.9+** (backend)
- **Node.js 16+** (frontend)
- **HuggingFace account** (API token for LLM access)
- Git

### Backend Setup

1. **Clone and navigate to project directory:**
   ```bash
   cd AI_Activity_2
   ```

2. **Create Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic python-multipart pdfplumber reportlab huggingface-hub
   ```

4. **Set HuggingFace API token:**
   ```bash
   export HF_TOKEN="your_huggingface_api_token"  # On Windows: set HF_TOKEN=...
   ```

5. **Start FastAPI backend (port 8006):**
   ```bash
   python run_backend.py
   # or: uvicorn main:app --host 0.0.0.0 --port 8006 --reload
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start Vite development server (port 5173):**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:5173
   ```

### Verification
- Frontend loads at `http://localhost:5173`
- Backend API available at `http://localhost:8006`
- Upload a sample resume and job description to verify end-to-end functionality

---

## Features

### Resume File Handling
- **Multi-format support**: TXT and PDF file uploads
- **Robust encoding detection**: Automatic fallback through UTF-8 → UTF-16 → Latin-1 → CP1252 → ISO-8859-1
- **Safe PDF extraction**: Uses `pdfplumber` with error recovery for corrupted documents
- **Single-read pattern**: File read only once to prevent stream exhaustion

### Input Validation & Security
- **Length validation**: Resume (10-50K chars), Job description (10-10K chars), Job title (1-200 chars)
- **Prompt injection detection**: 29-pattern detection system blocks dangerous inputs before LLM processing
- **Proper error handling**: Returns specific HTTPException messages for each validation failure

### AI-Powered Analysis
- **Resume extraction**: Llama 3.1 8B extracts candidate name, skills, experience, education, certifications
- **Job matching**: Llama 3.1 8B analyzes resume against job description with contextual scoring
- **Interview generation**: Creates 5 role-specific questions grounded in actual job requirements
- **Executive summary**: BART-based summarization with graceful timeout handling

### Privacy & Compliance
- **Data anonymization**: Only anonymized profile (skills, years, education) sent to LLM, never PII
- **PII masking**: Candidate name, email, phone masked in frontend responses
- **Consent tracking**: Records user consent with detailed data_shared and data_protected lists
- **Privacy disclosure**: `/api/pii-disclosure` endpoint explains data handling

### Real-Time Processing UI
- **5-step visualization**: Upload → Extract → Analyze → Generate → Report
- **Live progress indicators**: Animated step states (pending, active, completed)
- **Professional design**: SaaS-style gradient backgrounds, smooth animations, responsive layout
- **Responsive mobile**: Grid adjusts for tablets and mobile devices

### Result Delivery
- **Downloadable PDF reports**: Summary reports with match scores and recommendations
- **Structured JSON responses**: Interview questions and analysis data in machine-readable format
- **Company-facing insights**: Recommendations and rejection feedback for recruiter action

---

## Architecture / Workflow

### System Architecture

```
┌─────────────────────────────────────────────────┐
│          React Frontend (Vite)                  │
│  ├─ Resume upload form                          │
│  ├─ Real-time processing UI (5 steps)           │
│  └─ Results display & PDF download              │
└────────────────────┬────────────────────────────┘
                     │ HTTP/FormData
                     ▼
┌─────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8006)            │
├─────────────────────────────────────────────────┤
│  File Handling → Validation → LLM Pipeline      │
│  → Response Formatting → PII Masking            │
└────────────────────┬────────────────────────────┘
                     │ JSON
                     ▼
┌─────────────────────────────────────────────────┐
│      HuggingFace API (Llama 3.1 8B + BART)     │
└─────────────────────────────────────────────────┘
```

### End-to-End Workflow

**Step 1: Form Input**
- User uploads resume (TXT/PDF)
- Enters job description and job title
- System shows 5-step processing UI

**Step 2: File Processing**
- Resume bytes read once and decoded
- Text extracted from PDF or TXT
- Input length and injection safety validated

**Step 3: LLM Extraction**
- Llama 3.1 8B extracts: name, skills, experience_years, education, certifications
- Result validated for JSON structure with fallback values

**Step 4: PII Anonymization**
- Candidate name → "[Candidate Information Masked]"
- Email → null | Phone → null
- Skills and experience retained for analysis

**Step 5: Job Matching Analysis**
- Llama 3.1 8B receives anonymized profile + job description
- Scores across three dimensions: skills match, experience match, education match
- Average score combined into 0-100 match percentage
- Generates 5 role-specific interview questions (if score > 70%)

**Step 6: Summary Generation**
- BART summarizes analysis results with timeout handling
- Falls back to template if BART unavailable
- Generates recruiter recommendation (RECOMMEND/CONSIDER/REJECT)

**Step 7: Response Masking**
- PII masked in JSON response to frontend
- Candidate name displayed as masked
- Email and phone excluded
- Skills, scores, and recommendations visible

**Step 8: Frontend Display**
- Results component shows match score, skills, interview questions
- Optional: Generate and download PDF report

### Data Flow Summary
```
Resume File → Decode → Validate → Extract (Llama) → Anonymize → 
Analyze (Llama) → Score → Summarize (BART) → Mask PII → Response JSON
```

---

## AI Capabilities Used

### 1. Resume Information Extraction (Llama 3.1 8B)
**Purpose**: Automatically extract structured candidate information from unstructured resume text

**Input**: Raw resume text (any format)

**Output**: 
```json
{
  "name": "John Developer",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "experience_years": 6,
  "education": "BS Computer Science",
  "certifications": ["AWS Certified Solutions Architect"]
}
```

**Technique**: Few-shot prompting with explicit JSON format specification and fallback values

### 2. Resume-Job Fit Analysis (Llama 3.1 8B)
**Purpose**: Contextually analyze candidate against job requirements with nuanced scoring

**Input**:
- Anonymized candidate profile (skills, years, education only)
- Job description and job title

**Output**: 
```json
{
  "match_score": 92,
  "is_qualified": true,
  "matching_skills": ["Python", "FastAPI"],
  "missing_skills": ["Kubernetes"],
  "interview_questions": ["How have you optimized..."],
  "reasoning": "Candidate exceeds experience requirement..."
}
```

**Technique**: 
- Rule-based prompt engineering (Rule A: extract requirements, Rule B: define scoring categories, Rule C: ground answers)
- Explicit examples of good vs. bad interview questions
- Negative prompting (specify what NOT to do)
- Contextual reasoning instead of keyword matching

### 3. Executive Summarization (BART)
**Purpose**: Generate concise recruiter-facing summary with recommendation

**Input**: Full analysis results from job matching

**Output**:
```
Candidate demonstrates strong Python and FastAPI expertise with 6 years 
of production experience. However, lacks distributed systems background 
mentioned in job description.

RECOMMENDATION: RECOMMEND
```

**Technique**: BART abstractive summarization with 10-second timeout and graceful fallback template

### Why These Models?
- **Llama 3.1 8B**: Balance of intelligence, speed, and cost for structured extraction and reasoning
- **BART**: Optimized for abstractive summarization of technical content
- **Three separate calls**: Allows task-specific prompting and error isolation

---

## Challenges Faced

### Challenge 1: File Encoding Issues
**Problem**: Resumes submitted in various encodings (UTF-8, UTF-16, Latin-1, Windows-1252) caused decoding failures

**Solution**: 
- Implemented encoding fallback chain: UTF-8 → UTF-16 → Latin-1 → CP1252 → ISO-8859-1
- Single-read pattern prevents stream exhaustion
- Specific error messages guide users to correct issues

**Learning**: Always assume user-uploaded files have unknown encoding; defensive fallback chains prevent crashes

### Challenge 2: Generic Interview Questions
**Problem**: LLM generated generic questions ("Tell me about yourself") instead of role-specific ones

**Solution**:
- Implemented Rule A/B/C framework forcing explicit requirement extraction
- Added negative prompting (what NOT to generate)
- Required [GROUNDED IN: JD requirement] labels for each question
- Doubled prompt size to accommodate rules and examples

**Learning**: LLM quality depends more on prompt engineering than model selection

### Challenge 3: PII Exposure in Output
**Problem**: Candidate name, email, phone visible in results despite privacy claims

**Solution**:
- Data minimization: Only anonymized profile sent to LLM (skills, years, education)
- Response masking: Hide name/email/phone in JSON sent to frontend
- Consent tracking: Record user consent with detailed disclosure

**Learning**: Single-layer security insufficient; defense-in-depth approach needed (anonymize before processing + mask in output)

### Challenge 4: BART Timeout Failures
**Problem**: HuggingFace BART API returns 504 Gateway Timeout, causing crashes

**Solution**:
- Added 10-second timeout with graceful fallback
- Fallback template provides structured summary if BART unavailable
- Error logged for monitoring, but request completes successfully

**Learning**: External API failures should trigger graceful degradation, not complete failure

### Challenge 5: JSON Parsing Fragility
**Problem**: LLM responses with markdown code blocks or missing fields caused JSON parsing to fail

**Solution**:
- Strip markdown blocks (```json ... ```) before parsing
- Provide fallback values for all required fields
- Better error logging to identify parsing issues
- Validate schema after parsing

**Learning**: Defensive parsing with fallback values more reliable than strict parsing

### Challenge 6: Progress Bar Exceeding 100%
**Problem**: During step transitions, progress bar showed 110% due to rounding

**Solution**: 
- Added `Math.min()` to cap percentage at 100% maximum
- Separate logic for calculating width and percentage display

**Learning**: Frontend calculations need bounds checking; percentage fields prone to off-by-one errors

### Challenge 7: Real-Time Feedback Without WebSockets
**Problem**: Showing real-time processing steps without server-sent events infrastructure

**Solution**:
- Frontend simulation with 5 steps over ~7.5 seconds
- Step durations match approximate backend processing time
- Perceived real-time feedback without complex infrastructure
- Actual results displayed once backend responds

**Learning**: Perceived real-time is often sufficient; avoid premature infrastructure complexity

---

## Future Improvements

### Phase 1: Security Hardening
- [ ] API rate limiting per IP/user
- [ ] OAuth2 authentication for recruiter accounts
- [ ] Encrypted storage for historical screening records
- [ ] Audit logs for compliance (who screened whom, when)
- [ ] HTTPS enforcement with certificate pinning

### Phase 2: Monitoring & Observability
- [ ] Structured logging with correlation IDs
- [ ] Performance metrics: API latency, LLM processing time, file size distribution
- [ ] Error tracking with Sentry or similar
- [ ] Dashboard for recruiter usage analytics
- [ ] Alerts for failing LLM requests or timeout spikes

### Phase 3: Compliance & Data Governance
- [ ] GDPR compliance: Right-to-be-forgotten API for candidate data
- [ ] Data retention policies: Auto-delete screening records after 90 days
- [ ] PII encryption for storage (currently transient)
- [ ] Privacy policy updates with explicit data flow diagrams
- [ ] Third-party data processing agreements with HuggingFace

### Phase 4: Scalability & Performance
- [ ] Caching layer for job descriptions (Redis)
- [ ] Async job queue (Celery) for LLM processing
- [ ] Database integration for persistent storage
- [ ] Batch processing API for uploading multiple resumes
- [ ] CDN for frontend assets and PDF downloads

### Phase 5: Product Features
- [ ] Candidate comparison: Side-by-side analysis of multiple candidates
- [ ] Custom scoring rubrics: Recruiters define weights for skills/experience/education
- [ ] Interview feedback forms: Record candidate answers and interviewer notes
- [ ] Integration with ATS systems (Workday, Lever, Greenhouse)
- [ ] Multi-language support for resumes and job descriptions
- [ ] Fine-tuned models: Train domain-specific models on company hiring data

### Technical Debt
- [ ] Add comprehensive test suite (unit, integration, E2E)
- [ ] Implement proper error handling with retry logic
- [ ] Database migration from transient state to persistent storage
- [ ] Deployment automation with Docker and Kubernetes
- [ ] Infrastructure-as-code (Terraform) for cloud deployment

---

## API Endpoints

### `/api/screen-resume` (POST)
Analyzes resume against job description

**Request**: `FormData` with:
- `resumeFile` (File): Resume in TXT or PDF format
- `jobDescription` (String): Job requirements
- `jobTitle` (String): Role title
- `userConsent` (Boolean): Consent to anonymization

**Response**:
```json
{
  "match_score": 92,
  "is_qualified": true,
  "candidate_name": "[Candidate Information Masked]",
  "email": null,
  "phone": null,
  "skills": ["Python", "FastAPI"],
  "matching_skills": ["Python", "FastAPI"],
  "missing_skills": ["Kubernetes"],
  "interview_questions": ["Q1...", "Q2..."],
  "recommendation": "RECOMMEND",
  "summary": "...",
  "reasoning": "..."
}
```

### `/api/pii-disclosure` (GET)
Returns privacy policy explaining data handling

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18 + Vite | UI framework and build tool |
| **Styling** | CSS3 | Modern SaaS design with gradients |
| **Backend** | FastAPI + Uvicorn | REST API and async request handling |
| **LLM Integration** | HuggingFace API | Llama 3.1 8B, BART models |
| **PDF Extraction** | pdfplumber | Extract text from PDF files |
| **Report Generation** | reportlab | Generate downloadable PDF reports |
| **Data Validation** | Pydantic | Schema validation and serialization |

---

## License

This project is provided as-is for educational and commercial use.

---

## Contact & Support

For technical details, refer to `SYSTEM_ARCHITECTURE.md` for comprehensive system documentation.
