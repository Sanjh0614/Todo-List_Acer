"""
models/weekly_objective.py — Weekly Objective Entity
"""
from sqlalchemy import Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class WeeklyObjective(Base):
    __tablename__ = "weekly_objectives"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    week_start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    week_end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="planned") # planned, done
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="weekly_objectives")
    channel: Mapped["Channel"] = relationship("Channel")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="weekly_objective")
