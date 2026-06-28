"""
routers/tasks.py — Subtask Management
PATCH /api/tasks/{id}/done  → mark task done
GET  /api/tasks/{commitment_id}/recovery-plan → LLM recovery plan for high-risk
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.commitment import Commitment
from app.models.user import User
from app.routers.deps import get_current_user
from app.services.llm_service import LLMService
from app.services.google_calendar import create_calendar_event
from app.schemas.task import TaskOut, TaskCreate
from pydantic import BaseModel
from typing import Optional
from datetime import date as date_type, time as time_type

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None
    priority: Optional[str] = None
    channel_id: Optional[int] = None
    planned_date: Optional[date_type] = None
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.patch("/{task_id}/done")
def mark_task_done(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_done = True
    db.commit()
    return {"message": "Task completed"}

@router.get("", response_model=list[TaskOut])
def get_tasks(planned_date: Optional[date_type] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Task).filter(Task.user_id == user.id)
    if planned_date:
        query = query.filter(Task.planned_date == planned_date)
    return query.all()

@router.post("", response_model=TaskOut)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = Task(
        user_id=user.id,
        title=data.title,
        planned_date=data.planned_date,
        priority=data.priority or "none",
        channel_id=data.channel_id,
        commitment_id=None # Standalone task
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    if user.google_access_token:
        event_id = create_calendar_event(user, task)
        if event_id:
            task.google_event_id = event_id
            db.commit()
            db.refresh(task)
            
    return task

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if data.title is not None: task.title = data.title
    if data.description is not None: task.description = data.description
    if data.is_done is not None: task.is_done = data.is_done
    if data.priority is not None: task.priority = data.priority
    if data.channel_id is not None: task.channel_id = data.channel_id
    if data.planned_date is not None: task.planned_date = data.planned_date
    if data.start_time is not None: task.start_time = data.start_time
    if data.end_time is not None: task.end_time = data.end_time

    db.commit()
    db.refresh(task)
    return task

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
