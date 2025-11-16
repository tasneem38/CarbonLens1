from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.session import engine
from backend.db import models

# ⭐ ADD THESE TWO IMPORTS
from backend.api import routes_leaderboard
from backend.api import routes_footprint

app = FastAPI(title="CarbonLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⭐ REGISTER BOTH ROUTERS (NO PREFIX)
app.include_router(routes_footprint.router)
app.include_router(routes_leaderboard.router)

@app.on_event("startup")
def on_startup():
    try:
        models.Base.metadata.create_all(bind=engine)
    except:
        pass
