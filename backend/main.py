from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security_middleware import rate_limit_middleware, security_headers_middleware
from app.api.v1 import router
from app.models import User, UserRole, JobDescription, Resume, Application
from app.models.notification import Notification
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)

app = FastAPI(
    title="HireAI API",
    description="Smart Resume Analyzer & Hiring Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=security_headers_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary — sabko allow karo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "version": "1.0.0"
    }