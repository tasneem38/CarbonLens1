# backend/api/routes_leaderboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from backend.db.session import get_db
from backend.db.models import Leaderboard, FootprintRun

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

def get_tier(score: float):
    if score >= 90: return "Diamond"
    if score >= 75: return "Platinum"
    if score >= 60: return "Gold"
    if score >= 45: return "Silver"
    return "Bronze"

def score_to_xp(score: float):
    # scale to XP; tweak as you like
    return int(score * 12.5)

@router.get("/", summary="All-time leaderboard")
def get_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.query(Leaderboard).order_by(Leaderboard.score.desc()).limit(limit).all()
    return [
        {
            "name": entry.user_name,
            "score": round(entry.score, 2),
            "created_at": entry.created_at,
            "tier": get_tier(entry.score),
            "xp": score_to_xp(entry.score)
        }
        for entry in rows
    ]

@router.get("/monthly", summary="Leaderboard entries in the last 30 days")
def get_monthly_leaderboard(limit: int = 20, days: int = 30, db: Session = Depends(get_db)):
    one_month_ago = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(FootprintRun)
        .filter(FootprintRun.created_at >= one_month_ago)
        .order_by(FootprintRun.score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "name": f"User #{r.user_id or 'anon'}",
            "score": r.score,
            "total_kg": r.total_kg,
            "created_at": r.created_at,
            "tier": get_tier(r.score),
            "xp": score_to_xp(r.score)
        }
        for r in rows
    ]

@router.get("/user/{user_id}", summary="Get user's rank, score, tier and xp")
def get_user_rank(user_id: int, db: Session = Depends(get_db)):
    # Query ordered leaderboard to compute rank (for small datasets okay)
    rows = db.query(Leaderboard).order_by(Leaderboard.score.desc()).all()
    for idx, r in enumerate(rows, start=1):
        # we assume Leaderboard may store a user_id field in future; using user_name fallback
        # adapt if you add user_id to Leaderboard model
        if hasattr(r, "user_id") and r.user_id == user_id:
            return {"rank": idx, "score": r.score, "tier": get_tier(r.score), "xp": score_to_xp(r.score)}
        # allow matching by name "User #<id>"
        if r.user_name and r.user_name.lower() == f"user #{user_id}":
            return {"rank": idx, "score": r.score, "tier": get_tier(r.score), "xp": score_to_xp(r.score)}
    raise HTTPException(status_code=404, detail="User not found in leaderboard")
