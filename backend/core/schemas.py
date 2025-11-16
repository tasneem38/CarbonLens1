from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

# ----------------- Inputs -----------------
class LifestyleInput(BaseModel):
    electricityKwh: float = 0
    naturalGasTherms: float = 0
    carKm: float = 0
    busKm: float = 0
    diet: Literal["veg", "mixed", "nonveg"] = "mixed"
    foodEmissions: float = 0
    goodsEmissions: float = 0


# ----------------- Footprint Response -----------------
class FootprintTotals(BaseModel):
    total: float
    energy: float
    travel: float
    food: float
    goods: float = 0


class TrendPoint(BaseModel):
    x: str
    y: float


class FootprintResult(BaseModel):
    inputs: LifestyleInput
    totals: FootprintTotals
    score: int
    trend: List[TrendPoint]
    recommendations: List[Dict] = []


# ----------------- AI Tips -----------------
class AITip(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    impact_kg_month: Optional[float] = None
    confidence: Optional[float] = None
    category: Optional[str] = None
    steps: Optional[List[str]] = None


class TipsResponse(BaseModel):
    tips: List[Dict]  # using Dict to allow flexible AI output


# ----------------- Optional: User Models -----------------
class UserCreate(BaseModel):
    email: str


class UserOut(BaseModel):
    id: int
    email: str
