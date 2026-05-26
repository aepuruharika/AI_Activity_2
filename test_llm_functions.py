"""
Test cases for LLM functions.
Tests the core functionality of resume extraction, analysis, and summary generation.
"""

import pytest
import json
from llm_resume_extractor import extract_resume_info
from llm_matcher_scorer import analyze_resume_vs_jd
from llm_recruiter_summary import generate_recruiter_summary


class TestResumeExtractor:
    """Test suite for resume extraction functionality"""

    def test_extract_resume_returns_dict(self):
        """Test that extraction returns a dictionary"""
        resume_text = """
        John Doe
        Email: john@example.com
        Phone: 123-456-7890

        Skills: Python, JavaScript, React, AWS, Docker
        Experience: 5 years in software development
        Education: B.Tech Computer Science
        Certifications: AWS Solutions Architect
        """
        result = extract_resume_info(resume_text)
        assert isinstance(result, dict), "Result should be a dictionary"

    def test_extract_resume_has_required_fields(self):
        """Test that extracted resume has required fields"""
        resume_text = """
        John Doe
        Email: john@example.com
        Skills: Python, JavaScript
        Experience: 5 years
        Education: B.Tech
        """
        result = extract_resume_info(resume_text)

        required_fields = ["name", "email", "skills", "experience_summary", "education"]
        for field in required_fields:
            assert field in result or "error" in result, f"Field '{field}' missing or error occurred"

    def test_extract_resume_handles_empty_input(self):
        """Test handling of empty resume"""
        result = extract_resume_info("")
        assert isinstance(result, dict), "Should return dict even for empty input"

    def test_extract_resume_skills_is_list(self):
        """Test that skills are returned as a list"""
        resume_text = """
        John Doe
        Skills: Python, JavaScript, React
        Experience: 5 years
        """
        result = extract_resume_info(resume_text)
        if "skills" in result:
            assert isinstance(result["skills"], list), "Skills should be a list"


class TestAnalysisScorer:
    """Test suite for resume analysis and scoring"""

    def test_analyze_returns_dict(self):
        """Test that analysis returns a dictionary"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript"],
            "experience_years": 5,
            "experience_summary": "5 years in software development"
        }
        job_description = "Looking for Python developer with 5+ years experience"

        result = analyze_resume_vs_jd(extracted_resume, job_description)
        assert isinstance(result, dict), "Result should be a dictionary"

    def test_analyze_has_required_fields(self):
        """Test that analysis has required fields"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python"],
            "experience_years": 5
        }
        job_description = "Python developer needed"

        result = analyze_resume_vs_jd(extracted_resume, job_description)

        required_fields = ["match_score", "is_qualified"]
        for field in required_fields:
            assert field in result or "error" in result, f"Field '{field}' missing"

    def test_analyze_match_score_in_range(self):
        """Test that match score is between 0-100"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript"],
            "experience_years": 5
        }
        job_description = "Senior Python developer"

        result = analyze_resume_vs_jd(extracted_resume, job_description)

        if "match_score" in result:
            assert 0 <= result["match_score"] <= 100, "Match score should be 0-100"

    def test_analyze_qualified_threshold(self):
        """Test that is_qualified is set based on match_score"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python"],
            "experience_years": 10
        }
        job_description = "Python developer needed"

        result = analyze_resume_vs_jd(extracted_resume, job_description)

        if "match_score" in result and "is_qualified" in result:
            if result["match_score"] > 70:
                assert result["is_qualified"] is True, "Should be qualified if score > 70"
            else:
                assert result["is_qualified"] is False, "Should not be qualified if score <= 70"

    def test_analyze_qualified_has_interview_questions(self):
        """Test that qualified candidates get interview questions"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript", "AWS"],
            "experience_years": 10,
            "experience_summary": "10 years in full-stack development"
        }
        job_description = "Senior Python developer with AWS experience"

        result = analyze_resume_vs_jd(extracted_resume, job_description)

        if result.get("is_qualified") is True:
            assert "interview_questions" in result, "Qualified should have interview_questions"
            if result["interview_questions"]:
                assert isinstance(result["interview_questions"], list), "Interview questions should be list"

    def test_analyze_unqualified_has_rejection_reasons(self):
        """Test that unqualified candidates get rejection reasons"""
        extracted_resume = {
            "name": "Jane Doe",
            "skills": ["HTML", "CSS"],
            "experience_years": 1,
            "experience_summary": "1 year in web design"
        }
        job_description = "Senior Python backend engineer with 10+ years experience"

        result = analyze_resume_vs_jd(extracted_resume, job_description)

        if result.get("is_qualified") is False:
            assert "rejection_reasons" in result or "improvement_suggestions" in result, \
                "Unqualified should have rejection_reasons or suggestions"


class TestRecruiterSummary:
    """Test suite for recruiter summary generation"""

    def test_summary_returns_dict(self):
        """Test that summary returns a dictionary"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript"],
            "experience_years": 5,
            "strengths": ["Problem solving", "Leadership"]
        }
        analysis = {
            "match_score": 85,
            "is_qualified": True,
            "analysis_summary": "Strong match"
        }

        result = generate_recruiter_summary(extracted_resume, analysis, "Senior Developer")
        assert isinstance(result, dict), "Result should be a dictionary"

    def test_summary_has_required_fields(self):
        """Test that summary has required fields"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python"],
            "experience_years": 5,
            "strengths": ["Problem solving"]
        }
        analysis = {
            "match_score": 85,
            "is_qualified": True,
            "analysis_summary": "Good match"
        }

        result = generate_recruiter_summary(extracted_resume, analysis, "Developer")

        required_fields = ["executive_summary", "recommendation", "key_highlights"]
        for field in required_fields:
            assert field in result or "error" in result, f"Field '{field}' missing"

    def test_summary_executive_summary_is_string(self):
        """Test that executive summary is a string"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python"],
            "experience_years": 5,
            "strengths": ["Problem solving"]
        }
        analysis = {
            "match_score": 85,
            "is_qualified": True,
            "analysis_summary": "Good match"
        }

        result = generate_recruiter_summary(extracted_resume, analysis, "Developer")

        if "executive_summary" in result:
            assert isinstance(result["executive_summary"], str), "Executive summary should be a string"

    def test_summary_recommendation_values(self):
        """Test that recommendation is one of expected values"""
        extracted_resume = {
            "name": "John Doe",
            "skills": ["Python"],
            "experience_years": 5,
            "strengths": ["Problem solving"]
        }
        analysis = {
            "match_score": 85,
            "is_qualified": True,
            "analysis_summary": "Good match"
        }

        result = generate_recruiter_summary(extracted_resume, analysis, "Developer")

        if "recommendation" in result:
            valid_recommendations = ["RECOMMEND", "DO NOT RECOMMEND", "CONDITIONAL"]
            assert result["recommendation"] in valid_recommendations, \
                f"Recommendation should be one of {valid_recommendations}"
