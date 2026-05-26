#!/usr/bin/env python3
"""
Clean backend startup script
Ensures the correct main.py is running
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("RESUME SCREENING BACKEND - STARTUP")
print("=" * 70)

# Ensure we're in the correct directory
project_dir = Path(__file__).parent
os.chdir(project_dir)
print(f"\nWorking directory: {project_dir}")

# Load environment
print("\nLoading environment...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
if not api_key:
    print("ERROR: HUGGINGFACE_API_KEY not found in .env")
    sys.exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

# Import and verify app
print("\nLoading FastAPI application...")
try:
    from main import app
    print("✓ FastAPI app imported from main.py")
except Exception as e:
    print(f"ERROR: Failed to import main.py: {e}")
    sys.exit(1)

# List endpoints
print("\nRegistered API Endpoints:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(route.methods) if route.methods else 'GET'
        if route.path.startswith('/api/'):
            print(f"  {methods:20} {route.path}")

# Start server
print("\n" + "=" * 70)
print("Starting Uvicorn server on http://localhost:8000")
print("=" * 70 + "\n")

import uvicorn
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="info"
)
