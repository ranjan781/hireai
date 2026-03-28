from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.core.deps import get_current_user, require_hr
from app.models.user import User
from app.models.job import JobDescription
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_type: str = "full-time"
    description: str
    requirements: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience_years: str = "0"
    salary_range: Optional[str] = None

class JobOut(BaseModel):
    id: UUID
    title: str
    company: str
    location: Optional[str]
    job_type: str
    description: str
    requirements: Optional[str]
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: str
    salary_range: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("", response_model=JobOut, status_code=201)
def create_job(data: JobCreate, db: Session = Depends(get_db), hr: User = Depends(require_hr)):
    job = JobDescription(
        hr_user_id=hr.id,
        title=data.title,
        company=data.company,
        location=data.location,
        job_type=data.job_type,
        description=data.description,
        requirements=data.requirements,
        required_skills=data.required_skills,
        preferred_skills=data.preferred_skills,
        min_experience_years=data.min_experience_years,
        salary_range=data.salary_range
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobOut])
def list_jobs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = db.query(JobDescription).filter(
        JobDescription.is_active == True
    ).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: UUID, data: JobCreate, db: Session = Depends(get_db), hr: User = Depends(require_hr)):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.hr_user_id == hr.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not yours")
    for field, value in data.model_dump().items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}")
def delete_job(job_id: UUID, db: Session = Depends(get_db), hr: User = Depends(require_hr)):
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.hr_user_id == hr.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_active = False
    db.commit()
    return {"message": "Job deleted successfully"}