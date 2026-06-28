from pydantic import BaseModel
from datetime import date
from typing import Optional

class DailyHighlightOut(BaseModel):
    id: int
    user_id: int
    date: date
    content: str
    class Config: from_attributes = True

class ShutdownRequest(BaseModel):
    date: Optional[date] = None
