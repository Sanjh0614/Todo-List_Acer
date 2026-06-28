from pydantic import BaseModel
from typing import Optional

class ChannelCreate(BaseModel):
    name: str
    color: Optional[str] = "#10B981"

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class ChannelOut(BaseModel):
    id: int
    user_id: int
    name: str
    color: str

    class Config: from_attributes = True

class ChannelReorder(BaseModel):
    channel_ids: list[int]
