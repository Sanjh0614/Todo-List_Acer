import asyncio
from datetime import datetime, date, timedelta
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from app.database import SessionLocal
from app.models.task import Task
from app.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.ai.tools.email_tools import generate_and_send_task_email, generate_and_send_reminder_email

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def trigger_task_email(task_id: int):
    """
    Executes exactly once for a specific task, 5 minutes after its end time.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or task.is_done:
            logger.info(f"Task {task_id} is already done or deleted. No email sent.")
            return

        user = db.query(User).filter(User.id == task.user_id).first()
        if not user or not user.email:
            return
            
        logger.info(f"Task {task.id} ended 5 minutes ago for user {user.email}. Generating AI email.")
        
        try:
            # Execute the LangGraph tool
            result = await generate_and_send_task_email.ainvoke({
                "task_id": task.id,
                "task_title": task.title,
                "user_name": user.name or "User",
                "user_email": user.email
            })
            logger.info(f"LangGraph Tool result: {result}")
            
            # Automatically schedule another check 2 hours from now if not responded ONLY for exact time tasks
            if task.end_time:
                next_run_time = datetime.now() + timedelta(hours=2)
                schedule_task_email(task.id, next_run_time, job_suffix="followup")
                logger.info(f"Auto-rescheduled followup email for task {task.id} at {next_run_time}")
            
        except Exception as ai_e:
            logger.error(f"Failed to generate/send AI email: {ai_e}")
            
    except Exception as e:
        logger.error(f"Error in trigger_task_email: {e}")
    finally:
        db.close()


async def trigger_reminder_email(task_id: int):
    """
    Executes exactly once for a specific task, X hours before its start time.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or task.is_done:
            logger.info(f"Task {task_id} is already done or deleted. No pre-start reminder sent.")
            return

        user = db.query(User).filter(User.id == task.user_id).first()
        if not user or not user.email:
            return
            
        logger.info(f"Task {task.id} is starting soon for user {user.email}. Generating AI reminder email.")
        
        try:
            result = await generate_and_send_reminder_email.ainvoke({
                "task_id": task.id,
                "task_title": task.title,
                "user_name": user.name or "User",
                "user_email": user.email
            })
            logger.info(f"Reminder LangGraph Tool result: {result}")
        except Exception as ai_e:
            logger.error(f"Failed to generate/send AI reminder email: {ai_e}")
            
    except Exception as e:
        logger.error(f"Error in trigger_reminder_email: {e}")
    finally:
        db.close()


def schedule_task_email(task_id: int, run_time: datetime, job_suffix: str = "exact", is_reminder: bool = False):
    """
    Schedules an email to be sent at the exact run_time.
    """
    if not scheduler.running:
        logger.warning("Scheduler is not running!")
        return

    job_id = f"email_task_{task_id}_{job_suffix}"
    
    # Remove existing job if user rescheduled the task
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
        
    scheduler.add_job(
        trigger_reminder_email if is_reminder else trigger_task_email,
        trigger=DateTrigger(run_date=run_time),
        args=[task_id],
        id=job_id
    )
    logger.info(f"Scheduled AI email for task {task_id} ({job_suffix}) at {run_time}")


def setup_task_email_schedule(task):
    """
    Analyzes task properties and schedules one or more precise emails.
    """
    if task.is_done or not task.planned_date:
        return

    from datetime import time
    
    if task.end_time:
        # Schedule precisely 5 minutes after end_time
        run_time = datetime.combine(task.planned_date, task.end_time) + timedelta(minutes=5)
        if run_time > datetime.now():
            schedule_task_email(task.id, run_time, job_suffix="exact")
    else:
        # User didn't specify time, schedule at 8 AM, 2 PM, 7 PM
        for hour in (8, 14, 19):
            run_time = datetime.combine(task.planned_date, time(hour=hour, minute=0))
            if run_time > datetime.now():
                schedule_task_email(task.id, run_time, job_suffix=f"fixed_{hour}")

    if task.start_time and task.reminder_hours_before:
        # Schedule reminder X hours before start_time
        start_datetime = datetime.combine(task.planned_date, task.start_time)
        reminder_run_time = start_datetime - timedelta(hours=task.reminder_hours_before)
        if reminder_run_time > datetime.now():
            schedule_task_email(task.id, reminder_run_time, job_suffix="reminder", is_reminder=True)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.success("✅ Exact-Time Event Scheduler started (Continuous polling is OFF)")
    return scheduler
