# Quick Start Guide

## 5-Minute Setup

### Step 1: Get HuggingFace API Key
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up / Login
3. Go to Settings → Access Tokens
4. Create a new token with read access
5. Copy the token

### Step 2: Configure Environment

```bash
# In the project root directory
cp .env.example .env

# Edit .env and paste your API key
# HUGGINGFACE_API_KEY=your_token_here
```

### Step 3: Install Dependencies

**Backend:**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 4: Start Both Services

**Terminal 1 - Backend:**
```bash
python main.py
```
✅ Server running on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✅ App running on `http://localhost:5173`

## Using the Application

1. **Open** `http://localhost:5173` in your browser
2. **Enter Job Title** (e.g., "Senior Python Developer")
3. **Upload Resume** (PDF or TXT file)
4. **Paste Job Description** in the text area
5. **Click "Analyze Resume"**

### Results You'll See:

✓ **Candidate Information** - Name, skills, experience, education
✓ **Match Score** - How well candidate matches JD (0-100%)
✓ **If Score > 70%** - Advanced interview questions (5 questions)
✓ **If Score ≤ 70%** - Why not qualified + improvement suggestions
✓ **Recruiter Summary** - Executive summary with recommendation
✓ **PDF Download Button** - Download professional summary as PDF (for all candidates)

## File Structure

```
Resume_Screening_Project/
├── main.py                    # FastAPI server
├── llm_resume_extractor.py   # LLM 1: Extract info
├── llm_matcher_scorer.py     # LLM 2: Score & analyze
├── llm_recruiter_summary.py  # LLM 3: Summarize
├── requirements.txt
├── .env                       # Your API key here
└── frontend/                 # React app
```

## 3 LLM Models Explained

| Model | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Llama** | Extract resume data | Resume text | Structured JSON (name, skills, etc.) |
| **Mistral** | Score & generate questions | Extracted data + JD | Match score, interview Qs or rejection reasons |
| **Zephyr** | Summarize for recruiter | All previous data | Recommendation, next steps, summary |

## Troubleshooting

### "API request failed"
→ Check HuggingFace API key in .env file

### "CORS error"
→ Backend is not running on port 8000

### "Module not found"
→ Make sure you installed `pip install -r requirements.txt`

### "Port already in use"
→ Kill the process or use a different port:
```bash
python main.py --port 8001
```

## Sample Resume for Testing

```
John Doe
john@example.com | (555) 123-4567

EXPERIENCE
Senior Software Engineer at TechCorp (2021-2023)
- Led Python backend development
- Built microservices with Docker & Kubernetes
- 5 years of software development experience

SKILLS
Python, JavaScript, React, FastAPI, AWS, Docker, PostgreSQL

EDUCATION
B.S. Computer Science, State University

CERTIFICATIONS
AWS Solutions Architect Associate
```

## Sample Job Description

```
Senior Python Developer

Requirements:
- 5+ years of software development experience
- Strong Python skills
- Experience with FastAPI or Django
- AWS knowledge
- Docker and container experience
- PostgreSQL experience

Responsibilities:
- Design and implement backend services
- Lead architecture decisions
- Mentor junior developers
- Participate in code reviews
```

## API Testing (Optional)

Using curl:
```bash
curl -X POST http://localhost:8000/api/health
```

Response:
```json
{"status": "healthy", "service": "Resume Screening API"}
```

## What's Next?

After you get it running:
1. ✅ Test with sample resume & JD above
2. ✅ Try with your own resume
3. ✅ Experiment with different job descriptions
4. ✅ Check logs to see LLM processing steps

---

**Questions?** Check README.md for detailed documentation
