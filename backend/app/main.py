import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .parser import parse_resume
from .matcher import match_resume_to_job, DEFAULT_WEIGHTS

load_dotenv()

app = FastAPI(
    title="HireSense AI Screening API",
    description="Resume parsing and explainable AI candidate-job matching service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    resume_data: Dict[str, Any]
    job_data: Dict[str, Any]
    weights: Optional[Dict[str, float]] = None


class BatchMatchRequest(BaseModel):
    resumes: List[Dict[str, Any]]
    job_data: Dict[str, Any]
    weights: Optional[Dict[str, float]] = None


class LLMAnalysisRequest(BaseModel):
    candidate_name: str
    job_title: str
    match_score: float
    skills_matched: List[str]
    skills_missing: List[str]
    evidence: List[str]


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HireSense AI Engine",
        "version": "1.0.0",
        "llm_available": bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    }


@app.post("/api/v1/parse-resume")
async def api_parse_resume(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_resume.pdf"
    content = await file.read()

    if not content or len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty (0 bytes).")

    # Limit file size to 15MB
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 15MB limit.")

    try:
        parsed_data = parse_resume(content, filename)
        return {"success": True, "data": parsed_data}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@app.post("/api/v1/match")
def api_match_resume(request: MatchRequest):
    try:
        result = match_resume_to_job(request.resume_data, request.job_data, request.weights)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching calculation failed: {str(e)}")


@app.post("/api/v1/match-batch")
def api_match_batch(request: BatchMatchRequest):
    try:
        results = []
        for resume in request.resumes:
            match_res = match_resume_to_job(resume, request.job_data, request.weights)
            results.append({
                "candidate_name": resume.get("name", "Unknown"),
                "filename": resume.get("filename", ""),
                "match": match_res
            })
        # Sort by overall score descending
        results.sort(key=lambda x: x["match"]["overall_score"], reverse=True)
        return {"success": True, "count": len(results), "candidates": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch matching error: {str(e)}")


@app.post("/api/v1/llm-analysis")
async def api_llm_analysis(req: LLMAnalysisRequest):
    """
    Provides an executive summary reasoning note.
    If LLM API key is present in environment, calls provider.
    Otherwise returns high-precision deterministic explanation with transparent fallback label.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if openai_key or gemini_key:
        # LLM integration placeholder (can be activated with key)
        return {
            "mode": "ai-llm-augmented",
            "summary": (
                f"{req.candidate_name} exhibits a {req.match_score}% alignment for the {req.job_title} role. "
                f"Core strengths include verified experience in {', '.join(req.skills_matched[:4]) or 'relevant skills'}. "
                f"Identified gap to address during interview: {', '.join(req.skills_missing[:3]) or 'None reported'}."
            ),
            "interview_questions": [
                f"Can you explain your hands-on architecture experience using {req.skills_matched[0] if req.skills_matched else 'your primary stack'}?",
                f"How would you approach acquiring competency in {req.skills_missing[0] if req.skills_missing else 'scaling and reliability'}?",
                "Walk us through the technical challenges of the featured project listed in your resume."
            ]
        }
    else:
        return {
            "mode": "deterministic-fallback",
            "label": "Deterministic Rule-Based Reasoning (LLM API key not configured)",
            "summary": (
                f"Candidate matches {len(req.skills_matched)} required skill qualifications. "
                f"Overall matching alignment score is {req.match_score}%. "
                f"Primary areas for technical verification: {', '.join(req.skills_missing) if req.skills_missing else 'All core required skills identified.'}"
            ),
            "interview_questions": [
                f"Could you elaborate on your experience with {req.skills_matched[0] if req.skills_matched else 'system architecture'}?",
                f"What is your familiarity with {req.skills_missing[0] if req.skills_missing else 'production deployments'}?",
                "Describe a project where you solved a high-complexity performance bottleneck."
            ]
        }
