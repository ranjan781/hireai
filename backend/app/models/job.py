from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hr_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    job_type = Column(String, default="full-time")  # full-time, part-time, remote
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    required_skills = Column(ARRAY(String), default=[])   # ["Python", "FastAPI", ...]
    preferred_skills = Column(ARRAY(String), default=[])
    min_experience_years = Column(String, default="0")
    salary_range = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hr_user = relationship("User", back_populates="job_descriptions")
    applications = relationship("Application", back_populates="job")