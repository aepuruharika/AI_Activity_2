#!/usr/bin/env python3
"""Test script to verify backend is working"""

import requests
import sys
from pathlib import Path

print("=" * 70)
print("Resume Screening Backend - Manual Test Suite")
print("=" * 70)

# Test 1: Check imports
print("\n[1/5] Testing imports...")
try:
    from main import app
    from llm_resume_extractor import extract_resume_info
    from llm_matcher_scorer import analyze_resume_vs_jd
    from llm_recruiter_summary import generate_recruiter_summary
    from pdf_generator import generate_resume_summary_pdf
    print("  [OK] All imports successful")
except ImportError as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)

# Test 2: Check .env file
print("\n[2/5] Checking .env file...")
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        content = f.read()
        if "HUGGINGFACE_API_KEY" in content:
            print("  [OK] .env file exists and has API key configured")
        else:
            print("  [WARNING] .env file missing HUGGINGFACE_API_KEY")
else:
    print("  [ERROR] .env file not found")
    print("    Please create .env from .env.example")
    sys.exit(1)

# Test 3: Check if backend is running
print("\n[3/5] Checking if backend is running on localhost:8005...")
try:
    response = requests.get("http://localhost:8005/api/health", timeout=2)
    if response.status_code == 200:
        print(f"  [OK] Backend is running")
        data = response.json()
        print(f"    Status: {data.get('status')}")
        print(f"    Service: {data.get('service')}")
    else:
        print(f"  [ERROR] Backend returned {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  [WARNING] Cannot connect to backend on port 8005")
    print("    Make sure to run: python main.py")
except Exception as e:
    print(f"  [ERROR] {type(e).__name__}: {e}")

# Test 4: List all app routes
print("\n[4/5] Checking available routes in app...")
try:
    from main import app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'GET'
            routes.append(f"  {methods:10} {route.path}")

    if routes:
        print("  Available API Routes:")
        for route in sorted(routes):
            print(route)
    else:
        print("  [WARNING] No routes found")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 5: Test LLM function connectivity
print("\n[5/5] Testing LLM function connectivity...")
sample_resume = """
John Doe
Email: john@example.com
Phone: 123-456-7890
Skills: Python, JavaScript, React
Experience: 5 years in software development
Education: B.Tech Computer Science
"""

try:
    print("  Testing extract_resume_info()...")
    result = extract_resume_info(sample_resume)
    if "error" in result:
        print(f"    [WARNING] Function returned error: {result['error']}")
    else:
        print(f"    [OK] Successfully extracted resume for: {result.get('name', 'Unknown')}")
except Exception as e:
    print(f"    [ERROR] {e}")

print("\n" + "=" * 70)
print("Manual tests complete!")
print("\nTo run automated tests:")
print("  pip install pytest pytest-asyncio httpx")
print("  pytest test_llm_functions.py -v         # Test LLM functions")
print("  pytest test_api_endpoints.py -v         # Test API endpoints")
print("  pytest -v                               # Run all tests")
print("=" * 70)
