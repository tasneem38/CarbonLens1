# backend/api/routes_leaderboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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
    return int(score * 12.5)


@router.get("/")
def get_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(Leaderboard)
          .order_by(Leaderboard.score.desc())
          .limit(limit)
          .all()
    )

    return [
        {
            "user_id": r.user_id,
            "name": r.user_name,
            "score": r.score,
            "tier": get_tier(r.score),
            "xp": score_to_xp(r.score),
            "created_at": r.created_at
        }
        for r in rows
    ]


@router.get("/monthly")
def get_monthly_leaderboard(db: Session = Depends(get_db)):
    one_month = datetime.utcnow() - timedelta(days=30)

    rows = (
        db.query(FootprintRun)
          .filter(FootprintRun.created_at >= one_month)
          .order_by(FootprintRun.score.desc())
          .limit(20)
          .all()
    )

    return [
        {
            "user_id": r.user_id,
            "name": f"User #{r.user_id}" if r.user_id else "Anonymous",
            "score": r.score,
            "total_kg": r.total_kg,
            "tier": get_tier(r.score),
            "xp": score_to_xp(r.score),
        }
        for r in rows
    ]


@router.get("/user/{user_id}")
def get_user_rank(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Leaderboard)
          .order_by(Leaderboard.score.desc())
          .all()
    )

    for idx, r in enumerate(rows, start=1):
        if r.user_id == user_id:
            return {
                "rank": idx,
                "score": r.score,
                "tier": get_tier(r.score),
                "xp": score_to_xp(r.score),
            }

    return {"rank": None}
