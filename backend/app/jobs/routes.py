import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from ..models import User, ResumeAnalysis, JobApplication
from ..auth.jwt_handler import get_current_user
from ..ai_client import call_ai
from .schemas import (
    JobListingOut, MatchScoreRequest, MatchScoreOut,
    CoverLetterRequest, CoverLetterOut,
    ApplyRequest, JobApplicationOut, StatusUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


DEMO_JOBS = [
    {
        "job_id": "job-001",
        "job_title": "Software Engineer",
        "company": "TechNova Solutions",
        "location": "Hyderabad, Telangana",
        "description": "Software Engineer with Python, Java, SQL, REST APIs, Git, React and problem solving.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹6L - ₹12L",
        "posted_date": "2026-10-08",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-002",
        "job_title": "Backend Developer",
        "company": "CloudBridge Technologies",
        "location": "Hyderabad, Telangana",
        "description": "Backend Developer requiring Python, FastAPI, PostgreSQL, REST APIs, Git and database knowledge.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹7L - ₹14L",
        "posted_date": "2026-10-08",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-003",
        "job_title": "Frontend Developer",
        "company": "PixelWorks Technologies",
        "location": "Hyderabad, Telangana",
        "description": "Frontend Developer requiring HTML, CSS, JavaScript, React, TypeScript and Git.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹5L - ₹11L",
        "posted_date": "2026-10-08",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-004",
        "job_title": "Junior Software Engineer",
        "company": "NextGen Systems",
        "location": "Hyderabad, Telangana",
        "description": "Entry-level Software Engineer requiring Java, Python, SQL, data structures, algorithms and Git.",
        "apply_url": "https://www.glassdoor.co.in/",
        "salary_range": "₹5L - ₹9L",
        "posted_date": "2026-10-07",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-005",
        "job_title": "Python Developer",
        "company": "CodeCraft Labs",
        "location": "Hyderabad, Telangana",
        "description": "Python Developer requiring Python, Django, Flask, REST APIs, SQL and Git.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹6L - ₹13L",
        "posted_date": "2026-10-07",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-006",
        "job_title": "Java Developer",
        "company": "EnterpriseSoft",
        "location": "Hyderabad, Telangana",
        "description": "Java Developer requiring Java, Spring Boot, SQL, REST APIs, Microservices and Git.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹7L - ₹15L",
        "posted_date": "2026-10-06",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-007",
        "job_title": "Data Analyst",
        "company": "DataSphere Analytics",
        "location": "Hyderabad, Telangana",
        "description": "Data Analyst requiring Python, SQL, Excel, Power BI, statistics and data visualization.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹5L - ₹10L",
        "posted_date": "2026-10-06",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-008",
        "job_title": "Full Stack Developer",
        "company": "InnovateLabs",
        "location": "Bengaluru, Karnataka",
        "description": "Full Stack Developer with React, JavaScript, HTML, CSS, Node.js, SQL and REST APIs.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹8L - ₹16L",
        "posted_date": "2026-10-07",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-009",
        "job_title": "Software Engineer",
        "company": "Bengaluru TechWorks",
        "location": "Bengaluru, Karnataka",
        "description": "Software Engineer requiring Java, Python, Spring Boot, React, SQL and cloud fundamentals.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹8L - ₹17L",
        "posted_date": "2026-10-06",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-010",
        "job_title": "Backend Developer",
        "company": "Chennai Cloud Systems",
        "location": "Chennai, Tamil Nadu",
        "description": "Backend Developer requiring Java, Spring Boot, PostgreSQL, REST APIs and Docker.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹6L - ₹13L",
        "posted_date": "2026-10-06",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-011",
        "job_title": "Frontend Developer",
        "company": "Chennai Digital Labs",
        "location": "Chennai, Tamil Nadu",
        "description": "Frontend Developer requiring React, JavaScript, TypeScript, HTML, CSS and Git.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹5L - ₹11L",
        "posted_date": "2026-10-05",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-012",
        "job_title": "Software Engineer",
        "company": "Pune Software Systems",
        "location": "Pune, Maharashtra",
        "description": "Software Engineer requiring Java, Python, SQL, REST APIs, Git and problem solving.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹7L - ₹14L",
        "posted_date": "2026-10-05",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-013",
        "job_title": "Data Analyst",
        "company": "Pune Analytics Hub",
        "location": "Pune, Maharashtra",
        "description": "Data Analyst requiring SQL, Python, Excel, Power BI, statistics and data analysis.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹5L - ₹11L",
        "posted_date": "2026-10-05",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-014",
        "job_title": "Full Stack Developer",
        "company": "Mumbai Web Technologies",
        "location": "Mumbai, Maharashtra",
        "description": "Full Stack Developer requiring React, Node.js, JavaScript, SQL, HTML, CSS and REST APIs.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹8L - ₹18L",
        "posted_date": "2026-10-04",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-015",
        "job_title": "Java Developer",
        "company": "Mumbai Enterprise Solutions",
        "location": "Mumbai, Maharashtra",
        "description": "Java Developer requiring Java, Spring Boot, Microservices, SQL, REST APIs and Git.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹7L - ₹16L",
        "posted_date": "2026-10-04",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-016",
        "job_title": "Software Engineer",
        "company": "Delhi Technology Group",
        "location": "New Delhi, Delhi",
        "description": "Software Engineer requiring Python, Java, SQL, APIs, Git and data structures.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹6L - ₹13L",
        "posted_date": "2026-10-03",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-017",
        "job_title": "Python Developer",
        "company": "Delhi AI Systems",
        "location": "New Delhi, Delhi",
        "description": "Python Developer requiring Python, FastAPI, machine learning basics, SQL and REST APIs.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹7L - ₹15L",
        "posted_date": "2026-10-03",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-018",
        "job_title": "Remote Software Developer",
        "company": "DigitalWorks",
        "location": "Remote",
        "description": "Remote Software Developer requiring Python, JavaScript, React, APIs, SQL and Git.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹7L - ₹15L",
        "posted_date": "2026-10-03",
        "employer_logo": None,
        "is_remote": True,
    },
    {
        "job_id": "job-019",
        "job_title": "Remote Backend Developer",
        "company": "RemoteTech Solutions",
        "location": "Remote",
        "description": "Remote Backend Developer requiring Python, FastAPI, PostgreSQL, Docker, APIs and Git.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹8L - ₹16L",
        "posted_date": "2026-10-02",
        "employer_logo": None,
        "is_remote": True,
    },
    {
        "job_id": "job-020",
        "job_title": "Remote Full Stack Developer",
        "company": "GlobalCode Labs",
        "location": "Remote",
        "description": "Remote Full Stack Developer requiring React, Node.js, JavaScript, SQL, APIs and Git.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹9L - ₹18L",
        "posted_date": "2026-10-02",
        "employer_logo": None,
        "is_remote": True,
    },
    {
        "job_id": "job-021",
        "job_title": "DevOps Engineer",
        "company": "CloudOps India",
        "location": "Hyderabad, Telangana",
        "description": "DevOps Engineer requiring Docker, Kubernetes, Linux, Git, CI/CD and cloud fundamentals.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹8L - ₹17L",
        "posted_date": "2026-10-01",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-022",
        "job_title": "Machine Learning Engineer",
        "company": "AIWorks Technologies",
        "location": "Bengaluru, Karnataka",
        "description": "Machine Learning Engineer requiring Python, machine learning, NumPy, Pandas, SQL and APIs.",
        "apply_url": "https://www.naukri.com/",
        "salary_range": "₹9L - ₹20L",
        "posted_date": "2026-10-01",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-023",
        "job_title": "QA Engineer",
        "company": "QualityFirst Systems",
        "location": "Hyderabad, Telangana",
        "description": "QA Engineer requiring manual testing, automation testing, Selenium, SQL, APIs and Git.",
        "apply_url": "https://www.indeed.com/",
        "salary_range": "₹5L - ₹10L",
        "posted_date": "2026-09-30",
        "employer_logo": None,
        "is_remote": False,
    },
    {
        "job_id": "job-024",
        "job_title": "Cloud Engineer",
        "company": "CloudSphere Technologies",
        "location": "Pune, Maharashtra",
        "description": "Cloud Engineer requiring AWS, Linux, Docker, Kubernetes, networking and cloud infrastructure.",
        "apply_url": "https://www.linkedin.com/jobs/",
        "salary_range": "₹8L - ₹18L",
        "posted_date": "2026-09-30",
        "employer_logo": None,
        "is_remote": False,
    },
]


@router.get("/search", response_model=list[JobListingOut])
async def search_jobs(
    query: str = Query(..., min_length=2),
    location: str = Query(default=""),
    remote_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    current_user: User = Depends(get_current_user),
):
    query_lower = query.lower().strip()
    location_lower = location.lower().strip()

    results = []

    for job in DEMO_JOBS:
        searchable_text = (
            f"{job['job_title']} "
            f"{job['company']} "
            f"{job['description']}"
        ).lower()

        if query_lower not in searchable_text:
            continue

        if location_lower:
            job_location = job["location"].lower()

            if location_lower not in job_location and not (
                job["is_remote"] and location_lower == "remote"
            ):
                continue

        if remote_only and not job["is_remote"]:
            continue

        results.append(JobListingOut(**job))

    start = (page - 1) * 10
    end = start + 10

    return results[start:end]


@router.post("/match-score", response_model=MatchScoreOut)
async def get_match_score(
    body: MatchScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = await db.get(ResumeAnalysis, body.resume_analysis_id)

    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume analysis not found")

    resume_skills: set[str] = set()

    if resume.ats_score_breakdown and isinstance(resume.ats_score_breakdown, dict):
        for skill in resume.ats_score_breakdown.get("skills_found", []):
            resume_skills.add(skill.lower())

    raw_lower = (resume.raw_text or "").lower()
    jd_lower = body.job_description.lower()

    matching = []
    missing = []

    for skill in resume_skills:
        if skill in jd_lower:
            matching.append(skill)

    from ..resume.skill_extractor import extract_skills

    jd_skills = extract_skills(body.job_description)

    for skill in jd_skills:
        sl = skill.lower()

        if sl in raw_lower or sl in resume_skills:
            if sl not in [m.lower() for m in matching]:
                matching.append(skill)
        else:
            missing.append(skill)

    total = len(matching) + len(missing)

    if total == 0:
        score = 50
    else:
        score = int((len(matching) / total) * 100)

    if resume.ats_score:
        score = int(score * 0.6 + resume.ats_score * 0.4)

    score = max(0, min(100, score))

    return MatchScoreOut(
        match_score=score,
        matching_skills=matching[:20],
        missing_skills=missing[:20],
    )


@router.post("/generate-cover-letter", response_model=CoverLetterOut)
async def generate_cover_letter(
    body: CoverLetterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = await db.get(ResumeAnalysis, body.resume_analysis_id)

    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume analysis not found")

    resume_text = (resume.raw_text or "")[:4000]

    system_prompt = (
        "You are an expert career coach. Write a professional, compelling cover letter. "
        "Be concise (250-350 words). Use a warm but professional tone. "
        "Highlight relevant experience from the resume that matches the job. "
        "Do NOT make up experience — only reference what's in the resume. "
        "Return ONLY the cover letter text, no JSON wrapping, no subject line."
    )

    user_prompt = (
        f"Write a cover letter for this position:\n\n"
        f"Job Title: {body.job_title}\n"
        f"Company: {body.company}\n"
        f"Job Description:\n{body.job_description[:2000]}\n\n"
        f"Candidate's Resume:\n{resume_text}\n\n"
        f"Candidate Name: {current_user.name}"
    )

    letter = await call_ai(system_prompt, user_prompt, max_tokens=1500)

    return CoverLetterOut(cover_letter=letter.strip())


@router.post("/apply", response_model=JobApplicationOut, status_code=201)
async def save_application(
    body: ApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = JobApplication(
        user_id=current_user.id,
        resume_analysis_id=body.resume_analysis_id,
        job_id=body.job_id,
        job_title=body.job_title,
        company=body.company,
        location=body.location,
        apply_url=body.apply_url,
        job_description=body.job_description[:5000],
        salary_range=body.salary_range,
        employer_logo=body.employer_logo,
        match_score=body.match_score,
        cover_letter=body.cover_letter,
        status="applied",
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return application


@router.get("/applications", response_model=list[JobApplicationOut])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobApplication)
        .where(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.applied_at.desc())
    )

    return result.scalars().all()


@router.patch(
    "/applications/{application_id}",
    response_model=JobApplicationOut
)
async def update_application_status(
    application_id: str,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid = {"applied", "interviewing", "offer", "rejected"}

    if body.status not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(valid)}"
        )

    app = await db.get(JobApplication, application_id)

    if not app or app.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    app.status = body.status

    await db.commit()
    await db.refresh(app)

    return app


@router.delete(
    "/applications/{application_id}",
    status_code=204
)
async def delete_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = await db.get(JobApplication, application_id)

    if not app or app.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    await db.delete(app)
    await db.commit()