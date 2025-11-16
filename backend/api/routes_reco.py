from fastapi import APIRouter, HTTPException
from backend.services.recommender import (
    generate_tips,
    generate_chat_response
)
from backend.core.schemas import TipsResponse

router = APIRouter(prefix="/reco", tags=["Recommendations"])

# ---------------------------------------------------
# Recommendation API
# ---------------------------------------------------
@router.post("/generate", response_model=TipsResponse)
def generate_recommendations(inputs: dict):
    try:
        tips = generate_tips(inputs)

        if not isinstance(tips, list):
            raise ValueError("AI returned non-list")

        tips = [t for t in tips if isinstance(t, dict)]

        return TipsResponse(tips=tips)

    except Exception as e:
        print("Error in /reco/generate:", e)
        raise HTTPException(
            status_code=500,
            detail=f"AI recommendation error: {str(e)}"
        )


# ---------------------------------------------------
# Chat API
# ---------------------------------------------------
@router.post("/chat")
def chat_with_ai(payload: dict):
    try:
        response = generate_chat_response(payload)

        if not isinstance(response, str):
            raise ValueError("AI returned invalid chat response")

        return {"response": response}

    except Exception as e:
        print("Error in /reco/chat:", e)
        raise HTTPException(
            status_code=500,
            detail=f"AI chat error: {str(e)}"
        )
