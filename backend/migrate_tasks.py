import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "dev.db")

def migrate():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Dropping old indexes if they exist...")
        try: cursor.execute("DROP INDEX IF EXISTS ix_tasks_commitment_id")
        except: pass
        try: cursor.execute("DROP INDEX IF EXISTS ix_tasks_user_id")
        except: pass

        print("Dropping tasks_old if it exists...")
        try: cursor.execute("DROP TABLE IF EXISTS tasks_old")
        except: pass

        print("Renaming old tasks table...")
        # Since it failed previously, tasks might be tasks_old already. Let's check.
        try:
            cursor.execute("ALTER TABLE tasks RENAME TO tasks_old")
        except:
            print("Table might already be renamed.")

        
        print("Recreating new tasks table via SQLAlchemy...")
        import app.models # Trigger imports
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        print("Copying data...")
        # Note: the new table has 'priority'. We'll insert it as 'none'
        cursor.execute("""
            INSERT INTO tasks (
                id, commitment_id, user_id, title, description, 
                due_date, order_index, is_done, estimated_minutes, actual_minutes, 
                pomodoros_estimated, pomodoros_completed, channel_id, planned_date, 
                start_time, end_time, created_at, updated_at, priority
            )
            SELECT 
                id, commitment_id, user_id, title, description, 
                due_date, order_index, is_done, estimated_minutes, actual_minutes, 
                pomodoros_estimated, pomodoros_completed, channel_id, planned_date, 
                start_time, end_time, created_at, updated_at, 'none'
            FROM tasks_old
        """)
        
        print("Dropping old table...")
        cursor.execute("DROP TABLE tasks_old")
        
        conn.commit()
        print("Migration complete!")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
