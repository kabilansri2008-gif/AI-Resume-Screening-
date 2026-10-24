-- HireSense AI Screening System - Seed Data
-- Realistic sample data for demonstration (Clearly labeled as Demo Data)

-- 1. Demo Profile
INSERT INTO public.profiles (id, email, full_name, role, company_name)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'recruiter@hiresense.ai', 'Marcus Vance', 'recruiter', 'Nexus Global Tech')
ON CONFLICT (id) DO NOTHING;

-- 2. Demo Jobs
INSERT INTO public.jobs (id, recruiter_id, title, department, location, employment_type, description, required_skills, preferred_skills, min_experience, education_requirements, status)
VALUES 
    (
        '10000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        'Lead Full Stack AI Engineer',
        'Engineering',
        'San Francisco, CA (Hybrid)',
        'Full-time',
        'We are seeking an experienced Full Stack AI Engineer to spearhead our intelligent automation platform. You will design scalable microservices using Python and FastAPI, craft responsive web interfaces with React and Next.js, and maintain robust PostgreSQL databases in containerized Docker environments.',
        ARRAY['python', 'react', 'fastapi', 'postgresql', 'docker'],
        ARRAY['next.js', 'kubernetes', 'langchain', 'aws'],
        4.0,
        'Bachelor of Science in Computer Science or equivalent',
        'active'
    ),
    (
        '10000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        'Senior Frontend Developer',
        'Product & Design',
        'Remote (US / Canada)',
        'Remote',
        'Looking for a Senior Frontend Developer to elevate our user interface design system. Candidate must possess deep mastery of TypeScript, modern React, Tailwind CSS, and Next.js architecture with strong state management principles.',
        ARRAY['react', 'typescript', 'tailwind css', 'next.js'],
        ARRAY['graphql', 'jest', 'playwright', 'figma'],
        3.0,
        'Bachelor of Science or relevant portfolio',
        'active'
    ),
    (
        '10000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        'Cloud Infrastructure & DevOps Engineer',
        'Infrastructure',
        'New York, NY (On-site)',
        'Full-time',
        'Responsible for managing mission-critical AWS cloud infrastructure, orchestrating Kubernetes clusters, building automated CI/CD pipelines, and writing infrastructure-as-code using Terraform.',
        ARRAY['aws', 'kubernetes', 'docker', 'terraform', 'ci/cd'],
        ARRAY['python', 'helm', 'linux', 'prometheus'],
        5.0,
        'Bachelor of Science in Engineering or Computer Science',
        'active'
    )
ON CONFLICT (id) DO NOTHING;

-- 3. Demo Candidates
INSERT INTO public.candidates (id, recruiter_id, job_id, name, email, phone, linkedin_url, github_url, experience_years, education, skills, status)
VALUES
    (
        '20000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'Alex Mercer',
        'alex.mercer.dev@example.com',
        '+1 (555) 382-9102',
        'https://linkedin.com/in/alex-mercer',
        'https://github.com/alexmercer',
        5.5,
        ARRAY['B.S. in Computer Science - University of Washington'],
        ARRAY['python', 'react', 'fastapi', 'postgresql', 'docker', 'aws', 'next.js', 'git'],
        'shortlisted'
    ),
    (
        '20000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'Sarah Chen',
        'sarah.chen.tech@example.com',
        '+1 (555) 749-2184',
        'https://linkedin.com/in/sarahchen-swe',
        'https://github.com/sarahchen',
        4.0,
        ARRAY['M.S. in Software Systems - Georgia Tech'],
        ARRAY['python', 'react', 'fastapi', 'postgresql', 'typescript', 'tailwind css'],
        'under_review'
    ),
    (
        '20000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'David Patel',
        'david.patel.cloud@example.com',
        '+1 (555) 492-8172',
        'https://linkedin.com/in/davidpatel',
        'https://github.com/davidpatel',
        2.5,
        ARRAY['B.E. in Information Technology - Pune University'],
        ARRAY['python', 'react', 'mongodb', 'node.js', 'docker'],
        'new'
    ),
    (
        '20000000-0000-0000-0000-000000000004',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'Elena Rostova',
        'elena.rostova@example.com',
        '+1 (555) 912-4029',
        'https://linkedin.com/in/elenarostova',
        'https://github.com/erostova',
        3.0,
        ARRAY['B.S. in Applied Mathematics - St. Petersburg State'],
        ARRAY['java', 'spring boot', 'mysql', 'docker', 'linux'],
        'rejected'
    )
ON CONFLICT (id) DO NOTHING;

-- 4. Demo Explainable Analyses
INSERT INTO public.analyses (
    id, candidate_id, job_id, overall_score,
    required_skill_score, preferred_skill_score, experience_score, projects_score, education_score,
    matching_required_skills, missing_required_skills, matching_preferred_skills, missing_preferred_skills,
    evidence_snippets, score_breakdown, extraction_warnings, recommendation, scoring_methodology
)
VALUES
    (
        '30000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        92.0,
        100.0, 75.0, 100.0, 88.0, 95.0,
        ARRAY['python', 'react', 'fastapi', 'postgresql', 'docker'],
        ARRAY[]::text[],
        ARRAY['next.js', 'aws'],
        ARRAY['kubernetes', 'langchain'],
        '[
            "Architected high-throughput microservices using Python and FastAPI serving 1M+ daily active requests",
            "Designed reactive client dashboard in React & Next.js connected to PostgreSQL RDS cluster",
            "Containerized application fleet with Docker and integrated automated CI/CD deployment pipelines"
        ]'::jsonb,
        '{
            "required_skills": {"score": 100.0, "weight": 0.40, "weighted": 40.0},
            "preferred_skills": {"score": 75.0, "weight": 0.15, "weighted": 11.25},
            "experience": {"score": 100.0, "weight": 0.20, "weighted": 20.0},
            "projects_and_evidence": {"score": 88.0, "weight": 0.15, "weighted": 13.2},
            "education": {"score": 95.0, "weight": 0.10, "weighted": 9.5}
        }'::jsonb,
        ARRAY[]::text[],
        'Strong Match - Top Tier Alignment',
        'Evaluated via HireSense AI 5-factor deterministic formula (40% Required Skills, 15% Preferred, 20% Experience, 15% Project/Evidence, 10% Education).'
    ),
    (
        '30000000-0000-0000-0000-000000000002',
        '20000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        78.5,
        80.0, 50.0, 100.0, 75.0, 95.0,
        ARRAY['python', 'react', 'fastapi', 'postgresql'],
        ARRAY['docker'],
        ARRAY['next.js'],
        ARRAY['kubernetes', 'langchain', 'aws'],
        '[
            "Implemented REST APIs in Python using FastAPI with PostgreSQL persistence layer",
            "Built modular UI component library in React with responsive Tailwind CSS styling"
        ]'::jsonb,
        '{
            "required_skills": {"score": 80.0, "weight": 0.40, "weighted": 32.0},
            "preferred_skills": {"score": 50.0, "weight": 0.15, "weighted": 7.5},
            "experience": {"score": 100.0, "weight": 0.20, "weighted": 20.0},
            "projects_and_evidence": {"score": 75.0, "weight": 0.15, "weighted": 11.25},
            "education": {"score": 95.0, "weight": 0.10, "weighted": 9.5}
        }'::jsonb,
        ARRAY['Docker containerization skill missing from explicit experience section']::text[],
        'Good Match - Recruiter Review Recommended',
        'Evaluated via HireSense AI 5-factor deterministic formula.'
    )
ON CONFLICT (id) DO NOTHING;

-- 5. Screening Activity
INSERT INTO public.screening_activity (id, recruiter_id, job_id, candidate_id, action_type, description)
VALUES
    (
        '40000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        'RESUME_MATCHED',
        'Screened Alex Mercer against Lead Full Stack AI Engineer: Score 92.0%'
    ),
    (
        '40000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000002',
        'RESUME_MATCHED',
        'Screened Sarah Chen against Lead Full Stack AI Engineer: Score 78.5%'
    ),
    (
        '40000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        'STATUS_UPDATED',
        'Updated Alex Mercer application status to Shortlisted'
    )
ON CONFLICT (id) DO NOTHING;
