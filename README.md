# Resume Screening & Interview Generator

An AI-powered resume screening system using HuggingFace LLM models to extract information, score candidates, and generate interview questions or rejection feedback with professional recruiter summaries.

## 📋 System Architecture

The system orchestrates 3 different models in a unified pipeline:

### **Pipeline Flow:**
```
User Input (Resume + Job Description)
    ↓
[LLM 1: Llama] Extract resume data → Structured JSON
    ↓
[LLM 2: Llama] Score & Analyze → Score > 70%?
    ├─ YES → Generate interview questions
    └─ NO → Rejection reasons + improvements
    ↓
[Model 3: Facebook BART] Generate recruiter summary
    ↓
Final Output + PDF Generation
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- HuggingFace Inference API
- Pydantic (data validation)

**Frontend:**
- React (Vite)
- Modern CSS with animations

**Models Used:**
- **LLM 1 (Extraction):** `meta-llama/Llama-3.1-8B-Instruct` via HuggingFace Inference
- **LLM 2 (Scoring & Analysis):** `meta-llama/Llama-3.1-8B-Instruct` via HuggingFace Inference
- **Model 3 (Summary):** `facebook/bart-large-cnn` (Summarization API)

## 📁 Project Structure

```
Resume_Screening_Project/
├── main.py                          # FastAPI application
├── llm_resume_extractor.py          # LLM 1: Resume extraction
├── llm_matcher_scorer.py            # LLM 2: Scoring & analysis
├── llm_recruiter_summary.py         # LLM 3: Summary generation
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
│
└── frontend/                        # React application
    ├── src/
    │   ├── components/
    │   │   ├── ResumeScreener.jsx      # Main container
    │   │   ├── ResumeForm.jsx          # Form input
    │   │   ├── LoadingState.jsx        # Loading animation
    │   │   ├── ResultsDisplay.jsx      # Results container
    │   │   └── results/
    │   │       ├── CandidateInfo.jsx   # Extracted info
    │   │       ├── MatchScore.jsx      # Score & breakdown
    │   │       ├── InterviewQuestions.jsx  # Interview Qs
    │   │       ├── RejectionFeedback.jsx   # Rejection info
    │   │       └── RecruiterSummary.jsx    # Final summary
    │   │
    │   ├── styles/
    │   │   ├── ResumeScreener.css
    │   │   ├── ResumeForm.css
    │   │   ├── LoadingState.css
    │   │   ├── ResultsDisplay.css
    │   │   ├── CandidateInfo.css
    │   │   ├── MatchScore.css
    │   │   ├── InterviewQuestions.css
    │   │   ├── RejectionFeedback.css
    │   │   └── RecruiterSummary.css
    │   │
    │   ├── App.jsx
    │   └── App.css
    │
    └── package.json
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- HuggingFace API Key

### Installation

**1. Set up Python environment:**
```bash
cd Resume_Screening_Project
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

**2. Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your HuggingFace API key
```

**3. Set up React frontend:**
```bash
cd frontend
npm install
```

### Running the Application

**Terminal 1 - Start Backend (FastAPI):**
```bash
python main.py
# Server runs on http://localhost:8005
```

**Terminal 2 - Start Frontend (React):**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5177 (or next available port)
```

Visit the frontend localhost URL shown in terminal output (typically `http://localhost:5177`).

## 📊 Workflow

### **Step 1: Resume Extraction (LLM 1 - Llama)**
Extracts structured information:
- Full name, email, phone
- Skills (array)
- Years of experience
- Strengths
- Education & certifications

**Output Format:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "React", "AWS"],
  "experience_years": 5,
  "strengths": ["Problem Solving", "Leadership"],
  "education": "B.Tech Computer Science",
  "certifications": ["AWS Solutions Architect"]
}
```

### **Step 2: Scoring & Analysis (LLM 2 - Llama)**
- Compares extracted resume with job description
- Generates match score (0-100%)
- Identifies matching and missing skills
- Generates score breakdown (skills, experience, education match)
- **If score > 70%:** Generates 5 advanced technical interview questions
- **If score ≤ 70%:** Generates rejection reasons and improvement suggestions

**Output Format:**
```json
{
  "match_score": 85,
  "score_breakdown": {
    "skills_match": 90,
    "experience_match": 85,
    "education_match": 80
  },
  "is_qualified": true,
  "interview_questions": ["Q1...", "Q2..."],
  "matching_skills": ["Python", "React"],
  "missing_skills": [],
  "analysis_summary": "Strong match..."
}
```

### **Step 3: Recruiter Summary (BART Summarization)**
- Extracts key insights from candidate profile and analysis
- Uses Facebook BART model for concise summarization
- Key highlights (from candidate strengths)
- Recommendation status (RECOMMEND / DO NOT RECOMMEND)
- Interview complexity level (BEGINNER / INTERMEDIATE / ADVANCED)
- Next steps based on qualification status
- Salary range note based on experience

## 🔌 API Endpoints

### POST `/api/screen-resume`
Upload resume file and job description.

**Request:**
```
Content-Type: multipart/form-data
- jobTitle: string
- resumeFile: File (txt/pdf)
- jobDescription: string
```

**Response:**
```json
{
  "status": "success",
  "candidate_name": "John Doe",
  "extracted_resume": {...},
  "analysis": {...},
  "recruiter_summary": {...}
}
```

### POST `/api/screen-resume-text`
Alternative endpoint with text input.

**Request:**
```json
{
  "resume_text": "string",
  "job_description": "string",
  "job_title": "string"
}
```

### POST `/api/download-pdf`
Generate and download PDF summary of screening results.

**Request:**
```json
{
  "candidate_name": "John Doe",
  "job_title": "Position",
  "extracted_resume": {...},
  "analysis": {...},
  "recruiter_summary": {...}
}
```

**Response:**
- PDF file (attachment)
- Available for both qualified and rejected candidates
- Contains all analysis, interview questions/feedback, and recruiter recommendations

### GET `/api/health`
Health check endpoint.

## 🎯 Key Features

✅ **Dual-LLM Pipeline** - Llama 3.1 for extraction & analysis, BART for summarization
✅ **JSON-Structured Extraction** - Resume data extracted to standardized JSON format
✅ **Intelligent Matching** - Automatic resume-to-job comparison with percentage scoring
✅ **Dynamic Outputs** - Interview questions for qualified candidates, improvement suggestions for others
✅ **Professional UI** - Modern React interface with smooth animations and real-time feedback
✅ **Concurrent Processing** - Non-blocking async operations for fast response times
✅ **Robust Error Handling** - Graceful error management with informative user feedback
✅ **Modular Architecture** - Separate modules for extraction, analysis, and summarization
✅ **PDF Report Generation** - Professional PDF summaries with detailed candidate analysis
✅ **Comprehensive Logging** - Backend logging for debugging and monitoring

## 🔒 Environment Variables

Create a `.env` file in the project root:

```
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
LLM_MODEL_ID=meta-llama/Llama-3.1-8B-Instruct
```

**Configuration Details:**
- `HUGGINGFACE_API_KEY`: Your HuggingFace API key for accessing inference endpoints
- `LLM_MODEL_ID`: Llama 3.1 8B Instruct model for resume extraction and job matching analysis
- **Note:** BART (`facebook/bart-large-cnn`) is used for recruiter summary generation via HuggingFace Inference API

**Security:** Do NOT commit `.env` file with actual API keys. Use `.env.example` as template.

## 📝 Implementation Details

### Dual-LLM Architecture
- **LLM 1 - Llama 3.1 8B Instruct** (Extraction & Analysis): Used for resume extraction (Step 1) and resume-to-job matching (Step 2)
  - Configured via `LLM_MODEL_ID` environment variable
  - Returns JSON-structured data for both extraction and analysis
  - Handles qualification scoring with configurable thresholds
  
- **LLM 2 - Facebook BART** (Summarization): Used for recruiter summary generation (Step 3)
  - `facebook/bart-large-cnn` model
  - Generates concise executive summaries from candidate profiles
  - Provides key highlights and recommendations
  - Accessed via HuggingFace Inference API

### API Integration
- HuggingFace Inference API for chat completions (Llama)
- HuggingFace Inference API for summarization (BART)
- JSON extraction from LLM responses with error handling
- Temperature settings: 0.2 (extraction), 0.3 (analysis), default (summarization)

### Error Handling
- Graceful error handling with detailed messages
- JSON parsing fallback mechanism
- API request error catching and reporting
- Frontend displays user-friendly error messages

## 🚀 Future Enhancements

- Database integration for storing screening results
- Caching layer for repeated candidate analyses
- Batch processing capability for multiple resumes
- Export results to PDF/CSV formats
- User authentication and role-based access
- Analytics dashboard for hiring metrics
- Custom model fine-tuning for specific domains
- Email notifications for qualified candidates
