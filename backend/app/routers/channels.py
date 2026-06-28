from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.channel import Channel
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelOut, ChannelReorder

router = APIRouter(prefix="/api/channels", tags=["channels"])

@router.get("", response_model=list[ChannelOut])
def get_channels(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Channel).filter(Channel.user_id == user.id).order_by(Channel.order_index, Channel.id).all()

@router.patch("/reorder")
def reorder_channels(data: ChannelReorder, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    channels = db.query(Channel).filter(Channel.user_id == user.id, Channel.id.in_(data.channel_ids)).all()
    channel_map = {c.id: c for c in channels}
    
    for i, cid in enumerate(data.channel_ids):
        if cid in channel_map:
            channel_map[cid].order_index = i
            
    db.commit()
    return {"message": "Channels reordered"}

@router.post("", response_model=ChannelOut)
def create_channel(data: ChannelCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = Channel(user_id=user.id, name=data.name, color=data.color)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.put("/{channel_id}", response_model=ChannelOut)
def update_channel(channel_id: int, data: ChannelUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.query(Channel).filter(Channel.id == channel_id, Channel.user_id == user.id).first()
    if not c: raise HTTPException(404, "Channel not found")
    if data.name is not None: c.name = data.name
    if data.color is not None: c.color = data.color
    db.commit()
    db.refresh(c)
    return c

@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.query(Channel).filter(Channel.id == channel_id, Channel.user_id == user.id).first()
    if not c: raise HTTPException(404, "Channel not found")
    db.delete(c)
    db.commit()
    return {"message": "Channel deleted"}
