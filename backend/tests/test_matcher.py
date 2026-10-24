import pytest
from app.matcher import (
    calculate_skill_alignment,
    calculate_experience_score,
    calculate_tfidf_similarity,
    match_resume_to_job,
    DEFAULT_WEIGHTS
)
from app.parser import normalize_skill, extract_skills_from_text


def test_normalize_skill():
    assert normalize_skill("ReactJS") == "react"
    assert normalize_skill("node.js") == "node.js"
    assert normalize_skill("NodeJS") == "node.js"
    assert normalize_skill("K8s") == "kubernetes"
    assert normalize_skill("TypeScript") == "typescript"


def test_extract_skills_from_text():
    sample_text = """
    Senior Full Stack Engineer with 6+ years of experience in Python, Django, React, and PostgreSQL.
    Proficient with Docker, Kubernetes, and AWS cloud deployments.
    Familiar with GraphQL and CI/CD pipelines.
    """
    skills = extract_skills_from_text(sample_text)
    assert "python" in skills
    assert "django" in skills
    assert "react" in skills
    assert "postgresql" in skills
    assert "docker" in skills
    assert "kubernetes" in skills


def test_skill_alignment_perfect():
    candidate_skills = ["python", "fastapi", "react", "postgresql"]
    required_skills = ["Python", "React", "PostgreSQL"]

    res = calculate_skill_alignment(candidate_skills, required_skills)
    assert res["coverage_ratio"] == 1.0
    assert len(res["matched"]) == 3
    assert len(res["missing"]) == 0


def test_skill_alignment_partial_and_missing():
    candidate_skills = ["python", "django"]
    required_skills = ["Python", "React", "Docker", "AWS"]

    res = calculate_skill_alignment(candidate_skills, required_skills)
    assert res["coverage_ratio"] == 0.25
    assert "Python" in res["matched"]
    assert "React" in res["missing"]
    assert "Docker" in res["missing"]
    assert "AWS" in res["missing"]


def test_skill_alignment_empty_job_requirements():
    candidate_skills = ["python", "react"]
    required_skills = []

    res = calculate_skill_alignment(candidate_skills, required_skills)
    assert res["coverage_ratio"] == 1.0
    assert len(res["missing"]) == 0


def test_experience_scoring():
    # Meets/exceeds
    score_meets = calculate_experience_score(candidate_years=5.0, required_years=3.0)
    assert score_meets["score"] == 100.0

    # Partial
    score_partial = calculate_experience_score(candidate_years=2.0, required_years=4.0)
    assert score_partial["score"] == 50.0

    # Zero required
    score_zero = calculate_experience_score(candidate_years=1.0, required_years=0.0)
    assert score_zero["score"] == 100.0

    # Missing from resume
    score_unspecified = calculate_experience_score(candidate_years=0.0, required_years=3.0)
    assert score_unspecified["score"] == 30.0


def test_tfidf_similarity():
    text1 = "Expert software engineer building distributed cloud systems with Python and Kubernetes"
    text2 = "Looking for a software engineer to build distributed cloud systems using Python"
    sim = calculate_tfidf_similarity(text1, text2)
    assert sim > 0.3

    # Empty text case
    sim_empty = calculate_tfidf_similarity("", text2)
    assert sim_empty == 0.0


def test_match_resume_to_job_comprehensive():
    resume_data = {
        "name": "Jane Doe",
        "skills": ["python", "fastapi", "react", "docker", "postgresql"],
        "experience_years": 4.0,
        "education": ["Bachelor of Science in Computer Science"],
        "projects": ["Built real-time analytics portal with FastAPI and React"],
        "raw_text": "Jane Doe. 4+ years of experience in Python, FastAPI, React, Docker, and PostgreSQL.",
        "warnings": []
    }

    job_data = {
        "title": "Senior Python Developer",
        "description": "Seeking Python engineer with FastAPI and Docker experience",
        "required_skills": ["Python", "FastAPI", "Docker"],
        "preferred_skills": ["React", "Kubernetes"],
        "min_experience": 3.0,
        "education_requirements": "Bachelor"
    }

    result = match_resume_to_job(resume_data, job_data)

    assert result["overall_score"] >= 75.0
    assert "Python" in result["matching_required_skills"]
    assert "FastAPI" in result["matching_required_skills"]
    assert "Docker" in result["matching_required_skills"]
    assert "React" in result["matching_preferred_skills"]
    assert "Kubernetes" in result["missing_preferred_skills"]
    assert "score_breakdown" in result
    assert "ethical_ai_notice" in result


def test_empty_resume_edge_case():
    resume_data = {
        "name": "Empty Candidate",
        "skills": [],
        "experience_years": 0.0,
        "education": [],
        "projects": [],
        "raw_text": "",
        "warnings": ["Empty document detected."]
    }

    job_data = {
        "title": "Frontend Engineer",
        "description": "Need React and TypeScript",
        "required_skills": ["React", "TypeScript"],
        "preferred_skills": ["Tailwind"],
        "min_experience": 2.0,
        "education_requirements": "Bachelor"
    }

    result = match_resume_to_job(resume_data, job_data)
    assert result["overall_score"] < 40.0
    assert len(result["missing_required_skills"]) == 2
    assert len(result["extraction_warnings"]) > 0
