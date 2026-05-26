# Security Audit Report
## Resume Screening & Interview Generator Project

**Date:** May 26, 2026  
**Status:** Security Review Complete  
**Risk Level:** Medium (with recommendations)

---

## Executive Summary

The Resume Screening & Interview Generator application has been reviewed for security vulnerabilities. **6 security issues** were identified:
- **3 Critical/High severity** issues that need immediate attention
- **2 Medium severity** issues requiring implementation  
- **1 Low severity** informational finding

---

## 1. CRITICAL: CORS Misconfiguration (main.py, lines 14-20)

### Issue
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ❌ ALLOWS ANY ORIGIN
    allow_credentials=True,       # ❌ ALLOWS CREDENTIALS FROM ANY SOURCE
    allow_methods=["*"],          # ❌ ALLOWS ALL HTTP METHODS
    allow_headers=["*"],          # ❌ ALLOWS ALL HEADERS
)
```

### Risk
- **Type:** Cross-Origin Resource Sharing (CORS) Misconfiguration
- **Severity:** CRITICAL
- **Impact:** 
  - Any website can make requests to this API
  - Attackers can make malicious requests on behalf of users
  - Enables Cross-Site Request Forgery (CSRF) attacks
  - Allows data exfiltration from authenticated sessions

### Example Attack
```javascript
// Attacker's malicious website can now:
fetch('http://localhost:8005/api/screen-resume', {
  method: 'POST',
  body: formData,
  credentials: 'include'  // Sends user's credentials
})
```

### Recommendation
```python
# SECURE FIX:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5177",      # Your frontend only
        "http://localhost:3000",      # Dev/testing only if needed
        "https://yourdomain.com",     # Your production domain
    ],
    allow_credentials=False,           # Only if truly needed
    allow_methods=["GET", "POST"],     # Only required methods
    allow_headers=["Content-Type"],    # Only required headers
    max_age=600,                       # Cache CORS preflight for 10 min
)
```

**Priority:** IMPLEMENT IMMEDIATELY

---

## 2. HIGH: Unrestricted File Upload (main.py, lines 31-51)

### Issue
```python
resumeFile: UploadFile = File(...)
resume_text = await resumeFile.read()
resume_text = resume_text.decode("utf-8")
```

### Risk
- **Type:** Unrestricted File Upload / Denial of Service
- **Severity:** HIGH
- **Impact:**
  - Users can upload files of any size → Out of Memory crash
  - No file type validation (could upload executable files)
  - No filename sanitization → Directory traversal possible
  - Can crash the server with large files

### Example Attack
```bash
# Attacker uploads 10GB file
curl -F "resumeFile=@huge_file.bin" \
     -F "jobTitle=test" \
     -F "jobDescription=test" \
     http://localhost:8005/api/screen-resume

# Result: Server runs out of memory and crashes
```

### Recommendation
```python
# SECURE FIX:
from fastapi import UploadFile, File, HTTPException

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx'}

@app.post("/api/screen-resume")
async def screen_resume(
    resumeFile: UploadFile = File(...),
    jobDescription: str = Form(...),
    jobTitle: str = Form(...)
) -> Dict[str, Any]:
    # Check file size
    contents = await resumeFile.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Check file extension
    file_ext = Path(resumeFile.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    # Sanitize filename
    import re
    safe_filename = re.sub(r'[^\w.-]', '', resumeFile.filename)
    
    try:
        resume_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    
    # ... rest of code
```

**Priority:** IMPLEMENT IMMEDIATELY

---

## 3. HIGH: Sensitive Data in Error Messages (main.py, lines 48, 59, 67, etc.)

### Issue
```python
except Exception as e:
    raise HTTPException(status_code=400, detail=f"Error reading resume file: {str(e)}")
    # ❌ Exposes full error details to attacker
```

### Risk
- **Type:** Information Disclosure / Sensitive Data Exposure
- **Severity:** HIGH
- **Impact:**
  - Attackers learn system internals from error messages
  - Stack traces can reveal file paths, library versions, architecture
  - Helps attackers craft targeted exploits
  - Privacy violation (error details reach logs/analytics)

### Example Leak
```
User sees: "Error reading resume file: UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0"

Attacker learns: 
  - System uses Python 3
  - Uses UTF-8 encoding
  - File structure expectations
  - Perfect for crafting malicious payloads
```

### Recommendation
```python
import logging

logger = logging.getLogger(__name__)

@app.post("/api/screen-resume")
async def screen_resume(...):
    try:
        resume_text = await resumeFile.read()
        resume_text = resume_text.decode("utf-8")
    except Exception as e:
        # Log full details INTERNALLY
        logger.error(f"File read error for user: {str(e)}", exc_info=True)
        
        # Return generic message to USER
        raise HTTPException(
            status_code=400, 
            detail="Failed to read resume file. Please ensure it's a valid text file."
        )
```

**Priority:** IMPLEMENT IMMEDIATELY

---

## 4. MEDIUM: Path Traversal in PDF Filename (main.py, line 170)

### Issue
```python
filename = f"Resume_Screening_{candidate_name.replace(' ', '_')}.pdf"
# ❌ candidate_name is not sanitized
# Attacker can set: candidate_name = "../../../etc/passwd"
```

### Risk
- **Type:** Path Traversal / Directory Traversal
- **Severity:** MEDIUM
- **Impact:**
  - PDF could be saved to unexpected locations
  - Could overwrite important files
  - Doesn't directly cause RCE but aids reconnaissance

### Example Attack
```
POST /api/download-pdf
{
  "candidate_name": "../../sensitive_data"
  // Result: File saved to unexpected directory
}
```

### Recommendation
```python
import re
from pathlib import Path

@app.post("/api/download-pdf")
async def download_pdf(request: Dict[str, Any]) -> StreamingResponse:
    candidate_name = request.get("candidate_name", "Unknown")
    
    # SANITIZE: Remove any path traversal characters
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '', candidate_name)
    if not safe_name:
        safe_name = "Candidate"
    
    filename = f"Resume_Screening_{safe_name}.pdf"
    
    # Ensure filename doesn't contain path separators
    filename = Path(filename).name  # Remove any directory parts
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Priority:** IMPLEMENT THIS WEEK

---

## 5. MEDIUM: Verbose Debug Output in Logs (main.py, lines 56-89)

### Issue
```python
print(f"[STEP 1] Extracted candidate: {extracted_data.get('name', 'Unknown')}")
print(f"[STEP 1] Skills found: {len(extracted_data.get('skills', []))} items")
# ❌ Prints to stdout/logs - reveals processing details
```

### Risk
- **Type:** Information Disclosure / Verbose Logging
- **Severity:** MEDIUM
- **Impact:**
  - Production logs contain sensitive candidate information
  - Server logs could be exposed via misconfigured logging
  - Helps attackers understand system workflow
  - Privacy violation for candidate data

### Recommendation
```python
import logging

logger = logging.getLogger(__name__)

@app.post("/api/screen-resume")
async def screen_resume(...):
    # Log MINIMAL info in production
    logger.info("Resume screening request received")
    
    extracted_data = extract_resume_info(resume_text)
    if "error" in extracted_data:
        logger.error(f"Extraction failed: {extracted_data['error']}")
        raise HTTPException(status_code=500, detail="Resume extraction failed")
    
    # ONLY log success/failure, NOT candidate details
    logger.info("Resume extraction successful")
    
    # For debugging only:
    logger.debug(f"Extracted fields: {list(extracted_data.keys())}")  # NOT values!
```

**Priority:** IMPLEMENT THIS WEEK

---

## 6. LOW: Missing Input Validation (main.py, lines 111-115)

### Issue
```python
if not request.resume_text.strip():
    raise HTTPException(status_code=400, detail="Resume text is required")

if not request.job_description.strip():
    raise HTTPException(status_code=400, detail="Job description is required")
# ✓ Basic validation exists, but could be better
```

### Risk
- **Type:** Insufficient Input Validation
- **Severity:** LOW (because basic validation exists)
- **Impact:**
  - Very long strings could cause performance issues
  - No length limits on text inputs
  - LLM API could timeout with huge inputs

### Recommendation
```python
class ScreeningRequest(BaseModel):
    resume_text: str = Field(
        ..., 
        min_length=10,      # At least 10 chars
        max_length=50000,   # Max 50K chars
        description="Resume text"
    )
    job_description: str = Field(
        ..., 
        min_length=10, 
        max_length=10000,   # Job description max 10K
        description="Job description"
    )
    job_title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,     # Job title max 200 chars
        description="Job position title"
    )
```

**Priority:** IMPLEMENT NEXT SPRINT

---

## 7. LOW: Missing Rate Limiting

### Issue
No rate limiting on API endpoints. A user can spam requests.

### Risk
- **Type:** Denial of Service (DoS)
- **Severity:** LOW (because requires API calls which cost)
- **Impact:** Attacker could spam expensive LLM API calls

### Recommendation
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/screen-resume")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def screen_resume(...):
    # ... code
```

**Priority:** IMPLEMENT NEXT SPRINT

---

## Summary of Required Fixes

### 🔴 CRITICAL (Fix immediately)
| # | Issue | File | Line | Fix Time |
|---|-------|------|------|----------|
| 1 | CORS Misconfiguration | main.py | 14-20 | 15 min |
| 2 | Unrestricted File Upload | main.py | 31-51 | 30 min |
| 3 | Sensitive Data in Errors | main.py | 48, 59, 67 | 20 min |

### 🟡 MEDIUM (Fix this week)
| # | Issue | File | Line | Fix Time |
|---|-------|------|------|----------|
| 4 | Path Traversal in Filename | main.py | 170 | 15 min |
| 5 | Verbose Debug Logging | main.py | 56-89 | 20 min |

### 🟢 LOW (Fix next sprint)
| # | Issue | File | Impact | Fix Time |
|---|-------|------|--------|----------|
| 6 | Missing Input Length Limits | main.py | DoS risk | 15 min |
| 7 | No Rate Limiting | main.py | DoS risk | 20 min |

---

## Implementation Checklist

- [ ] **CORS Configuration**
  - [ ] Set allow_origins to specific domains only
  - [ ] Set allow_credentials=False
  - [ ] Set allow_methods to ["GET", "POST"]
  - [ ] Set allow_headers to ["Content-Type"]
  - [ ] Test CORS policies

- [ ] **File Upload Validation**
  - [ ] Add MAX_FILE_SIZE constant (5MB)
  - [ ] Validate file extension (.txt, .pdf)
  - [ ] Check file size before processing
  - [ ] Sanitize filename
  - [ ] Test with invalid files

- [ ] **Error Messages**
  - [ ] Remove exception details from API responses
  - [ ] Add logging for internal debugging
  - [ ] Use generic user-facing messages
  - [ ] Test error scenarios

- [ ] **Filename Sanitization**
  - [ ] Use Path().name to remove traversal chars
  - [ ] Use regex to remove special chars
  - [ ] Test with malicious filenames

- [ ] **Logging**
  - [ ] Configure logging instead of print()
  - [ ] Remove candidate details from logs
  - [ ] Log only success/failure + errors
  - [ ] Test logging output

- [ ] **Input Validation**
  - [ ] Add min/max length to resume_text
  - [ ] Add min/max length to job_description
  - [ ] Add min/max length to job_title
  - [ ] Test boundary cases

- [ ] **Rate Limiting**
  - [ ] Install slowapi: `pip install slowapi`
  - [ ] Configure rate limits (10/min per IP)
  - [ ] Test rate limiting

---

## Security Best Practices Applied

✅ **Good:**
- Use of HTTPException for error handling
- Input validation with Pydantic (basic)
- Using libraries instead of custom auth
- Async/await for non-blocking I/O
- Environment variables for sensitive config

❌ **Issues Found:**
- Overly permissive CORS settings
- No file upload validation
- Verbose error messages
- Unsafe filename handling
- Debug logging in production
- No rate limiting

---

## Testing Security Fixes

### Test CORS Fix
```bash
# Should fail (different origin)
curl -H "Origin: http://evil.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:8005/api/screen-resume

# Should succeed (allowed origin)
curl -H "Origin: http://localhost:5177" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:8005/api/screen-resume
```

### Test File Upload Fix
```bash
# Should fail (file too large)
dd if=/dev/zero of=large.txt bs=1M count=10
curl -F "resumeFile=@large.txt" \
     -F "jobTitle=test" \
     -F "jobDescription=test" \
     http://localhost:8005/api/screen-resume

# Should fail (wrong extension)
echo "test" > test.exe
curl -F "resumeFile=@test.exe" \
     -F "jobTitle=test" \
     -F "jobDescription=test" \
     http://localhost:8005/api/screen-resume
```

### Test Error Message Fix
```bash
# Upload non-UTF8 file
curl -F "resumeFile=@binary_file.bin" \
     -F "jobTitle=test" \
     -F "jobDescription=test" \
     http://localhost:8005/api/screen-resume

# Should show generic error, not stack trace
```

---

## Frontend Security Notes

The frontend code (React components) appears secure:
- ✅ No eval() or innerHTML usage
- ✅ No hardcoded credentials
- ✅ Uses form data properly
- ✅ Error handling implemented

**Recommendation:** Add Content Security Policy (CSP) headers in production.

---

## Deployment Recommendations

1. **Before Production:**
   - Fix all CRITICAL issues
   - Fix all MEDIUM issues
   - Enable HTTPS (not HTTP)
   - Add rate limiting
   - Configure logging properly

2. **Environment Separation:**
   - Development: CORS open, verbose logging
   - Production: Strict CORS, minimal logging

3. **Monitoring:**
   - Monitor API error rates
   - Alert on unusual file upload sizes
   - Track CORS rejection attempts
   - Monitor rate limit violations

4. **Documentation:**
   - Document CORS policy
   - Document file upload limits
   - Document security measures

---

## Conclusion

The application is **NOT READY FOR PRODUCTION** without addressing the critical CORS and file upload issues. With the recommended fixes implemented, the security posture will improve significantly.

**Estimated total fix time: 1-2 hours**

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [CORS Security](https://owasp.org/www-community/attacks/csrf)
- [File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)

---

**Report Prepared:** May 26, 2026  
**Next Review:** After implementing fixes
