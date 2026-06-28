from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from app.schemas.task import TaskOut

class WeeklyObjectiveBase(BaseModel):
    title: str
    channel_id: Optional[int] = None
    week_start_date: date
    week_end_date: date
    status: Optional[str] = "planned"

class WeeklyObjectiveCreate(WeeklyObjectiveBase):
    pass

class WeeklyObjectiveUpdate(BaseModel):
    title: Optional[str] = None
    channel_id: Optional[int] = None
    week_start_date: Optional[date] = None
    week_end_date: Optional[date] = None
    status: Optional[str] = None

class WeeklyObjectiveOut(WeeklyObjectiveBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskOut] = []

    model_config = ConfigDict(from_attributes=True)
