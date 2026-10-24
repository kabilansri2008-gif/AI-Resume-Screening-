-- Supabase PostgreSQL Schema for HireSense AI Screening System
-- Enables UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'recruiter' CHECK (role IN ('recruiter', 'administrator')),
    company_name TEXT DEFAULT 'HireSense Demo Org',
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Jobs Table
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recruiter_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    department TEXT NOT NULL,
    location TEXT NOT NULL,
    employment_type TEXT NOT NULL CHECK (employment_type IN ('Full-time', 'Part-time', 'Contract', 'Remote', 'Hybrid')),
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL DEFAULT '{}',
    preferred_skills TEXT[] NOT NULL DEFAULT '{}',
    min_experience NUMERIC NOT NULL DEFAULT 0,
    education_requirements TEXT DEFAULT 'Bachelor''s Degree',
    certifications TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'draft', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Candidates Table
CREATE TABLE IF NOT EXISTS public.candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recruiter_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    experience_years NUMERIC DEFAULT 0,
    education TEXT[] DEFAULT '{}',
    skills TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'under_review', 'shortlisted', 'interviewed', 'rejected', 'hired')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Resumes Table
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    file_type TEXT,
    raw_text TEXT,
    word_count INTEGER DEFAULT 0,
    confidence_score NUMERIC DEFAULT 95.0,
    warnings TEXT[] DEFAULT '{}',
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Analyses Table (Explainable AI Match Results)
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    overall_score NUMERIC NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    required_skill_score NUMERIC DEFAULT 0,
    preferred_skill_score NUMERIC DEFAULT 0,
    experience_score NUMERIC DEFAULT 0,
    projects_score NUMERIC DEFAULT 0,
    education_score NUMERIC DEFAULT 0,
    matching_required_skills TEXT[] DEFAULT '{}',
    missing_required_skills TEXT[] DEFAULT '{}',
    matching_preferred_skills TEXT[] DEFAULT '{}',
    missing_preferred_skills TEXT[] DEFAULT '{}',
    evidence_snippets JSONB DEFAULT '[]'::jsonb,
    score_breakdown JSONB DEFAULT '{}'::jsonb,
    extraction_warnings TEXT[] DEFAULT '{}',
    recommendation TEXT NOT NULL,
    scoring_methodology TEXT,
    is_llm_enhanced BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Recruiter Notes Table
CREATE TABLE IF NOT EXISTS public.recruiter_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES public.candidates(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Screening Activity Table
CREATE TABLE IF NOT EXISTS public.screening_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recruiter_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
    candidate_id UUID REFERENCES public.candidates(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_recruiter ON public.jobs(recruiter_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_candidates_job ON public.candidates(job_id);
CREATE INDEX IF NOT EXISTS idx_candidates_recruiter ON public.candidates(recruiter_id);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON public.candidates(status);
CREATE INDEX IF NOT EXISTS idx_resumes_candidate ON public.resumes(candidate_id);
CREATE INDEX IF NOT EXISTS idx_analyses_candidate ON public.analyses(candidate_id);
CREATE INDEX IF NOT EXISTS idx_analyses_job ON public.analyses(job_id);
CREATE INDEX IF NOT EXISTS idx_analyses_overall_score ON public.analyses(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_activity_recruiter ON public.screening_activity(recruiter_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recruiter_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.screening_activity ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view and manage their own profile"
    ON public.profiles FOR ALL
    USING (auth.uid() = id);

CREATE POLICY "Recruiters manage own jobs"
    ON public.jobs FOR ALL
    USING (auth.uid() = recruiter_id);

CREATE POLICY "Recruiters manage own candidates"
    ON public.candidates FOR ALL
    USING (auth.uid() = recruiter_id);

CREATE POLICY "Recruiters access resumes of own candidates"
    ON public.resumes FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.candidates
            WHERE candidates.id = resumes.candidate_id
            AND candidates.recruiter_id = auth.uid()
        )
    );

CREATE POLICY "Recruiters access analyses of own candidates"
    ON public.analyses FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.candidates
            WHERE candidates.id = analyses.candidate_id
            AND candidates.recruiter_id = auth.uid()
        )
    );

CREATE POLICY "Recruiters manage notes on own candidates"
    ON public.recruiter_notes FOR ALL
    USING (auth.uid() = recruiter_id);

CREATE POLICY "Recruiters view own activity"
    ON public.screening_activity FOR ALL
    USING (auth.uid() = recruiter_id);
