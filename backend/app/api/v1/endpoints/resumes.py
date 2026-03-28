from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pathlib import Path
import shutil, os
from app.core.database import get_db
from app.core.deps import get_current_user, require_applicant
from app.core.config import settings
from app.models.user import User
from app.models.resume import Resume
from pydantic import BaseModel
from datetime import datetime
from app.ml.parsers.resume_parser import resume_parser

router = APIRouter(prefix="/resumes", tags=["Resumes"])

class ResumeOut(BaseModel):
    id: UUID
    file_name: str
    extracted_skills: List[str]
    extracted_experience_years: float
    is_parsed: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    applicant: User = Depends(require_applicant)
):
    # File type check
    allowed = [".pdf", ".docx", ".doc"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files allowed")

    # File size check
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

    # Save file
    upload_dir = Path(settings.UPLOAD_DIR) / str(applicant.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    with open(file_path, "wb") as f:
        f.write(content)

    # DB mein save karo
    resume = Resume(
        applicant_id=applicant.id,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        is_parsed="pending"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    try:
        resume.is_parsed = "processing"
        db.commit()

        parsed = resume_parser.parse(str(file_path))

        resume.raw_text = parsed.get("raw_text", "")
        resume.extracted_skills = parsed.get("extracted_skills", [])
        resume.extracted_experience_years = parsed.get("extracted_experience_years", 0.0)
        resume.extracted_education = parsed.get("extracted_education", [])
        resume.contact_info = parsed.get("contact_info", {})
        resume.is_parsed = "done"
        db.commit()
        db.refresh(resume)
    except Exception as e:
        resume.is_parsed = "failed"
        db.commit()
        print(f"Resume parsing error: {e}")


    # TODO Phase 3: ML parsing yahan trigger hoga
    # parse_resume_task.delay(str(resume.id))

    return resume

@router.get("/my", response_model=List[ResumeOut])
def my_resumes(db: Session = Depends(get_db), applicant: User = Depends(require_applicant)):
    return db.query(Resume).filter(Resume.applicant_id == applicant.id).all()

@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume