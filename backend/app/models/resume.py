from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)

    # ML se extract hoga — parsed data
    raw_text = Column(Text)
    extracted_skills = Column(ARRAY(String), default=[])
    extracted_experience_years = Column(Float, default=0.0)
    extracted_education = Column(JSONB, default=[])
    extracted_designations = Column(ARRAY(String), default=[])
    contact_info = Column(JSONB, default={})

    is_parsed = Column(String, default="pending")  # pending, processing, done, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applicant = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)

    # ML score
    match_score = Column(Float, default=0.0)         # 0-100
    strong_skills = Column(ARRAY(String), default=[])
    weak_skills = Column(ARRAY(String), default=[])
    missing_skills = Column(ARRAY(String), default=[])
    ai_recommendation = Column(Text)
    score_breakdown = Column(JSONB, default={})

    status = Column(String, default="applied")
    # applied → under_review → shortlisted → interview → selected / rejected

    hr_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    applicant = relationship("User", back_populates="applications")
    job = relationship("JobDescription", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")