# backend/create_db.py
from backend.db.session import engine
from backend.db import models

def create_all():
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

if __name__ == "__main__":
    create_all()
