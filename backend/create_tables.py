from app.database import Base, engine
import app.models # this will trigger the __init__.py imports

print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
