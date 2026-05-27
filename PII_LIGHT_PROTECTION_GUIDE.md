# Light PII Protection Implementation Guide

## Overview

**Goal:** Minimize PII exposure through masking + consent while keeping system simple.

### What Gets Protected
```
User Resume (John Doe, john@example.com, 555-1234)
    ↓
Extracted: name="Candidate_001", email=null, phone=null
    ↓
Internal Processing: Only "Candidate_001" used
    ↓
LLM still gets full resume (external risk, but user knows)
    ↓
Output: "Candidate_001" instead of "John Doe"
    ↓
PDF/JSON: No name, email, phone exposed
```

### Risk Profile
- ✅ **Prevents accidental PII leaks** (logs, PDFs, API responses)
- ✅ **User informed** of external API usage
- ⚠️ **External LLM still sees resume** (HuggingFace terms apply)
- ⚠️ **No encryption** (if intercepted in transit, data exposed)

---

## Implementation Steps

### Step 1: Create PII Masking Module

Create file: `pii_masker.py`

```python
import hashlib
from typing import Dict, Any, Tuple
import uuid

class PIIMasker:
    """Anonymizes PII data while preserving internal referencing."""
    
    def __init__(self):
        self.masking_map = {}  # Maps original name → masked ID
    
    def generate_candidate_id(self, original_name: str) -> str:
        """
        Generate consistent masked ID for a candidate.
        Same name always maps to same ID within session.
        """
        if original_name in self.masking_map:
            return self.masking_map[original_name]
        
        # Use first 8 chars of hash for consistency
        hash_digest = hashlib.sha256(original_name.encode()).hexdigest()[:8]
        masked_id = f"Candidate_{hash_digest.upper()}"
        
        self.masking_map[original_name] = masked_id
        return masked_id
    
    def mask_extracted_data(self, extracted_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove/mask PII from extracted resume data.
        
        Returns copy with:
        - name → Candidate ID
        - email → None (removed)
        - phone → None (removed)
        - All other data preserved
        """
        masked = extracted_resume.copy()
        
        original_name = extracted_resume.get('name', 'Unknown')
        masked['name'] = self.generate_candidate_id(original_name)
        masked['email'] = None
        masked['phone'] = None
        masked['original_name_hash'] = hashlib.sha256(
            original_name.encode()
        ).hexdigest()  # For audit purposes only
        
        return masked
    
    def mask_analysis_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Keep analysis data as-is (no PII there)."""
        return analysis.copy()
    
    def mask_recruiter_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Keep summary as-is (no direct PII)."""
        return summary.copy()


# Global instance for session
_masker = PIIMasker()

def get_masker() -> PIIMasker:
    return _masker
```

---

### Step 2: Add Consent Tracking

Create file: `consent_manager.py`

```python
from datetime import datetime
from typing import Optional

class ConsentRecord:
    """Track user consent for data processing."""
    
    def __init__(self, user_ip: str, job_title: str):
        self.timestamp = datetime.now()
        self.user_ip = user_ip
        self.job_title = job_title
        self.agreed_to_external_processing = False
        self.agreed_to_pdf_generation = False
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_ip": self.user_ip,
            "job_title": self.job_title,
            "external_processing": self.agreed_to_external_processing,
            "pdf_generation": self.agreed_to_pdf_generation
        }


class ConsentManager:
    """Manages user consent tracking."""
    
    def __init__(self):
        self.consents = []
    
    def record_consent(self, user_ip: str, job_title: str, 
                      external_processing: bool, pdf_generation: bool) -> ConsentRecord:
        """Record user consent before screening."""
        consent = ConsentRecord(user_ip, job_title)
        consent.agreed_to_external_processing = external_processing
        consent.agreed_to_pdf_generation = pdf_generation
        
        self.consents.append(consent)
        print(f"✓ Consent recorded: {consent.to_dict()}")
        
        return consent
    
    def validate_consent(self, external_processing: bool, pdf_generation: bool) -> bool:
        """Validate that user consented to requested operations."""
        if not external_processing:
            raise ValueError("Must consent to external LLM processing")
        return True
```

---

### Step 3: Update Backend (main.py)

Add consent endpoint and update screening endpoints:

```python
# Add to imports at top
from pii_masker import get_masker
from consent_manager import ConsentManager

# Create global consent manager
consent_manager = ConsentManager()

# NEW ENDPOINT: Pre-screening consent
@app.post("/api/consent")
async def get_consent_requirements(request: Request) -> Dict[str, Any]:
    """
    Inform user about data processing before they submit.
    This is shown in a popup/modal on frontend.
    """
    user_ip = request.client.host
    
    return {
        "status": "ok",
        "user_ip": user_ip,
        "disclosures": {
            "external_processing": {
                "title": "External LLM Processing",
                "description": "Your resume will be sent to HuggingFace's Llama model to extract information and analyze job fit. HuggingFace's privacy policy applies.",
                "data_sent": ["Resume text", "Job description", "Job title"],
                "data_not_sent": ["Name", "Email", "Phone"],
                "link": "https://huggingface.co/privacy"
            },
            "pdf_generation": {
                "title": "PDF Report Generation",
                "description": "A PDF report will be generated and downloaded to your computer. Keep it secure.",
                "data_included": ["Match score", "Interview questions or rejection reasons"],
                "data_excluded": ["Your actual name", "Email", "Phone"]
            },
            "data_retention": {
                "title": "Data Retention",
                "description": "Resume data is deleted from our servers immediately after processing."
            }
        }
    }


# UPDATED ENDPOINT: Add consent validation
@app.post("/api/screen-resume")
async def screen_resume(
    request: Request,
    resumeFile: UploadFile = File(...),
    jobDescription: str = Form(...),
    jobTitle: str = Form(...),
    consentExternalProcessing: bool = Form(default=False),
    consentPdfGeneration: bool = Form(default=False),
) -> Dict[str, Any]:
    """
    Main endpoint with consent validation and PII masking.
    """
    user_ip = request.client.host
    
    # STEP 0: Validate consent
    if not consentExternalProcessing:
        raise HTTPException(
            status_code=400,
            detail="Must consent to external LLM processing to continue"
        )
    
    # Record consent
    consent_manager.record_consent(
        user_ip=user_ip,
        job_title=jobTitle,
        external_processing=consentExternalProcessing,
        pdf_generation=consentPdfGeneration
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

    # MASK PII AFTER EXTRACTION
    masker = get_masker()
    masked_extracted_data = masker.mask_extracted_data(extracted_data)
    
    print(f"[STEP 1] Extracted candidate: {masked_extracted_data.get('name', 'Unknown')}")
    print(f"[STEP 1] Skills found: {len(masked_extracted_data.get('skills', []))} items")

    print("\n=== STEP 2: Analyzing & Scoring (LLM 2: Llama) ===")
    # NOTE: Still passes original data to LLM (user consented)
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

    # Return masked data to frontend (NOT original)
    return {
        "status": "success",
        "candidate_name": masked_extracted_data.get("name", "Unknown"),
        "extracted_resume": masked_extracted_data,  # ← MASKED
        "analysis": analysis_data,
        "recruiter_summary": summary_data,
        "job_title": jobTitle,
        "process_stage": "completed",
    }
```

---

### Step 4: Update Frontend - Add Consent Modal

Update: `src/components/ResumeScreener.jsx`

```jsx
import { useState } from 'react'
import ResumeForm from './ResumeForm'
import LoadingState from './LoadingState'
import ResultsDisplay from './ResultsDisplay'
import ConsentModal from './ConsentModal'
import '../styles/ResumeScreener.css'

function ResumeScreener() {
  const [currentStep, setCurrentStep] = useState('consent') // consent, form, loading, results, error
  const [processingStep, setProcessingStep] = useState('')
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [userConsent, setUserConsent] = useState({
    externalProcessing: false,
    pdfGeneration: false
  })

  const handleConsentAgree = (consentData) => {
    setUserConsent(consentData)
    setCurrentStep('form')
  }

  const handleConsentDecline = () => {
    setError("You must consent to continue. System cannot function without external LLM processing.")
    setCurrentStep('error')
  }

  const handleSubmit = async (formData) => {
    setCurrentStep('loading')
    setProcessingStep('Step 1/3: Extracting resume information...')

    const submitFormData = new FormData()
    submitFormData.append('jobTitle', formData.jobTitle)
    submitFormData.append('resumeFile', formData.resumeFile)
    submitFormData.append('jobDescription', formData.jobDescription)
    submitFormData.append('consentExternalProcessing', userConsent.externalProcessing)
    submitFormData.append('consentPdfGeneration', userConsent.pdfGeneration)

    try {
      const response = await fetch('http://localhost:8005/api/screen-resume', {
        method: 'POST',
        body: submitFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to screen resume')
      }

      const data = await response.json()
      setResults(data)
      setCurrentStep('results')
    } catch (err) {
      let errorMsg = err.message || 'Unknown error'
      setError(errorMsg)
      setCurrentStep('error')
      console.error('Full error:', err)
    }
  }

  const handleReset = () => {
    setCurrentStep('form')
    setResults(null)
    setError('')
    setProcessingStep('')
  }

  return (
    <div className="resume-screener">
      <header className="screener-header">
        <h1>🚀 Resume Screening & Interview Generator</h1>
        <p className="subtitle">AI-Powered Resume Analysis with Multi-LLM Orchestration</p>
      </header>

      <main className="screener-main">
        {currentStep === 'consent' && (
          <ConsentModal 
            onAgree={handleConsentAgree} 
            onDecline={handleConsentDecline} 
          />
        )}
        {currentStep === 'form' && <ResumeForm onSubmit={handleSubmit} isLoading={false} />}
        {currentStep === 'loading' && (
          <div className="loading-container">
            <LoadingState step={processingStep} />
            <p className="status-text">{processingStep}</p>
          </div>
        )}
        {currentStep === 'results' && <ResultsDisplay results={results} onReset={handleReset} />}
        {currentStep === 'error' && (
          <div className="error-container">
            <h2>❌ Error</h2>
            <p>{error}</p>
            <button className="btn-reset" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

export default ResumeScreener
```

---

### Step 5: Create Consent Modal Component

Create: `src/components/ConsentModal.jsx`

```jsx
import { useState } from 'react'
import '../styles/ConsentModal.css'

function ConsentModal({ onAgree, onDecline }) {
  const [externalProcessing, setExternalProcessing] = useState(false)
  const [pdfGeneration, setPdfGeneration] = useState(false)

  const handleAgree = () => {
    if (!externalProcessing) {
      alert('You must consent to external LLM processing to continue')
      return
    }
    onAgree({
      externalProcessing,
      pdfGeneration
    })
  }

  return (
    <div className="consent-overlay">
      <div className="consent-modal">
        <h2>📋 Data Processing Disclosure</h2>
        
        <div className="disclosure-section">
          <h3>What Data We Process</h3>
          <p>Your resume will be analyzed using AI models to:</p>
          <ul>
            <li>Extract your skills and experience</li>
            <li>Compare against the job description</li>
            <li>Generate interview questions</li>
          </ul>
        </div>

        <div className="disclosure-section warning">
          <h3>⚠️ Important: External API Processing</h3>
          <p>
            Your resume will be sent to <strong>HuggingFace's Llama model</strong> for analysis.
            Your data is subject to <a href="https://huggingface.co/privacy" target="_blank">HuggingFace's privacy policy</a>.
          </p>
          <label className="consent-checkbox">
            <input
              type="checkbox"
              checked={externalProcessing}
              onChange={(e) => setExternalProcessing(e.target.checked)}
            />
            <span>
              I consent to sending my resume to HuggingFace's LLM for analysis
              <br />
              <small>(Required to use this service)</small>
            </span>
          </label>
        </div>

        <div className="disclosure-section">
          <h3>Optional: PDF Report</h3>
          <p>
            A PDF report can be generated with your results.
            The report will NOT include your actual name, email, or phone number.
          </p>
          <label className="consent-checkbox">
            <input
              type="checkbox"
              checked={pdfGeneration}
              onChange={(e) => setPdfGeneration(e.target.checked)}
            />
            <span>I want to generate a PDF report</span>
          </label>
        </div>

        <div className="disclosure-section">
          <h3>Data Retention</h3>
          <p>
            Your resume is deleted from our servers immediately after analysis.
            No data is stored long-term.
          </p>
        </div>

        <div className="consent-actions">
          <button 
            className="btn-decline" 
            onClick={onDecline}
          >
            Decline & Exit
          </button>
          <button 
            className="btn-agree" 
            onClick={handleAgree}
            disabled={!externalProcessing}
          >
            Agree & Continue
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConsentModal
```

---

### Step 6: Style the Consent Modal

Create: `src/styles/ConsentModal.css`

```css
.consent-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.consent-modal {
  background: white;
  border-radius: 12px;
  padding: 40px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.consent-modal h2 {
  color: var(--text-dark);
  margin-bottom: 25px;
  font-size: 1.5em;
}

.disclosure-section {
  margin-bottom: 25px;
  padding: 15px;
  border-left: 4px solid var(--primary-color);
  background: var(--light-bg);
  border-radius: 6px;
}

.disclosure-section.warning {
  border-left-color: var(--warning-color);
  background: #fef3c7;
}

.disclosure-section h3 {
  color: var(--text-dark);
  margin-bottom: 10px;
  font-size: 1.1em;
}

.disclosure-section p {
  color: var(--text-light);
  margin-bottom: 10px;
  line-height: 1.6;
}

.disclosure-section ul {
  margin-left: 20px;
  color: var(--text-light);
}

.disclosure-section li {
  margin-bottom: 8px;
}

.disclosure-section a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
}

.disclosure-section a:hover {
  text-decoration: underline;
}

.consent-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  margin-top: 15px;
}

.consent-checkbox input[type="checkbox"] {
  margin-top: 4px;
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
}

.consent-checkbox span {
  color: var(--text-dark);
  font-weight: 500;
  line-height: 1.5;
}

.consent-checkbox small {
  display: block;
  color: var(--text-light);
  font-size: 0.9em;
  margin-top: 4px;
}

.consent-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid var(--border-color);
}

.btn-decline,
.btn-agree {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-decline {
  background: var(--light-bg);
  color: var(--text-dark);
  border: 2px solid var(--border-color);
}

.btn-decline:hover {
  background: var(--border-color);
  transform: translateY(-2px);
}

.btn-agree {
  background: var(--primary-color);
  color: white;
}

.btn-agree:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.4);
}

.btn-agree:disabled {
  background: var(--text-light);
  cursor: not-allowed;
  opacity: 0.6;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .consent-modal {
    margin: 20px;
    max-width: 100%;
  }

  .consent-actions {
    flex-direction: column;
  }
}
```

---

### Step 7: Update PDF Generator to Remove PII

Modify: `pdf_generator.py` - Remove PII display

```python
# Around line 120-124, replace with:

story.append(Paragraph("CANDIDATE INFORMATION", heading_style))
story.append(Paragraph(f"<b>Candidate ID:</b> {extracted_resume.get('name', 'N/A')}", normal_style))
# ✓ Name is now "Candidate_XXXXX" due to masking
# ✓ Email and phone are removed (set to None)

# Skip phone if None
if extracted_resume.get('email'):
    story.append(Paragraph(f"<b>Email:</b> {extracted_resume.get('email', 'N/A')}", normal_style))

if extracted_resume.get('phone'):
    story.append(Paragraph(f"<b>Phone:</b> {extracted_resume.get('phone', 'N/A')}", normal_style))

story.append(Paragraph(f"<b>Education:</b> {extracted_resume.get('education', 'N/A')}", normal_style))
```

---

## Data Flow Comparison

### Before (No PII Protection)
```
User Resume (John Doe, john@example.com)
    ↓ [Full PII in memory]
    ↓ [Sent to HuggingFace]
    ↓ [Stored in API response]
    ↓ [Printed to console]
    ↓ [Included in PDF]
    ↓ [EXPOSED - High Risk]
```

### After (Light PII Protection)
```
User Resume (John Doe, john@example.com)
    ↓ [Full PII in memory]
    ↓ [Sent to HuggingFace] ← User consented
    ↓ [MASKED to "Candidate_XXXXX"]
    ↓ [API returns masked data]
    ↓ [Console logs "Candidate_XXXXX"]
    ↓ [PDF shows "Candidate_XXXXX"]
    ↓ [Safer - User Informed]
```

---

## How to Improve Further

### Phase 2: Medium Protection (Add Later)
```
1. Remove email/phone from LLM prompts
   - Send only: skills, experience years, education
   - Keep name for context, but hash it
   
2. Add data deletion after 24 hours
   - Auto-delete resume files from /tmp
   - Clear in-memory cache
   
3. Add request logging
   - Log: timestamp, job_title, consent status
   - Don't log: name, email, resume content
```

### Phase 3: Heavy Protection (Add Even Later)
```
1. Extract only job-relevant fields from resume
   - Parse resume for: skills, years, education
   - Don't send full text to LLM
   
2. Anonymize before LLM
   - Send to scoring: "Senior Engineer with Python, 6 years"
   - Don't send: full resume, name, contact info
   
3. Encrypt at rest
   - Encrypt resume files before storage
   - Decrypt only during processing
```

### Phase 4: Maximum Protection (Separate Effort)
```
1. Run Llama locally (no external APIs)
2. Full end-to-end encryption
3. GDPR compliance suite (right to delete, access, etc.)
```

---

## Testing the Implementation

### Test Case 1: Consent Flow
```
1. Open app
2. See consent modal
3. Don't check "External Processing"
4. Try to click "Agree" → Disabled (Good!)
5. Check "External Processing"
6. Click "Agree" → Proceeds
```

### Test Case 2: Data Masking
```
1. Upload John Doe's resume
2. Results show "Candidate_XXXXX"
3. Console logs "Candidate_XXXXX" (not "John Doe")
4. PDF shows "Candidate_XXXXX" (not name/email/phone)
```

### Test Case 3: PII Removal
```
1. Upload resume with phone: 555-1234
2. API response: phone is null (not in response)
3. PDF: no phone number shown
```

---

## Summary: Light PII vs Alternatives

| Feature | Light | Medium | Heavy | Max |
|---------|-------|--------|-------|-----|
| Consent flow | ✅ | ✅ | ✅ | ✅ |
| Masking | ✅ | ✅ | ✅ | ✅ |
| Redaction | ✅ | ✅ | ✅ | ✅ |
| Selective LLM data | ❌ | ✅ | ✅ | ✅ |
| Encryption | ❌ | ✅ | ✅ | ✅ |
| Auto-deletion | ❌ | ✅ | ✅ | ✅ |
| Local LLM | ❌ | ❌ | ❌ | ✅ |
| GDPR compliance | ❌ | ⚠️ | ✅ | ✅ |
| Effort | 30 min | 2-3h | 4-5h | 1-2 days |

---

## Files to Create/Modify

### Create New:
- `pii_masker.py` - PII masking logic
- `consent_manager.py` - Consent tracking
- `src/components/ConsentModal.jsx` - Consent UI
- `src/styles/ConsentModal.css` - Consent styles

### Modify:
- `main.py` - Add consent endpoint, validation, masking calls
- `pdf_generator.py` - Skip null PII fields
- `src/components/ResumeScreener.jsx` - Add consent flow

### No Changes Needed:
- `llm_matcher_scorer.py` - Still gets full data (consented)
- `llm_resume_extractor.py` - Still gets full data (consented)
- `llm_recruiter_summary.py` - No changes needed
