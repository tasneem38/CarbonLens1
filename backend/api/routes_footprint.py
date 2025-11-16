from fastapi import APIRouter, Depends   # ✅ Must be first before using router
from sqlalchemy.orm import Session

from backend.core.schemas import LifestyleInput, FootprintResult, FootprintTotals, TrendPoint
from backend.db.session import get_db
from backend.db import models
from backend.services.calculator import compute_footprint as compute_totals
from backend.services.scoring import green_score as score_from_total
from backend.services.forecasting import naive_forecast_series as forecast_series
from backend.db.models import Leaderboard
import random

# ✅ You must define the router right after import
router = APIRouter(prefix="/footprint", tags=["Footprint"])


@router.post("/compute", response_model=FootprintResult)
def compute_footprint(payload: LifestyleInput, db: Session = Depends(get_db)):
    totals = compute_totals(payload.model_dump())
    score = score_from_total(totals["total"])
    trend = forecast_series(totals["total"])

# backend/api/routes_footprint.py

    run = models.FootprintRun(
        user_id=None,
        inputs=payload.model_dump(),
        total_kg=totals["total"],
        energy_kg=totals["energy"],
        travel_kg=totals["travel"],
        food_kg=totals["food"],
        goods_kg=totals.get("goods", 0),   # ← FIXED
        score=score
    )
    db.add(run)

    # Leaderboard entry
    anon_id = random.randint(1000, 9999)
    entry = Leaderboard(
        user_id=None,                     # ← FIXED
        user_name=f"Anonymous #{anon_id}",
        score=score
    )
    db.add(entry)

    db.commit()
