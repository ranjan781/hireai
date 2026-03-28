from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.notification_service import (
    get_user_notifications, get_unread_count,
    mark_all_read, mark_one_read
)
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationOut(BaseModel):
    id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_notifications(db, str(current_user.id))

@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = get_unread_count(db, str(current_user.id))
    return {"count": count}

@router.patch("/read-all")
def read_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mark_all_read(db, str(current_user.id))
    return {"message": "All marked as read"}

@router.patch("/{notif_id}/read")
def read_one(
    notif_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mark_one_read(db, str(notif_id), str(current_user.id))
    return {"message": "Marked as read"}