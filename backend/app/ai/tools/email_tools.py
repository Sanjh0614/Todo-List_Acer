from langchain_core.tools import tool
from pydantic import BaseModel, Field
import smtplib
from email.message import EmailMessage
from loguru import logger
from app.config import settings
from app.services.llm_service import LLMService

class GenerateEmailInput(BaseModel):
    task_id: int = Field(description="The ID of the task that ended.")
    task_title: str = Field(description="The title of the task.")
    user_name: str = Field(description="The name of the user.")
    user_email: str = Field(description="The email address of the user.")

@tool("generate_and_send_task_email", args_schema=GenerateEmailInput)
async def generate_and_send_task_email(task_id: int, task_title: str, user_name: str, user_email: str) -> str:
    """
    Generates an email via LLM asking the user if they completed their task, 
    and then sends the email using SMTP.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return "Failed: SMTP credentials missing in .env."

    try:
        # We need an LLM to generate the text
        llm = LLMService()
        if not llm.client:
            # Fallback if no LLM configured
            response = f"Hey {user_name}! Your time for '{task_title}' is up. Did you crush it?\n\n[Click here if you finished it: {settings.FRONTEND_URL.replace('5173', '8000')}/api/tasks/{task_id}/complete_via_email]"
        else:
            prompt = f"""
            The user '{user_name}' had scheduled a task called '{task_title}' which was supposed to end right now.
            Write a short, friendly, and highly motivating email (3-4 sentences max) asking them if they completed it.
            At the very end of the email, strictly include this exact line:
            [Click here if you finished it: http://localhost:8000/api/tasks/{task_id}/complete_via_email]
            """
            
            ai_res = await llm.client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250, temperature=0.7,
            )
            response = ai_res.choices[0].message.content.strip()

        # Send the email!
        msg = EmailMessage()
        msg.set_content(response)
        msg['Subject'] = f"Did you complete: {task_title}? 🎯 [ID:{task_id}]"
        # Format the From header to show the display name "AI Productivity"
        sender_email = settings.SMTP_FROM or settings.SMTP_USERNAME
        msg['From'] = f"AI Productivity <{sender_email}>"
        msg['To'] = user_email

        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {user_email}")
        return f"Successfully generated and sent email to {user_email}."
    
    except Exception as e:
        logger.error(f"Error inside generate_and_send_task_email tool: {e}")
        return f"Error: {e}"


@tool("generate_and_send_reminder_email", args_schema=GenerateEmailInput)
async def generate_and_send_reminder_email(task_id: int, task_title: str, user_name: str, user_email: str) -> str:
    """
    Generates a pre-start reminder email via LLM motivating the user to get ready for their task.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return "Failed: SMTP credentials missing in .env."

    try:
        llm = LLMService()
        if not llm.client:
            response = f"Hey {user_name}! Quick reminder that your task '{task_title}' is starting soon. Get ready to crush it! 🔥"
        else:
            prompt = f"""
            The user '{user_name}' has a task called '{task_title}' which is starting very soon.
            Write a short, highly motivating, hype-building email (3-4 sentences max) reminding them to get ready and focus up!
            Do not include any links. Just pure hype and motivation.
            """
            
            ai_res = await llm.client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250, temperature=0.8,
            )
            response = ai_res.choices[0].message.content.strip()

        msg = EmailMessage()
        msg.set_content(response)
        msg['Subject'] = f"Reminder: {task_title} starting soon! 🚀"
        sender_email = settings.SMTP_FROM or settings.SMTP_USERNAME
        msg['From'] = f"AI Productivity <{sender_email}>"
        msg['To'] = user_email

        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Reminder email sent successfully to {user_email}")
        return f"Successfully generated and sent reminder to {user_email}."
    
    except Exception as e:
        logger.error(f"Error inside generate_and_send_reminder_email tool: {e}")
        return f"Error: {e}"

