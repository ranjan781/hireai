from fastapi import APIRouter
from app.api.v1.endpoints import auth, jobs, resumes, applications, notifications

router = APIRouter()
router.include_router(auth.router)
router.include_router(jobs.router)
router.include_router(resumes.router)
router.include_router(applications.router)
router.include_router(notifications.router)