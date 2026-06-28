from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as date_type, datetime
from app.database import get_db
from app.models.daily_highlight import DailyHighlight
from app.models.task import Task
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.ritual import DailyHighlightOut, ShutdownRequest
from app.services.hybrid_client import HybridClient

router = APIRouter(prefix="/api/rituals", tags=["rituals"])

@router.post("/shutdown", response_model=DailyHighlightOut)
async def generate_shutdown_highlight(data: ShutdownRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target_date = data.date or date_type.today()
    
    # 1. Fetch completed tasks for the target date
    tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.planned_date == target_date,
        Task.is_done == True
    ).all()
    
    task_titles = [t.title for t in tasks]
    prompt_text = f"Generate a short, journal-style daily highlight based on these completed tasks: {', '.join(task_titles) if task_titles else 'None'}. Make it encouraging and reflective."

    # 2. Use AI layer
    client = HybridClient()
    ai_content = client.generate(prompt=prompt_text, system_instr="You are a helpful productivity coach generating an end of day summary.", temperature=0.7)
    
    # 3. Save Highlight
    hl = db.query(DailyHighlight).filter(DailyHighlight.user_id == user.id, DailyHighlight.date == target_date).first()
    if not hl:
        hl = DailyHighlight(user_id=user.id, date=target_date, content=ai_content)
        db.add(hl)
    else:
        hl.content = ai_content
    
    db.commit()
    db.refresh(hl)
    return hl

@router.get("/highlights", response_model=list[DailyHighlightOut])
def get_highlights(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(DailyHighlight).filter(DailyHighlight.user_id == user.id).order_by(DailyHighlight.date.desc()).all()
