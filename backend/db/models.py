# backend/db/models.py
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, JSON, DateTime, func

Base = declarative_base()


# ------------------------
# Users (optional)
# ------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)


# ------------------------
# Footprint Runs
# ------------------------
class FootprintRun(Base):
    __tablename__ = "footprint_runs"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, nullable=True)
    inputs = mapped_column(JSON, nullable=True)

    total_kg = mapped_column(Float, nullable=False)
    energy_kg = mapped_column(Float, nullable=False)
    travel_kg = mapped_column(Float, nullable=False)
    food_kg = mapped_column(Float, nullable=False)
    goods_kg = mapped_column(Float, default=0)

    score = mapped_column(Float, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())


# ------------------------
# Leaderboard
# ------------------------
class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = mapped_column(Integer, primary_key=True, index=True)
    user_name = mapped_column(String, default="Anonymous")
    score = mapped_column(Float, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())
