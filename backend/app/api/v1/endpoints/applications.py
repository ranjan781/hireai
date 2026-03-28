from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.core.deps import get_current_user, require_hr, require_applicant
from app.models.user import User
from app.models.resume import Application, Resume
from app.models.job import JobDescription
from app.ml.matchers.jd_matcher import jd_matcher
from app.ml.gap_analyzer.analyzer import analyze_gap
from app.ml.gap_analyzer.ai_recommender import get_ai_recommendation
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["Applications"])

class ApplyRequest(BaseModel):
    job_id: UUID
    resume_id: UUID

class ApplicationOut(BaseModel):
    id: UUID
    job_id: UUID
    resume_id: UUID
    match_score: float
    strong_skills: List[str]
    weak_skills: List[str]
    missing_skills: List[str]
    ai_recommendation: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str
    hr_notes: Optional[str] = None

@router.post("/apply", response_model=ApplicationOut, status_code=201)
async def apply_for_job(
    data: ApplyRequest,
    db: Session = Depends(get_db),
    applicant: User = Depends(require_applicant)
):
    from app.services.notification_service import create_notification

    job = db.query(JobDescription).filter(JobDescription.id == data.job_id).first()
    if not job or not job.is_active:
        raise HTTPException(status_code=404, detail="Job not found or closed")

    resume = db.query(Resume).filter(
        Resume.id == data.resume_id,
        Resume.applicant_id == applicant.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    existing = db.query(Application).filter(
        Application.applicant_id == applicant.id,
        Application.job_id == data.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied for this job")

    result = jd_matcher.calculate_match(
        resume_skills=resume.extracted_skills or [],
        resume_text=resume.raw_text or "",
        required_skills=job.required_skills or [],
        preferred_skills=job.preferred_skills or [],
        jd_text=job.description or ""
    )

    gap = analyze_gap(
        result,
        resume.extracted_experience_years or 0.0,
        job.min_experience_years or "0"
    )

    ai_rec = await get_ai_recommendation(
        candidate_name=applicant.full_name,
        match_score=gap["match_score"],
        strong_skills=gap["strong_skills"],
        weak_skills=gap["weak_skills"],
        missing_skills=gap["missing_skills"],
        job_title=job.title,
        experience_years=resume.extracted_experience_years or 0.0,
        min_experience=job.min_experience_years or "0"
    )

    application = Application(
        applicant_id=applicant.id,
        job_id=data.job_id,
        resume_id=data.resume_id,
        match_score=gap["match_score"],
        strong_skills=gap["strong_skills"],
        weak_skills=gap["weak_skills"],
        missing_skills=gap["missing_skills"],
        ai_recommendation=ai_rec,
        score_breakdown=gap["score_breakdown"],
        status="applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Notifications
    create_notification(
        db=db,
        user_id=str(applicant.id),
        title="Application Submitted!",
        message=f"Your application for {job.title} has been submitted. Match Score: {gap['match_score']}%",
        notif_type="success"
    )
    create_notification(
        db=db,
        user_id=str(job.hr_user_id),
        title="New Application Received!",
        message=f"{applicant.full_name} applied for {job.title}. ML Score: {gap['match_score']}%",
        notif_type="info"
    )

    return application

@router.get("/my", response_model=List[ApplicationOut])
def my_applications(
    db: Session = Depends(get_db),
    applicant: User = Depends(require_applicant)
):
    return db.query(Application).filter(
        Application.applicant_id == applicant.id
    ).all()

@router.get("/job/{job_id}", response_model=List[ApplicationOut])
def job_applications(
    job_id: UUID,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    return db.query(Application).filter(
        Application.job_id == job_id
    ).all()

@router.patch("/{application_id}/status")
def update_status(
    application_id: UUID,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    from app.services.notification_service import create_notification

    valid = ["applied", "under_review", "shortlisted", "interview", "selected", "rejected"]
    if data.status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose: {valid}")

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status
    app.status = data.status
    if data.hr_notes:
        app.hr_notes = data.hr_notes
    db.commit()

    # Status messages
    status_msgs = {
        "shortlisted": ("You've been Shortlisted!", "Congratulations! You have been shortlisted.", "success"),
        "interview": ("Interview Scheduled!", "You have been selected for an interview. HR will contact you soon.", "success"),
        "selected": ("Offer Extended!", "Congratulations! You have been selected for the position.", "success"),
        "rejected": ("Application Update", "Thank you for applying. We have decided to move forward with other candidates.", "info"),
        "under_review": ("Application Under Review", "Your application is currently being reviewed by the HR team.", "info"),
    }

    if data.status in status_msgs:
        title, msg, notif_type = status_msgs[data.status]
        create_notification(
            db=db,
            user_id=str(app.applicant_id),
            title=title,
            message=msg,
            notif_type=notif_type
        )

    return {"message": "Status updated", "status": data.status}