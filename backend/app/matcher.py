import re
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .parser import normalize_skill


DEFAULT_WEIGHTS = {
    "required_skills": 0.40,
    "preferred_skills": 0.15,
    "experience": 0.20,
    "projects": 0.15,
    "education": 0.10,
}


def calculate_skill_alignment(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    norm_candidate = {normalize_skill(s) for s in candidate_skills}
    norm_required = [normalize_skill(s) for s in required_skills]

    matched = []
    missing = []

    for orig_req, norm_req in zip(required_skills, norm_required):
        # Check direct or synonym or substring
        is_matched = False
        if norm_req in norm_candidate:
            is_matched = True
        else:
            for c_skill in norm_candidate:
                if norm_req in c_skill or c_skill in norm_req:
                    is_matched = True
                    break

        if is_matched:
            matched.append(orig_req)
        else:
            missing.append(orig_req)

    coverage = len(matched) / len(required_skills) if required_skills else 1.0
    return {
        "matched": matched,
        "missing": missing,
        "coverage_ratio": min(coverage, 1.0),
        "score_contribution": round(min(coverage, 1.0) * 100, 2)
    }


def calculate_experience_score(candidate_years: float, required_years: float) -> Dict[str, Any]:
    if required_years <= 0:
        score = 100.0
        status = "Meets experience requirements"
    elif candidate_years >= required_years:
        score = 100.0
        status = f"Exceeds/meets required {required_years} years ({candidate_years} yrs verified)"
    elif candidate_years > 0:
        ratio = candidate_years / required_years
        score = max(20.0, ratio * 100)
        status = f"{candidate_years} yrs out of {required_years} required years"
    else:
        score = 30.0  # Experience not explicitly specified in resume format
        status = "Not explicitly stated in resume header; requires human recruiter verification"

    return {
        "score": round(score, 2),
        "candidate_years": candidate_years,
        "required_years": required_years,
        "status": status
    }


def calculate_tfidf_similarity(resume_text: str, job_text: str) -> float:
    if not resume_text.strip() or not job_text.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(np.clip(sim, 0.0, 1.0))
    except Exception:
        return 0.5


def extract_relevant_evidence(resume_text: str, required_skills: List[str]) -> List[str]:
    """Finds exact sentences or bullet points in the resume that mention required skills."""
    evidence = []
    lines = [line.strip() for line in resume_text.split('\n') if len(line.strip()) > 20]

    for skill in required_skills[:5]:
        pattern = re.compile(rf'\b{re.escape(skill)}\b', re.IGNORECASE)
        for line in lines:
            if pattern.search(line):
                cleaned = line.lstrip('•-* 0123456789. ')
                if cleaned not in evidence and len(cleaned) <= 180:
                    evidence.append(cleaned)
                    break
    return evidence[:4]


def match_resume_to_job(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    weights = custom_weights or DEFAULT_WEIGHTS

    req_skills = job_data.get("required_skills", [])
    pref_skills = job_data.get("preferred_skills", [])
    min_exp = float(job_data.get("min_experience", 0))
    job_desc = job_data.get("description", "")
    job_title = job_data.get("title", "")
    full_job_text = f"{job_title} {job_desc} {' '.join(req_skills)} {' '.join(pref_skills)}"

    candidate_skills = resume_data.get("skills", [])
    candidate_exp = float(resume_data.get("experience_years", 0))
    resume_text = resume_data.get("raw_text", "")

    # 1. Required Skills Alignment (40%)
    req_alignment = calculate_skill_alignment(candidate_skills, req_skills)
    req_score = req_alignment["coverage_ratio"] * 100

    # 2. Preferred Skills Alignment (15%)
    pref_alignment = calculate_skill_alignment(candidate_skills, pref_skills)
    pref_score = pref_alignment["coverage_ratio"] * 100 if pref_skills else 100.0

    # 3. Relevant Experience Alignment (20%)
    exp_alignment = calculate_experience_score(candidate_exp, min_exp)
    exp_score = exp_alignment["score"]

    # 4. Project & Work Evidence (TF-IDF + project presence) (15%)
    tfidf_sim = calculate_tfidf_similarity(resume_text, full_job_text)
    projects_count = len(resume_data.get("projects", []))
    project_presence_factor = min(1.0, projects_count / 2.0)
    # Blend TF-IDF similarity with project evidence
    projects_score = ((tfidf_sim * 0.7) + (project_presence_factor * 0.3)) * 100
    projects_score = min(100.0, max(20.0, projects_score))

    # 5. Education & Certification Alignment (10%)
    edu_list = resume_data.get("education", [])
    req_edu = job_data.get("education_requirements", "").lower()
    edu_score = 70.0
    edu_status = "Education information detected in resume."
    if not edu_list:
        edu_score = 40.0
        edu_status = "No explicit degree mentioned; manual review suggested."
    elif req_edu:
        matched_edu = any(req_edu in e.lower() or any(deg in e.lower() for deg in ["bachelor", "master", "b.tech", "degree"]) for e in edu_list)
        if matched_edu:
            edu_score = 95.0
            edu_status = "Meets or aligns with degree requirements."

    # Compute Total Weighted Heuristic Score
    w_req = weights.get("required_skills", 0.40)
    w_pref = weights.get("preferred_skills", 0.15)
    w_exp = weights.get("experience", 0.20)
    w_proj = weights.get("projects", 0.15)
    w_edu = weights.get("education", 0.10)

    total_score = (
        (req_score * w_req) +
        (pref_score * w_pref) +
        (exp_score * w_exp) +
        (projects_score * w_proj) +
        (edu_score * w_edu)
    )

    total_score = round(min(100.0, max(0.0, total_score)), 1)

    # Relevant evidence snippet extraction
    evidence = extract_relevant_evidence(resume_text, req_alignment["matched"])

    # Warnings and confidence limitations
    warnings = list(resume_data.get("warnings", []))
    if not req_alignment["matched"]:
        warnings.append("Zero required skills directly detected; score relies purely on text similarity.")
    if candidate_exp == 0 and min_exp > 0:
        warnings.append(f"Job requires {min_exp} years, but resume does not state years in standard numeric format.")

    score_breakdown = {
        "required_skills": {
            "score": round(req_score, 1),
            "weight": w_req,
            "weighted_value": round(req_score * w_req, 1),
            "matched_count": len(req_alignment["matched"]),
            "total_count": len(req_skills)
        },
        "preferred_skills": {
            "score": round(pref_score, 1),
            "weight": w_pref,
            "weighted_value": round(pref_score * w_pref, 1),
            "matched_count": len(pref_alignment["matched"]),
            "total_count": len(pref_skills)
        },
        "experience": {
            "score": round(exp_score, 1),
            "weight": w_exp,
            "weighted_value": round(exp_score * w_exp, 1),
            "candidate_years": candidate_exp,
            "required_years": min_exp
        },
        "projects_and_evidence": {
            "score": round(projects_score, 1),
            "weight": w_proj,
            "weighted_value": round(projects_score * w_proj, 1),
            "tfidf_similarity": round(tfidf_sim, 3)
        },
        "education": {
            "score": round(edu_score, 1),
            "weight": w_edu,
            "weighted_value": round(edu_score * w_edu, 1),
            "status": edu_status
        }
    }

    # Recommendation category
    if total_score >= 80:
        recommendation = "Strong Match"
        status_tag = "Recommended for Interview"
    elif total_score >= 65:
        recommendation = "Good Match"
        status_tag = "Requires Recruiter Review"
    elif total_score >= 50:
        recommendation = "Moderate Match"
        status_tag = "Secondary Consideration"
    else:
        recommendation = "Low Alignment"
        status_tag = "Review Missing Qualifications"

    return {
        "overall_score": total_score,
        "recommendation": recommendation,
        "status_tag": status_tag,
        "matching_required_skills": req_alignment["matched"],
        "missing_required_skills": req_alignment["missing"],
        "matching_preferred_skills": pref_alignment["matched"],
        "missing_preferred_skills": pref_alignment["missing"],
        "experience_status": exp_alignment["status"],
        "education_alignment": edu_status,
        "evidence_snippets": evidence,
        "score_breakdown": score_breakdown,
        "extraction_warnings": warnings,
        "weights_used": weights,
        "scoring_methodology": (
            "Score is a deterministic heuristic composite (40% Required Skills, 15% Preferred Skills, "
            "20% Experience, 15% Project/Text Alignment via TF-IDF cosine similarity, 10% Education). "
            "Scores represent alignment indicators and NOT hiring guarantees. Human recruiter verification is mandatory."
        ),
        "ethical_ai_notice": (
            "HireSense AI complies with responsible recruitment guidelines. No demographic, gender, age, "
            "ethnicity, religion, or personal protected traits are factored into score calculation."
        )
    }
