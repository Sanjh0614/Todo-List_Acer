import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN reminder_hours_before INTEGER;"))
        conn.commit()
        print("Successfully added reminder_hours_before column to tasks table.")
except Exception as e:
    print(f"Error (column might already exist): {e}")
