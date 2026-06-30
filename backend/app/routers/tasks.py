"""
routers/tasks.py — Task CRUD API

All endpoints require JWT authentication.
Real-time sync: Supabase Realtime broadcasts task INSERT/UPDATE/DELETE events
automatically since we write through SQLAlchemy to Supabase PostgreSQL.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models.task import Task
from app.models.commitment import Commitment
from app.models.user import User
from app.routers.deps import get_current_user
from app.services.llm_service import LLMService
from app.services.google_calendar import create_calendar_event, update_calendar_event, delete_calendar_event
from app.schemas.task import TaskOut, TaskCreate, TaskUpdate
from typing import Optional
from datetime import date as date_type

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ── Backlog Tasks (Dynamic AI Recommended) ───────────────────────────────────
@router.get("/backlog")
async def get_backlog_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Fetches all overdue tasks and concurrently uses the LangGraph backlog agent 
    to generate customized AI recommendations for each without feeding raw JSON to the LLM.
    """
    import asyncio
    from app.ai.graph.backlog_graph import generate_backlog_recommendation_graph
    
    today = date_type.today()
    overdue_tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.is_done == False,
        Task.planned_date < today
    ).order_by(Task.planned_date.desc()).all()
    
    if not overdue_tasks:
        return []

    # Prepare async execution for LangGraph tool calls
    async def fetch_recommendation(task):
        rec = await generate_backlog_recommendation_graph(task.id)
        # Convert SQLAlchemy object to dictionary safely
        task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
        task_dict["ai_recommendation"] = rec
        return task_dict

    # Execute all LangGraph workflows concurrently
    results = await asyncio.gather(*(fetch_recommendation(t) for t in overdue_tasks))
    return list(results)

# ── List Tasks ─────────────────────────────────────────────────────────────────
@router.get("", response_model=list[TaskOut])
def get_tasks(
    planned_date: Optional[date_type] = Query(None),
    weekly_plan_id: Optional[int] = Query(None),
    daily_plan_id: Optional[int] = Query(None),
    commitment_id: Optional[int] = Query(None),
    channel_id: Optional[int] = Query(None),
    is_done: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Flexible task query with optional filters.
    All filters are ANDed together.
    """
    query = db.query(Task).filter(Task.user_id == user.id)
    if planned_date:
        query = query.filter(Task.planned_date == planned_date)
    if weekly_plan_id is not None:
        query = query.filter(Task.weekly_plan_id == weekly_plan_id)
    if daily_plan_id is not None:
        query = query.filter(Task.daily_plan_id == daily_plan_id)
    if commitment_id is not None:
        query = query.filter(Task.commitment_id == commitment_id)
    if channel_id is not None:
        query = query.filter(Task.channel_id == channel_id)
    if is_done is not None:
        query = query.filter(Task.is_done == is_done)
    return query.order_by(Task.order_index, Task.created_at).all()


# ── Create Task ────────────────────────────────────────────────────────────────
@router.post("", response_model=TaskOut)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = Task(
        user_id=user.id,
        title=data.title,
        description=data.description,
        planned_date=data.planned_date,
        due_date=data.due_date,
        priority=data.priority or "none",
        channel_id=data.channel_id,
        weekly_plan_id=data.weekly_plan_id,
        daily_plan_id=data.daily_plan_id,
        commitment_id=data.commitment_id,
        estimated_minutes=data.estimated_minutes,
        start_time=data.start_time,
        end_time=data.end_time,
        reminder_hours_before=data.reminder_hours_before,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Sync to Google Calendar if user has connected it
    if user.google_access_token:
        event_id = create_calendar_event(user, task, db=db)
        if event_id:
            task.google_event_id = event_id
            db.commit()
            db.refresh(task)

    from app.services.email_scheduler import setup_task_email_schedule
    setup_task_email_schedule(task)

    return task


# ── Update Task ────────────────────────────────────────────────────────────────
@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Apply all non-None updates
    update_fields = data.model_dump(exclude_none=True)
    for field, value in update_fields.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # Sync Google Calendar
    if user.google_access_token:
        if task.google_event_id:
            update_calendar_event(user, task, db=db)
        else:
            event_id = create_calendar_event(user, task, db=db)
            if event_id:
                task.google_event_id = event_id
                db.commit()
                db.refresh(task)

    # Re-schedule emails
    from app.services.email_scheduler import setup_task_email_schedule
    setup_task_email_schedule(task)

    return task


# ── Mark Done ──────────────────────────────────────────────────────────────────
@router.patch("/{task_id}/done", response_model=TaskOut)
def mark_task_done(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_done = True
    db.commit()
    db.refresh(task)
    return task


# ── Mark Undone ────────────────────────────────────────────────────────────────
@router.patch("/{task_id}/undone", response_model=TaskOut)
def mark_task_undone(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_done = False
    db.commit()
    db.refresh(task)
    return task


# ── Complete & Delete via Email ────────────────────────────────────────────────
@router.get("/{task_id}/complete_via_email", response_class=HTMLResponse)
def complete_task_via_email(task_id: int, db: Session = Depends(get_db)):
    from app.config import settings
    # Since this is clicked from email, we might not have a Bearer token in the GET request.
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return "<h2>Task not found or already deleted! Great job! 🎉</h2>"

    user = db.query(User).filter(User.id == task.user_id).first()
    
    if user and user.google_access_token and task.google_event_id:
        delete_calendar_event(user, task.google_event_id, db=db)

    db.delete(task)
    db.commit()
    
    return f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #000; color: #10B981;">
            <h1>🎉 Fantastic Work!</h1>
            <h2>'{task.title}' has been marked as complete.</h2>
            <br/>
            <a href="{settings.FRONTEND_URL}/dashboard" style="color: #8B5CF6; text-decoration: none;">Return to Dashboard</a>
        </body>
    </html>
    """


# ── Delete Task ────────────────────────────────────────────────────────────────
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if user.google_access_token and task.google_event_id:
        delete_calendar_event(user, task.google_event_id, db=db)

    db.delete(task)
    db.commit()
    return {"message": "Task deleted", "id": task_id}


# ── Bulk Reorder ───────────────────────────────────────────────────────────────
@router.patch("/bulk/reorder")
def bulk_reorder_tasks(
    task_orders: list[dict],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update order_index for multiple tasks at once.
    Body: [{"id": 1, "order_index": 0}, {"id": 2, "order_index": 1}, ...]
    """
    for item in task_orders:
        task = db.query(Task).filter(Task.id == item["id"], Task.user_id == user.id).first()
        if task:
            task.order_index = item["order_index"]
    db.commit()
    return {"message": f"Reordered {len(task_orders)} tasks"}


# ── Recovery Plan ──────────────────────────────────────────────────────────────
@router.get("/{commitment_id}/recovery-plan")
async def recovery_plan(commitment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.query(Commitment).filter(Commitment.id == commitment_id, Commitment.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commitment not found")
    if c.risk_score < 0.5:
        return {"plan": "Risk is low — no recovery plan needed yet."}
    llm = LLMService()
    plan = await llm.generate_recovery_plan(c)
    return {"plan": plan}


# ── Today's Task Count ─────────────────────────────────────────────────────────
@router.get("/stats/today")
def today_task_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from datetime import date
    today = date.today()
    total = db.query(func.count(Task.id)).filter(Task.user_id == user.id, Task.planned_date == today).scalar() or 0
    done = db.query(func.count(Task.id)).filter(Task.user_id == user.id, Task.planned_date == today, Task.is_done == True).scalar() or 0
    return {"total": total, "done": done, "pending": total - done}
