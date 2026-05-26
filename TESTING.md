# Testing Guide - Resume Screening Project

This document describes how to run tests for the Resume Screening & Interview Generator project.

## 📋 Test Structure

### Test Files
- **test_backend.py** - Manual verification script (no external dependencies needed)
- **test_llm_functions.py** - Unit tests for LLM functions (requires pytest)
- **test_api_endpoints.py** - API endpoint tests using FastAPI TestClient (requires pytest)

## 🚀 Quick Start

### 1. Install Testing Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

Or install everything at once:
```bash
pip install -r requirements.txt
```

### 2. Run Manual Backend Test

No external API calls needed. Just checks imports, configuration, and routes.

```bash
python test_backend.py
```

**Output:**
```
[1/5] Testing imports... ✓
[2/5] Checking .env file... ✓
[3/5] Checking if backend is running on localhost:8005... ✓
[4/5] Checking available routes in app... ✓
[5/5] Testing LLM function connectivity... ✓
```

### 3. Run Automated Tests with Pytest

#### Run All Tests
```bash
pytest -v
```

#### Run Specific Test File
```bash
# Test LLM functions
pytest test_llm_functions.py -v

# Test API endpoints
pytest test_api_endpoints.py -v
```

#### Run Specific Test Class
```bash
pytest test_llm_functions.py::TestResumeExtractor -v
```

#### Run Specific Test
```bash
pytest test_llm_functions.py::TestResumeExtractor::test_extract_resume_returns_dict -v
```

#### Run with Coverage Report
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

## 📝 Test Categories

### Unit Tests (test_llm_functions.py)

Tests individual LLM functions without backend running.

**TestResumeExtractor (5 tests)**
- Resume extraction returns dict
- Extracted resume has required fields
- Handles empty input gracefully
- Skills are returned as list

**TestAnalysisScorer (7 tests)**
- Analysis returns dict
- Has required fields (match_score, is_qualified)
- Match score is within 0-100 range
- Qualified threshold logic (score > 70)
- Qualified candidates get interview questions
- Unqualified candidates get rejection reasons
- Score breakdown components

**TestRecruiterSummary (5 tests)**
- Summary returns dict
- Has required fields (executive_summary, recommendation, key_highlights)
- Executive summary is string
- Recommendation has valid values (RECOMMEND, DO NOT RECOMMEND, CONDITIONAL)

### Integration Tests (test_api_endpoints.py)

Tests API endpoints using FastAPI's TestClient.

**TestHealthEndpoint (3 tests)**
- Health check returns 200
- Returns valid JSON
- Has status field

**TestScreenResumeTextEndpoint (4 tests)**
- Endpoint exists
- Requires resume_text
- Requires job_description
- Returns JSON response

**TestScreenResumeEndpoint (4 tests)**
- Requires resumeFile
- Requires jobTitle
- Requires jobDescription
- Works with valid input

**TestDownloadPdfEndpoint (2 tests)**
- Endpoint exists
- Returns PDF content

**TestErrorHandling (2 tests)**
- Invalid endpoint returns 404
- Invalid method handling

## 🔧 Running Tests Step by Step

### Step 1: Prerequisites Check
```bash
# Ensure Python is installed
python --version

# Ensure dependencies are installed
pip list | grep pytest
```

### Step 2: Start Backend (Optional for API tests)
```bash
# Terminal 1
python main.py
```

### Step 3: Run Manual Test
```bash
# Terminal 2
python test_backend.py
```

### Step 4: Run Automated Tests
```bash
# Without backend running - only unit tests work
pytest test_llm_functions.py -v

# With backend running - all tests work
pytest -v
```

## 📊 Understanding Test Results

### Passing Test Example
```
test_llm_functions.py::TestResumeExtractor::test_extract_resume_returns_dict PASSED [20%]
```

### Failing Test Example
```
test_llm_functions.py::TestResumeExtractor::test_extract_resume_returns_dict FAILED [20%]
AssertionError: assert <class 'str'> == <class 'dict'>
```

### Skipped Test Example
```
test_api_endpoints.py::TestDownloadPdfEndpoint::test_download_pdf_returns_pdf SKIPPED [45%]
```

## 🐛 Debugging Tests

### Run with Verbose Output
```bash
pytest test_llm_functions.py -vv
```

### Show Print Statements
```bash
pytest test_llm_functions.py -v -s
```

### Stop on First Failure
```bash
pytest test_llm_functions.py -x
```

### Show Local Variables on Failure
```bash
pytest test_llm_functions.py -l
```

### Run with Python Debugger
```bash
pytest test_llm_functions.py --pdb
```

## 🎯 Test Execution Scenarios

### Scenario 1: Quick Sanity Check (No Backend Needed)
```bash
python test_backend.py
```
Expected time: < 5 seconds

### Scenario 2: Unit Tests Only
```bash
pytest test_llm_functions.py -v
```
Expected time: 2-5 minutes (depends on API response time)

### Scenario 3: Full Test Suite (Backend Running)
```bash
# Terminal 1: Start backend
python main.py

# Terminal 2: Run all tests
pytest -v
```
Expected time: 5-10 minutes

### Scenario 4: CI/CD Pipeline
```bash
# Install deps
pip install -r requirements.txt

# Run tests
pytest --tb=short -v

# Optional: Generate coverage
pytest --cov=. --cov-report=term-missing
```

## ✅ Checklist for Test Success

- [ ] Python 3.8+ installed
- [ ] All dependencies from requirements.txt installed
- [ ] .env file configured with HUGGINGFACE_API_KEY
- [ ] Backend running on port 8005 (for integration tests)
- [ ] pytest configuration recognized (pytest.ini exists)
- [ ] All test files in project root

## 📋 Expected Test Counts

```
Total Tests: ~29
├── test_backend.py: Manual checks (not counted as pytest)
├── test_llm_functions.py: 17 unit tests
│   ├── TestResumeExtractor: 4 tests
│   ├── TestAnalysisScorer: 7 tests
│   └── TestRecruiterSummary: 5 tests
└── test_api_endpoints.py: 15 integration tests
    ├── TestHealthEndpoint: 3 tests
    ├── TestScreenResumeTextEndpoint: 4 tests
    ├── TestScreenResumeEndpoint: 4 tests
    ├── TestDownloadPdfEndpoint: 2 tests
    ├── TestErrorHandling: 2 tests
    └── TestCORSHeaders: 1 test
```

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'pytest'"
**Solution:**
```bash
pip install pytest pytest-asyncio httpx
```

### Issue: "Connection refused" when running API tests
**Solution:** Start the backend first
```bash
python main.py
```

### Issue: "HUGGINGFACE_API_KEY not found in .env"
**Solution:** Create .env file
```bash
cp .env.example .env
# Edit .env with your actual API key
```

### Issue: Tests timeout or hang
**Solution:** Check internet connection (LLM API calls need network)

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)
- [Test-Driven Development Guide](https://en.wikipedia.org/wiki/Test-driven_development)

## 🤝 Contributing Tests

When adding new features:
1. Write tests first (TDD approach)
2. Implement feature
3. Ensure all tests pass
4. Add documentation

Example:
```python
def test_new_feature():
    """Test description"""
    # Arrange
    input_data = {...}
    
    # Act
    result = new_feature(input_data)
    
    # Assert
    assert result == expected_value
```
