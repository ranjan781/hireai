import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.matchers.jd_matcher import JDMatcher
from app.ml.gap_analyzer.analyzer import analyze_gap

matcher = JDMatcher()

def test_perfect_match():
    """Saari required skills hain toh high score aana chahiye"""
    result = matcher.calculate_match(
        resume_skills=["Python", "FastAPI", "Docker", "AWS", "PostgreSQL"],
        resume_text="Experienced Python developer with FastAPI Docker AWS PostgreSQL",
        required_skills=["Python", "FastAPI", "Docker", "AWS", "PostgreSQL"],
        preferred_skills=[],
        jd_text="Python FastAPI Docker AWS PostgreSQL developer needed"
    )
    assert result["match_score"] >= 70
    assert len(result["missing_skills"]) == 0
    assert len(result["strong_skills"]) > 0

def test_no_skills_match():
    """Koi skill match nahi — low score aana chahiye"""
    result = matcher.calculate_match(
        resume_skills=["Java", "Spring"],
        resume_text="Java Spring developer",
        required_skills=["Python", "FastAPI", "Docker", "AWS"],
        preferred_skills=[],
        jd_text="Python FastAPI Docker AWS developer needed"
    )
    assert result["match_score"] < 50
    assert len(result["missing_skills"]) > 0

def test_partial_match():
    """Kuch skills match — medium score"""
    result = matcher.calculate_match(
        resume_skills=["Python", "Git"],
        resume_text="Python developer with Git experience",
        required_skills=["Python", "FastAPI", "Docker", "AWS"],
        preferred_skills=[],
        jd_text="Python FastAPI Docker AWS developer"
    )
    assert 0 < result["match_score"] < 80
    assert "Python" in result["strong_skills"]
    assert len(result["missing_skills"]) > 0

def test_gap_analysis_grade():
    """Score ke hisaab se grade sahi hona chahiye"""
    high_result = {"match_score": 90, "strong_skills": ["Python"], "weak_skills": [], "missing_skills": [], "score_breakdown": {}}
    gap_high = analyze_gap(high_result)
    assert gap_high["grade"] == "A"

    low_result = {"match_score": 30, "strong_skills": [], "weak_skills": [], "missing_skills": ["Python"], "score_breakdown": {}}
    gap_low = analyze_gap(low_result)
    assert gap_low["grade"] in ["D", "F"]

def test_gap_analysis_recommendation():
    """AI recommendation generate honi chahiye"""
    result = {"match_score": 85, "strong_skills": ["Python", "FastAPI"], "weak_skills": [], "missing_skills": [], "score_breakdown": {}}
    gap = analyze_gap(result)
    assert gap["ai_recommendation"] is not None
    assert len(gap["ai_recommendation"]) > 10

def test_empty_skills():
    """Empty skills handle honi chahiye"""
    result = matcher.calculate_match(
        resume_skills=[],
        resume_text="",
        required_skills=["Python"],
        preferred_skills=[],
        jd_text="Python developer"
    )
    assert result["match_score"] >= 0
    assert isinstance(result["missing_skills"], list)

def test_score_range():
    """Score 0-100 ke beech hona chahiye"""
    result = matcher.calculate_match(
        resume_skills=["Python", "FastAPI"],
        resume_text="Python FastAPI developer",
        required_skills=["Python"],
        preferred_skills=["FastAPI"],
        jd_text="Python developer preferred FastAPI"
    )
    assert 0 <= result["match_score"] <= 100