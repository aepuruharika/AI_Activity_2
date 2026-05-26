# 📑 Project Index & Quick Reference

## 🎯 Where to Start

**New to the project?** Read these in order:
1. **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Project overview & features
2. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
3. **[README.md](README.md)** - Complete documentation

---

## 📚 Documentation Files

| File | Purpose | Read When |
|------|---------|-----------|
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | Complete project overview with PDF feature | First time / Overall understanding |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide | Ready to run the project |
| [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) | Step-by-step verification checklist | Want to verify everything works |
| [README.md](README.md) | Full technical documentation | Need detailed API/feature info |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Architecture & design decisions | Want to understand the system design |
| [CHANGES.md](CHANGES.md) | What's new / Recent updates | Want to see what changed |

---

## 🔧 Backend Files

### Core LLM Modules
| File | Purpose | Lines |
|------|---------|-------|
| [main.py](main.py) | FastAPI orchestrator + endpoints | 180+ |
| [llm_resume_extractor.py](llm_resume_extractor.py) | LLM 1: Llama extraction | 70+ |
| [llm_matcher_scorer.py](llm_matcher_scorer.py) | LLM 2: Mistral scoring | 80+ |
| [llm_recruiter_summary.py](llm_recruiter_summary.py) | LLM 3: Zephyr summary | 75+ |
| **[pdf_generator.py](pdf_generator.py)** | **PDF report generation** | **200+** |

### Configuration
| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python dependencies |
| [.env.example](.env.example) | Environment variables template |

---

## 🎨 Frontend Files

### React Components
```
frontend/src/components/
├── App.jsx                      (Root component)
├── ResumeScreener.jsx           (Main state container)
├── ResumeForm.jsx               (User input form)
├── LoadingState.jsx             (Processing animation)
├── ResultsDisplay.jsx           (Results & PDF button)
└── results/
    ├── CandidateInfo.jsx        (Extracted data display)
    ├── MatchScore.jsx           (Score visualization)
    ├── InterviewQuestions.jsx   (Interview Qs)
    ├── RejectionFeedback.jsx    (Rejection reasons)
    └── RecruiterSummary.jsx     (Summary display)
```

### Stylesheets
```
frontend/src/styles/
├── ResumeScreener.css           (Main layout)
├── ResumeForm.css               (Form styling)
├── LoadingState.css             (Spinner animation)
├── ResultsDisplay.css           (Results + PDF button)
├── CandidateInfo.css
├── MatchScore.css
├── InterviewQuestions.css
├── RejectionFeedback.css
└── RecruiterSummary.css
```

---

## 🔌 API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/screen-resume` | POST | Upload & screen resume | JSON with all analysis |
| `/api/screen-resume-text` | POST | Text input alternative | JSON with all analysis |
| `/api/download-pdf` | POST | Download PDF report | PDF file (attachment) |
| `/api/health` | GET | Health check | Status |

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────┐
│         React Frontend                   │
│  (localhost:5173)                        │
│  - ResumeForm → LoadingState → Results   │
│  - PDF Download Button                   │
└──────────────┬───────────────────────────┘
               │
         HTTP POST/GET
               │
┌──────────────▼───────────────────────────┐
│       FastAPI Backend                    │
│  (localhost:8000)                        │
│                                          │
│  /api/screen-resume (main endpoint)      │
│  ├── Step 1: llm_resume_extractor        │
│  ├── Step 2: llm_matcher_scorer          │
│  ├── Step 3: llm_recruiter_summary       │
│                                          │
│  /api/download-pdf (PDF endpoint)        │
│  └── pdf_generator.py                    │
└──────────────┬───────────────────────────┘
               │
         HuggingFace API
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
 Llama      Mistral     Zephyr
```

---

## 🚀 Getting Started (3 Steps)

### Step 1: Setup
```bash
# Get HuggingFace API key from:
# https://huggingface.co/settings/tokens

# Configure environment
cp .env.example .env
# Edit .env with your API key
```

### Step 2: Install
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Step 3: Run
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Open browser
# http://localhost:5173
```

---

## 📊 What Each LLM Does

### LLM 1: Llama (Extraction)
**Input:** Resume text  
**Output:** Structured JSON
```json
{
  "name": "John Doe",
  "skills": ["Python", "React", "AWS"],
  "experience_years": 5,
  "strengths": [...],
  "education": "B.Tech"
}
```

### LLM 2: Mistral (Scoring)
**Input:** Extracted resume + Job description  
**Output:** Score + Questions/Reasons
```json
{
  "match_score": 85,
  "is_qualified": true,
  "interview_questions": [...] or
  "rejection_reasons": [...]
}
```

### LLM 3: Zephyr (Summary)
**Input:** All previous data + Job title  
**Output:** Recruiter summary
```json
{
  "executive_summary": "...",
  "recommendation": "RECOMMEND",
  "next_steps": [...]
}
```

---

## 📥 PDF Download Feature

### How It Works
1. User completes screening
2. Clicks "📥 Download Summary as PDF"
3. Frontend sends all results to backend
4. Backend generates PDF (ReportLab)
5. PDF downloads automatically

### What's in the PDF
- ✅ Candidate information
- ✅ Match score & breakdown
- ✅ Interview questions (if qualified)
- ✅ Rejection reasons (if not qualified)
- ✅ Recruiter recommendations
- ✅ Next steps

### Available For
- ✅ Qualified candidates (score > 70%)
- ✅ Rejected candidates (score ≤ 70%)

---

## 🛠️ Common Tasks

### Add a New Component
```bash
# 1. Create component file
frontend/src/components/MyComponent.jsx

# 2. Create CSS file
frontend/src/styles/MyComponent.css

# 3. Import in parent component
import MyComponent from './components/MyComponent'
```

### Update an LLM Prompt
```bash
# Edit the prompt string in the relevant file:
# - llm_resume_extractor.py (LLM 1)
# - llm_matcher_scorer.py (LLM 2)
# - llm_recruiter_summary.py (LLM 3)

# Look for the `prompt = f"""..."""` string
```

### Change API Endpoint Port
```bash
# In main.py, change:
uvicorn.run(app, host="0.0.0.0", port=8000)
# to:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Change Frontend Port
```bash
# Run with custom port:
npm run dev -- --port 5174
```

---

## 🐛 Debugging Tips

### Check Backend Logs
```bash
# Terminal running main.py shows:
# ✓ Extracted candidate: ...
# ✓ Match Score: ...
# ✓ Summary generated: ...
```

### Check Frontend Logs
```bash
# Press F12 in browser → Console tab
# Shows API errors and fetch details
```

### Test API Directly
```bash
# Check health
curl http://localhost:8000/api/health

# Should return:
# {"status": "healthy", "service": "Resume Screening API"}
```

---

## 📋 File Changes Summary

### New Files
- ✅ `pdf_generator.py` - PDF generation
- ✅ `CHANGES.md` - Update documentation
- ✅ `FINAL_SUMMARY.md` - Project overview
- ✅ `INDEX.md` - This file

### Modified Files
- ✅ `main.py` - Added PDF endpoint
- ✅ `requirements.txt` - Added reportlab
- ✅ `ResultsDisplay.jsx` - Added PDF button
- ✅ `ResultsDisplay.css` - PDF button styles

### Removed Files
- ❌ `/static/` folder
- ❌ `/frontend/src/assets/`
- ❌ `/frontend/public/`

---

## 📞 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| API key invalid | Check `.env` file |
| Can't connect to backend | Verify `python main.py` is running |
| Module not found | Run `pip install -r requirements.txt` |
| Port in use | Change port in code |
| PDF download fails | Check browser console (F12) |
| Slow API responses | HuggingFace can take 5-30 seconds |

See **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** for detailed troubleshooting.

---

## ✅ Project Status

| Component | Status |
|-----------|--------|
| Backend API | ✅ Complete |
| LLM Integration | ✅ Complete |
| React Frontend | ✅ Complete |
| PDF Generation | ✅ Complete |
| Error Handling | ✅ Complete |
| Documentation | ✅ Complete |
| Testing Ready | ✅ Ready |
| Production Ready | ✅ Ready |

---

## 📚 Reference Links

- **HuggingFace**: https://huggingface.co
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev
- **ReportLab**: https://www.reportlab.com
- **Vite**: https://vitejs.dev

---

## 🎓 Learning Path

1. **Understand the system**: Read `FINAL_SUMMARY.md`
2. **See it in action**: Follow `QUICKSTART.md`
3. **Deep dive**: Read `README.md`
4. **Understand design**: Read `PROJECT_SUMMARY.md`
5. **Explore code**: Start with `main.py`

---

**Version:** 1.1 (Updated with PDF feature)  
**Last Updated:** May 2026  
**Status:** ✅ Ready to Deploy

---

**Start with [QUICKSTART.md](QUICKSTART.md) or [FINAL_SUMMARY.md](FINAL_SUMMARY.md)!**
