"""
Test cases for API endpoints.
Tests the FastAPI endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app as fastapi_app

# Create test client
client = TestClient(fastapi_app)


class TestHealthEndpoint:
    """Test suite for health check endpoint"""

    def test_health_check_returns_200(self):
        """Test that health endpoint returns 200"""
        response = client.get("/api/health")
        assert response.status_code == 200, "Health endpoint should return 200"

    def test_health_check_returns_json(self):
        """Test that health endpoint returns valid JSON"""
        response = client.get("/api/health")
        data = response.json()
        assert isinstance(data, dict), "Health response should be JSON"

    def test_health_check_has_status(self):
        """Test that health response has status field"""
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data, "Health response should have 'status' field"
        assert data["status"] == "healthy", "Status should be 'healthy'"


class TestScreenResumeTextEndpoint:
    """Test suite for screen-resume-text endpoint"""

    def test_screen_resume_text_endpoint_exists(self):
        """Test that endpoint exists"""
        response = client.post("/api/screen-resume-text", json={
            "resume_text": "Sample resume",
            "job_description": "Sample job",
            "job_title": "Sample role"
        })
        assert response.status_code != 404, "Endpoint should exist"

    def test_screen_resume_text_requires_resume(self):
        """Test that resume_text is required"""
        response = client.post("/api/screen-resume-text", json={
            "resume_text": "",
            "job_description": "Sample job",
            "job_title": "Sample role"
        })
        assert response.status_code == 400, "Should reject empty resume"

    def test_screen_resume_text_requires_job_description(self):
        """Test that job_description is required"""
        response = client.post("/api/screen-resume-text", json={
            "resume_text": "Sample resume",
            "job_description": "",
            "job_title": "Sample role"
        })
        assert response.status_code == 400, "Should reject empty job description"


class TestScreenResumeEndpoint:
    """Test suite for screen-resume endpoint (file upload)"""

    def test_screen_resume_requires_file(self):
        """Test that resumeFile is required"""
        response = client.post(
            "/api/screen-resume",
            data={
                "jobTitle": "Developer",
                "jobDescription": "Python developer needed"
            }
        )
        assert response.status_code == 422, "Should require resumeFile"

    def test_screen_resume_requires_job_title(self):
        """Test that jobTitle is required"""
        response = client.post(
            "/api/screen-resume",
            files={"resumeFile": ("test.txt", b"Sample resume")},
            data={"jobDescription": "Sample job"}
        )
        assert response.status_code == 422, "Should require jobTitle"

    def test_screen_resume_requires_job_description(self):
        """Test that jobDescription is required"""
        response = client.post(
            "/api/screen-resume",
            files={"resumeFile": ("test.txt", b"Sample resume")},
            data={"jobTitle": "Developer"}
        )
        assert response.status_code == 422, "Should require jobDescription"


class TestDownloadPdfEndpoint:
    """Test suite for PDF download endpoint"""

    def test_download_pdf_endpoint_exists(self):
        """Test that PDF download endpoint exists"""
        response = client.post("/api/download-pdf", json={
            "candidate_name": "John Doe",
            "job_title": "Developer",
            "extracted_resume": {},
            "analysis": {},
            "recruiter_summary": {}
        })
        assert response.status_code != 404, "Endpoint should exist"


class TestErrorHandling:
    """Test suite for error handling"""

    def test_invalid_endpoint_returns_404(self):
        """Test that invalid endpoint returns 404"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404, "Invalid endpoint should return 404"

    def test_invalid_method_returns_error(self):
        """Test that invalid HTTP method returns appropriate error"""
        response = client.get("/api/screen-resume")
        assert response.status_code in [405, 404], "Invalid method should return error"
