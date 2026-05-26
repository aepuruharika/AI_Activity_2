#!/usr/bin/env python3
"""Debug script - Run this to check if backend will work"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("BACKEND DEBUG CHECKER")
print("=" * 70)

# Step 1: Check .env
print("\n[STEP 1] Checking .env file...")
env_file = Path(".env")
if not env_file.exists():
    print("ERROR: .env file not found!")
    print("Creating it from .env.example...")
    import shutil
    shutil.copy(".env.example", ".env")
    print("Created .env file")

with open(".env") as f:
    env_content = f.read()
    if "hf_" in env_content:
        print("OK: API key found in .env")
    else:
        print("WARNING: API key might be invalid")

# Step 2: Load environment
print("\n[STEP 2] Loading environment variables...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
llama_model = os.getenv("LLAMA_MODEL_ID")

print(f"  API Key loaded: {api_key[:20]}..." if api_key else "  ERROR: No API key!")
print(f"  Llama Model: {llama_model}")

# Step 3: Try importing FastAPI app
print("\n[STEP 3] Testing FastAPI app import...")
try:
    from main import app
    print("OK: FastAPI app imported successfully")

    # Check routes
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            if methods:
                print(f"  {', '.join(methods):15} {route.path}")
            else:
                print(f"  GET            {route.path}")
except Exception as e:
    print(f"ERROR: Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Try importing LLM modules
print("\n[STEP 4] Testing LLM module imports...")
try:
    from llm_resume_extractor import extract_resume_info
    print("OK: llm_resume_extractor imported")
except Exception as e:
    print(f"ERROR: llm_resume_extractor failed: {e}")
    sys.exit(1)

try:
    from llm_matcher_scorer import analyze_resume_vs_jd
    print("OK: llm_matcher_scorer imported")
except Exception as e:
    print(f"ERROR: llm_matcher_scorer failed: {e}")
    sys.exit(1)

try:
    from llm_recruiter_summary import generate_recruiter_summary
    print("OK: llm_recruiter_summary imported")
except Exception as e:
    print(f"ERROR: llm_recruiter_summary failed: {e}")
    sys.exit(1)

try:
    from pdf_generator import generate_resume_summary_pdf
    print("OK: pdf_generator imported")
except Exception as e:
    print(f"ERROR: pdf_generator failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL CHECKS PASSED!")
print("=" * 70)
print("\nBackend should work. Run: python main.py")
print("=" * 70)
