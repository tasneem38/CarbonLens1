# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend.api import routes_leaderboard
from backend.api import routes_footprint     # ✅ ADD THIS LINE

from backend.db.session import engine
from backend.db import models


app = FastAPI(title="CarbonLens API")

# Allow frontend in dev
origins = [
    "http://localhost",
    "http://localhost:8501",
    "http://127.0.0.1",
    "http://127.0.0.1:8501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_footprint.router)   # ✅ MUST be first so Analyzer works
app.include_router(routes_leaderboard.router) # leaderboard


@app.on_event("startup")
def on_startup():
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init error:", e)
