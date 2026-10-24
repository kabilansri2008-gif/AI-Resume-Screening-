# HireSense AI — Intelligent Resume Screening System

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-Python%20FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20Postgres-3ecf8e?style=flat&logo=supabase)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

HireSense AI is a full-stack, production-grade recruitment SaaS platform engineered to streamline resume parsing, provide transparent and explainable candidate-job matching, and eliminate protected-characteristic hiring bias.

---

## 🌟 Key Features

1. **Multi-Format Resume Parsing**:
   - High-throughput Python microservice utilizing **PyMuPDF (`fitz`)** for PDFs and **`python-docx`** for DOCX files.
   - Extracts candidate contact info (name, email, phone, LinkedIn), skill sets, experience chronologies, education, and projects.
   - Graceful handling of scanned documents, empty files, or corrupted archives with informative warnings and confidence scores.

2. **Explainable 5-Factor AI Matching Engine**:
   - **40% Required Skills Coverage**: Normalized exact & synonym taxonomy matching (`ReactJS` $\leftrightarrow$ `React`, `k8s` $\leftrightarrow$ `Kubernetes`).
   - **15% Preferred Skills Coverage**: Bonus competencies that elevate suitability without penalizing if omitted from job specs.
   - **20% Relevant Experience**: Quantitative years verification against minimum criteria.
   - **15% Project & Work Evidence**: NLP Term Frequency-Inverse Document Frequency (**TF-IDF**) vectorization and cosine similarity.
   - **10% Education & Certifications**: Degree relevance checks.
   - **Configurable Weights**: Recruiters and Admins can customize scoring weights directly in settings.

3. **Responsible AI & Anti-Bias Framework**:
   - Zero protected attributes (age, gender, ethnicity, religion, caste, photograph) are extracted or used in calculations.
   - Textual citations extracted from the resume back up every scoring decision.
   - Clear compliance notice that scores are decision-support heuristics, not automated hiring verdicts.

4. **16 Production SaaS Pages**:
   1. **Landing Page (`/`)**: Hero section, live interactive candidate preview gauge, 3-step workflow, feature cards, and anti-bias pledge.
   2. **Sign In (`/login`)**: Secure authentication with one-click Demo Recruiter and Demo Admin access.
   3. **Sign Up (`/signup`)**: Recruiter & Administrator role registration.
   4. **Password Reset (`/forgot-password`)**: Recovery instructions with confirmation status.
   5. **Recruiter Dashboard (`/dashboard`)**: KPI metrics, candidate score distribution histogram, applicant volume breakdown, and recent activity.
   6. **Job Openings (`/dashboard/jobs`)**: Filterable job directory with status toggling (active, draft, archived).
   7. **Create Job (`/dashboard/jobs/new`)**: Structured job specification builder with raw JD paste auto-fill.
   8. **Edit Job (`/dashboard/jobs/[id]/edit`)**: Modify requirements, skills, or seniorities.
   9. **Job Details (`/dashboard/jobs/[id]`)**: Deep-dive into job requirements and ranked candidate applicant pool.
   10. **Resume Upload & Batch Screening (`/dashboard/upload`)**: Drag-and-drop batch PDF/DOCX upload with progress indicators and instant demo preloader.
   11. **Candidate Pool (`/dashboard/candidates`)**: Searchable candidate directory with multi-tier score filters, pipeline status updates, and multi-selection comparison.
   12. **Candidate Details & AI Analysis (`/dashboard/candidates/[id]`)**: Explainable dossier with SVG score gauge, radar chart, matched vs missing skills, extracted citations, and recruiter notes.
   13. **Side-by-Side Candidate Comparison (`/dashboard/candidates/compare`)**: Objective comparative evaluation matrix.
   14. **Reports & Exports (`/dashboard/reports`)**: Downloadable CSV spreadsheets and printable candidate PDF dossiers.
   15. **Screening Audit Trail (`/dashboard/activity`)**: Chronological event log of screenings and recruiter decisions.
   16. **User Settings & Customization (`/dashboard/settings`)**: Profile settings, role switching, database state, and algorithm weight customizer.
   17. **Methodology & Architecture Guide (`/dashboard/help`)**: In-depth mathematical explanation and FAQ.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide React, Recharts, Canvas Confetti.
- **Backend (Python)**: FastAPI, PyMuPDF, python-docx, Scikit-learn, NumPy, Uvicorn, Pytest.
- **Database & Auth**: Supabase PostgreSQL, Row-Level Security (RLS) policies, plus local persistence demo fallback.
- **Export Engine**: Client-side safe CSV generator & printable PDF dossier stylesheets.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/AI-resume-screening.git
cd AI-resume-screening
```

### 2. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

> **Note**: HireSense AI features a **Zero-Friction Demo Mode**. Even before configuring Supabase keys, all 16 pages, resume parsing, matching, and comparisons work out-of-the-box using the pre-seeded local storage adapter!

### 3. Python AI Backend Service Setup
In a separate terminal window:
```bash
cd backend
python -m venv .venv

# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
FastAPI interactive Swagger docs will be live at: **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🧪 Running the Unit Test Suite

The Python matching algorithm and edge cases are validated using Pytest:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

### Test Suite Highlights:
- `test_normalize_skill`: Validates synonym normalization (`ReactJS` $\rightarrow$ `react`, `k8s` $\rightarrow$ `kubernetes`).
- `test_extract_skills_from_text`: Verifies NLP regex skill extraction.
- `test_skill_alignment_perfect` & `partial`: Tests coverage ratios and missing skill flags.
- `test_experience_scoring`: Tests meeting, exceeding, partial, and unspecified years of experience.
- `test_tfidf_similarity`: Tests term vector cosine similarity calculations.
- `test_match_resume_to_job_comprehensive`: Validates end-to-end multi-vector weighted scoring.
- `test_empty_resume_edge_case`: Ensures empty or non-extractable resumes produce useful warnings without crashing.

---

## 📁 Sample Resumes for Instant Testing

Realistic sample resumes are pre-generated in the `sample_resumes/` folder:
1. `alex_mercer_lead_ai.pdf` (PDF format - Strong Match, 92%)
2. `sarah_chen_fullstack.docx` (DOCX format - Good Match, 78.5%)
3. `david_patel_junior_dev.pdf` (PDF format - Moderate Match, 58%)

You can upload these files directly in the **Upload & Screen** page or click the **"Load 3 Sample Resumes (Instant Demo)"** button for one-click testing!

---

## 🗄️ Database Migrations & Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com).
2. Run the SQL migration in `supabase/migrations/20261024000000_init_schema.sql` via the Supabase SQL Editor.
3. (Optional) Run the seed script in `supabase/seed.sql` to populate sample jobs and candidate evaluations.
4. Copy your credentials to `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
   NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
   ```

---

## 🛡️ Ethical AI & Anti-Bias Notice

HireSense AI complies with EEOC guidelines and Responsible AI frameworks. The platform does not use age, gender, race, ethnicity, religion, caste, disability, or personal photographs to calculate candidate scores. All AI output must be reviewed by a human recruiter before taking hiring actions.
#   A I - R e s u m e - S c r e e n i n g -  
 