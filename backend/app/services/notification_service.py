from sqlalchemy.orm import Session
from app.models.notification import Notification
import uuid

def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notif_type: str = "info"
) -> Notification:
    notif = Notification(
        user_id=uuid.UUID(str(user_id)),
        title=title,
        message=message,
        type=notif_type
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

def get_user_notifications(db: Session, user_id: str, limit: int = 20):
    return db.query(Notification).filter(
        Notification.user_id == uuid.UUID(str(user_id))
    ).order_by(Notification.created_at.desc()).limit(limit).all()

def get_unread_count(db: Session, user_id: str) -> int:
    return db.query(Notification).filter(
        Notification.user_id == uuid.UUID(str(user_id)),
        Notification.is_read == False
    ).count()

def mark_all_read(db: Session, user_id: str):
    db.query(Notification).filter(
        Notification.user_id == uuid.UUID(str(user_id)),
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()

def mark_one_read(db: Session, notif_id: str, user_id: str):
    notif = db.query(Notification).filter(
        Notification.id == uuid.UUID(str(notif_id)),
        Notification.user_id == uuid.UUID(str(user_id))
    ).first()
    if notif:
        notif.is_read = True
        db.commit()