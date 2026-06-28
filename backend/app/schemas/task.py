from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional

class TaskOut(BaseModel):
    id: int
    commitment_id: Optional[int] = None
    title: str
    description: Optional[str]
    order_index: int
    is_done: bool
    estimated_minutes: int
    actual_minutes: int
    pomodoros_estimated: int
    pomodoros_completed: int
    priority: str
    channel_id: Optional[int] = None
    planned_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    class Config: from_attributes = True

class TaskCreate(BaseModel):
    title: str
    planned_date: Optional[date] = None
    priority: Optional[str] = "none"
    channel_id: Optional[int] = None
