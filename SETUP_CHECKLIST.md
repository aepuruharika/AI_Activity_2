# Setup Checklist

Complete these steps to run the Resume Screening application:

## ✅ Pre-requisites

- [ ] Python 3.8 or higher installed
- [ ] Node.js 16+ installed
- [ ] HuggingFace account created (huggingface.co)
- [ ] Text editor or IDE (VS Code recommended)

## ✅ Step 1: HuggingFace API Key

- [ ] Log in to [huggingface.co](https://huggingface.co)
- [ ] Navigate to Settings → [Access Tokens](https://huggingface.co/settings/tokens)
- [ ] Click "New token"
- [ ] Give it a name (e.g., "Resume Screener")
- [ ] Select "Read" permission
- [ ] Copy the token

## ✅ Step 2: Project Setup

- [ ] Clone or download the project
- [ ] Open terminal in project root directory
- [ ] Copy `.env.example` to `.env`
  ```bash
  cp .env.example .env
  ```
- [ ] Open `.env` file and paste your HuggingFace API key
  ```
  HUGGINGFACE_API_KEY=your_token_here
  ```

## ✅ Step 3: Backend Setup

- [ ] Create Python virtual environment
  ```bash
  python -m venv venv
  ```

- [ ] Activate virtual environment
  ```bash
  # Windows:
  venv\Scripts\activate
  
  # Linux/Mac:
  source venv/bin/activate
  ```

- [ ] Install Python dependencies
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verify installation
  ```bash
  python -c "import fastapi; print('FastAPI installed')"
  ```

## ✅ Step 4: Frontend Setup

- [ ] Open new terminal and navigate to frontend folder
  ```bash
  cd frontend
  ```

- [ ] Install Node.js dependencies
  ```bash
  npm install
  ```

- [ ] Verify installation
  ```bash
  npm list react
  ```

## ✅ Step 5: Start Services

- [ ] Terminal 1: Start backend
  ```bash
  # Make sure venv is activated first
  python main.py
  ```
  Expected: `INFO:     Application startup complete`

- [ ] Terminal 2: Start frontend
  ```bash
  cd frontend
  npm run dev
  ```
  Expected: `Local: http://localhost:5173/`

## ✅ Step 6: Verify Setup

- [ ] Open http://localhost:5173 in browser
- [ ] See "Resume Screening & Interview Generator" title
- [ ] Form appears with Job Title, Resume, and Job Description fields
- [ ] Backend terminal shows no errors
- [ ] Frontend terminal shows no errors

## ✅ Step 7: Test the Application

### Create a test resume (test_resume.txt):
```
John Doe
john@example.com
(555) 123-4567

EXPERIENCE
Senior Software Engineer at TechCorp (2021-2023)
- 5 years of Python development
- Built microservices with Docker and Kubernetes
- AWS cloud architecture

SKILLS
Python, JavaScript, React, FastAPI, AWS, Docker, PostgreSQL, Microservices

EDUCATION
B.S. Computer Science

CERTIFICATIONS
AWS Solutions Architect Associate
```

### Create a test job description (test_jd.txt):
```
Senior Python Developer

About the Role:
Looking for an experienced Python developer to join our backend team.

Requirements:
- 5+ years of software development
- Expert-level Python skills
- FastAPI or Django experience
- AWS knowledge required
- Docker and container experience
- PostgreSQL experience

Responsibilities:
- Design and implement backend services
- Lead architecture decisions
- Mentor junior developers
- Participate in code reviews
```

### Run the test:
- [ ] Enter "Senior Python Developer" as job title
- [ ] Upload test_resume.txt
- [ ] Paste test job description
- [ ] Click "Analyze Resume"
- [ ] Wait for processing (should see 3 steps)
- [ ] See results with:
  - [ ] Candidate information
  - [ ] Match score (should be ~85%)
  - [ ] Interview questions (since >70%)
  - [ ] Recruiter summary

## ✅ Troubleshooting

### Issue: "Connection refused" or "Cannot connect to API"
- [ ] Check if backend is running on terminal 1
- [ ] Check console output for errors
- [ ] Verify backend running on localhost:8000
- [ ] Try restarting backend

### Issue: "API key is invalid" or "Unauthorized"
- [ ] Verify API key in `.env` file is correct
- [ ] Check no extra spaces in `.env`
- [ ] Try generating a new token on huggingface.co
- [ ] Make sure you copied the full token

### Issue: "Module not found: 'fastapi'"
- [ ] Verify venv is activated (should show "(venv)" in prompt)
- [ ] Run `pip install -r requirements.txt` again
- [ ] Try `pip install fastapi uvicorn requests pydantic python-dotenv`

### Issue: "Cannot find module 'react'"
- [ ] Make sure you're in frontend directory
- [ ] Run `npm install` again
- [ ] Try `npm cache clean --force` then `npm install`

### Issue: Slow responses from LLM
- [ ] HuggingFace API can take 5-30 seconds first time
- [ ] Subsequent calls might be faster due to model loading
- [ ] Check internet connection
- [ ] Consider using smaller models if preferred

## ✅ Port Conflicts

If ports are already in use:

### Change backend port:
```bash
# Edit main.py and change:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed from 8000
```

### Change frontend port:
```bash
# Edit frontend/vite.config.js or use:
npm run dev -- --port 5174
```

## ✅ Next Steps After Verification

- [ ] Test with your own resume
- [ ] Try different job descriptions
- [ ] Experiment with different scores
- [ ] Check backend console for processing steps
- [ ] Review the generated questions/feedback

## ✅ Development Tips

- **Live Reload**: Both frontend and backend support hot reload
- **Console Logs**: Backend shows detailed processing steps
- **Browser Console**: Check frontend console (F12) for errors
- **API Testing**: Use curl to test endpoints:
  ```bash
  curl http://localhost:8000/api/health
  ```

## ✅ File Locations to Know

```
Resume_Screening_Project/
├── .env                           # Your API key goes here
├── main.py                        # Backend entry point
├── llm_*.py                       # LLM modules
├── requirements.txt               # Python dependencies
│
└── frontend/
    ├── package.json               # Node dependencies
    ├── src/
    │   ├── App.jsx               # Main React component
    │   └── components/           # React components
    └── vite.config.js            # Vite config (auto-generated)
```

## ✅ Documentation Files

- [ ] `README.md` - Complete documentation
- [ ] `QUICKSTART.md` - Fast setup guide
- [ ] `PROJECT_SUMMARY.md` - Architecture overview
- [ ] `SETUP_CHECKLIST.md` - This file

## ✅ Success Criteria

You'll know everything is working when:

✅ Backend starts without errors  
✅ Frontend loads in browser  
✅ Form appears with all input fields  
✅ Resume upload is accepted  
✅ Analysis completes and shows results  
✅ You see candidate info, match score, and summary  

---

## 📞 Support

**If you encounter issues:**

1. Check error messages in console (backend Terminal 1)
2. Check browser console (Frontend - Press F12)
3. Verify API key is correct
4. Review TROUBLESHOOTING section above
5. Check README.md for detailed documentation

**Common fixes:**
- Restart both services (backend & frontend)
- Clear browser cache (Ctrl+Shift+Del)
- Check Python and Node.js versions

---

**Ready to go!** Follow the checklist above and you'll be up and running in 15 minutes. 🚀
