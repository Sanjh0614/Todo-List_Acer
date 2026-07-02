"""
routers/reminders.py — Reminders
GET /api/reminders             → all reminders for user (most recent first)
POST /api/reminders/{id}/action → record user action (pay_now, later, already_done, dismiss)
"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.reminder import Reminder
from app.routers.deps import get_current_user

router = APIRouter(prefix="/api/reminders", tags=["reminders"])

from app.models.task import Task

@router.get("")
def list_reminders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reminders = db.query(Reminder).filter(Reminder.user_id == user.id).order_by(Reminder.sent_at.desc()).limit(50).all()
    results = [{
        "id": f"rem_{r.id}", "commitment_id": r.commitment_id, "style": r.style,
        "message": r.message, "sent_at": r.sent_at, "scheduled_for": None, 
        "user_action": r.user_action, "sort_time": r.sent_at
    } for r in reminders]

    # Dynamically inject upcoming AI task reminders
    tasks = db.query(Task).filter(Task.user_id == user.id, Task.reminder_hours_before != None, Task.is_done == False).all()
    for t in tasks:
        if t.planned_date and t.start_time:
            from datetime import datetime, timedelta
            start_dt = datetime.combine(t.planned_date, t.start_time)
            scheduled_for = start_dt - timedelta(hours=t.reminder_hours_before)
            
            results.append({
                "id": f"task_{t.id}",
                "commitment_id": t.commitment_id,
                "style": "task",
                "message": f"AI Pre-Start Reminder: '{t.title}'",
                "sent_at": None,
                "scheduled_for": scheduled_for,
                "user_action": None,
                "sort_time": scheduled_for
            })

    def _get_sort_time(x):
        dt = x["sort_time"]
        if not dt: return datetime.min
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    results.sort(key=_get_sort_time, reverse=True)
    for r in results:
        del r["sort_time"]
        
    return results[:50]

@router.post("/{reminder_id}/action")
def record_action(reminder_id: int, action: str = Body(embed=True), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == user.id).first()
    if not r:
        return {"message": "Not found"}
    r.user_action = action
    r.action_time = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Action recorded"}
