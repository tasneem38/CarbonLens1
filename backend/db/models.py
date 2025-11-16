from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, ForeignKey, JSON, DateTime, func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True)
    name = mapped_column(String)

class FootprintRun(Base):
    __tablename__ = "footprint_runs"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, nullable=True)
    inputs = mapped_column(JSON, nullable=True)
    total_kg = mapped_column(Float, nullable=False)
    energy_kg = mapped_column(Float, nullable=False)
    travel_kg = mapped_column(Float, nullable=False)
    food_kg = mapped_column(Float, nullable=False)
    score = mapped_column(Float, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())

class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_name = mapped_column(String, default="Anonymous")
    score = mapped_column(Float, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())
