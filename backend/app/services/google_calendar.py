from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.config import settings
from datetime import datetime, timedelta
import os

# Allow HTTP for local development OAuth flows
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def get_google_flow(state=None):
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": "ai-productivity",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state
    )
    return flow

def get_calendar_service(user):
    if not user.google_access_token or not user.google_refresh_token:
        return None
        
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(user, task):
    service = get_calendar_service(user)
    if not service: return None
    
    if not task.planned_date:
        return None
        
    date_str = task.planned_date.isoformat()
    end_date = task.planned_date + timedelta(days=1)
    end_date_str = end_date.isoformat()
    
    event = {
        'summary': task.title,
        'description': task.description or '',
        'start': {
            'date': date_str,
        },
        'end': {
            'date': end_date_str, 
        }
    }
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('id')
    except Exception as e:
        print(f"Failed to create Google Calendar event: {e}")
        return None

def update_calendar_event(user, task):
    if not task.google_event_id:
        return create_calendar_event(user, task)

    service = get_calendar_service(user)
    if not service: return None
    
    if not task.planned_date:
        return None
        
    date_str = task.planned_date.isoformat()
    end_date = task.planned_date + timedelta(days=1)
    end_date_str = end_date.isoformat()
    
    event = {
        'summary': task.title,
        'description': task.description or '',
        'start': {
            'date': date_str,
        },
        'end': {
            'date': end_date_str, 
        }
    }
    
    try:
        updated_event = service.events().update(calendarId='primary', eventId=task.google_event_id, body=event).execute()
        return updated_event.get('id')
    except Exception as e:
        print(f"Failed to update Google Calendar event: {e}")
        return task.google_event_id

def delete_calendar_event(user, event_id):
    service = get_calendar_service(user)
    if not service or not event_id: return
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        print(f"Failed to delete event: {e}")

def get_calendar_events(user, time_min: str, time_max: str):
    service = get_calendar_service(user)
    if not service: return []
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        print(f"Failed to fetch events: {e}")
        return []
