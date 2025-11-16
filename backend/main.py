from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.session import engine
from backend.db import models

from backend.api import routes_footprint

from backend.api import routes_reco 
app = FastAPI(title="CarbonLens API")

app.include_router(routes_footprint.router)

app.include_router(routes_reco.router) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        models.Base.metadata.create_all(bind=engine)
    except:
        pass
