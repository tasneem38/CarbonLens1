import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# -----------------------------
# FALLBACK Recommendations
# -----------------------------
def fallback_recs(totals, highest, profile):
    return [
        {
            "title": "Improve home energy efficiency",
            "text": (
                f"Your energy emissions are {totals.get('energy',0)} kg/month. "
                "Start with simple high-impact fixes like sealing drafts, reducing AC load, "
                "and switching to LED lighting."
            ),
            "impact_kg_month": max(5, int(totals.get("energy", 0) * 0.10)),
            "confidence": 0.85,
            "steps": [
                "Seal gaps around doors/windows using weather strips.",
                "Replace 5–10 bulbs with LEDs.",
                "Increase AC temperature by 1–2°C."
            ],
            "category": "Energy"
        },
        {
            "title": "Reduce short car trips",
            "text": (
                f"Travel emissions are {totals.get('travel',0)} kg/month. "
                "Short trips waste the most fuel — combining errands helps reduce this."
            ),
            "impact_kg_month": max(3, int(totals.get("travel", 0) * 0.15)),
            "confidence": 0.75,
            "steps": [
                "List all weekly short trips.",
                "Group 2–3 trips into a single outing.",
                "Try public transport at least once per week."
            ],
            "category": "Travel"
        },
        {
            "title": "Lower food-based emissions",
            "text": (
                f"Food-related CO₂ is {totals.get('food',0)} kg/month. "
                "Reducing high-emission meals (red meat, dairy-heavy dishes) makes a big difference."
            ),
            "impact_kg_month": max(4, int(totals.get("food", 0) * 0.12)),
            "confidence": 0.80,
            "steps": [
                "Replace 2 red-meat meals with plant-based options.",
                "Try legume-based proteins like chickpeas or lentils.",
                "Shift 1–2 weekly meals to vegetarian."
            ],
            "category": "Food"
        }
    ]


# -----------------------------
# Extract JSON from model text
# -----------------------------
def _extract_json_from_text(text: str):
    if not text:
        return None
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # Try ```json fenced block
    m = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except:
            pass

    # Try to extract first list/object
    m2 = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if m2:
        try:
            return json.loads(m2.group(1))
        except:
            pass

    return None


# -----------------------------
# Main Recommendation Generator
# -----------------------------
def generate_tips(payload):
    totals = {
        "total": payload.get("total") or payload.get("total_kg") or 0,
        "energy": payload.get("energy") or payload.get("energy_kg") or 0,
        "travel": payload.get("travel") or payload.get("travel_kg") or 0,
        "food": payload.get("food") or payload.get("food_kg") or 0,
        "goods": payload.get("goods") or payload.get("goods_kg") or 0,
    }

    profile = payload.get("profile", "your lifestyle")

    highest = max(
        [
            ("energy", totals["energy"]),
            ("travel", totals["travel"]),
            ("food", totals["food"]),
            ("goods", totals["goods"])
        ],
        key=lambda x: x[1]
    )[0]

    # -----------------------------
    # Better / friendlier system prompt
    # -----------------------------
    system_prompt = f"""
You are an expert carbon footprint coach who writes warm, motivating,
and highly actionable recommendations.

STRICT RULES:
- Use ONLY the values given below (do NOT guess).
- Provide **4–6 recommendations**.
- Each recommendation MUST contain:
  - title
  - text (2–3 sentence explanation)
  - impact_kg_month (INTEGER)
  - confidence (0–1)
  - steps (3–5 short bullet points)
  - category (Energy, Travel, Food, Goods)
- Add brief citations like: (Analyzer: 50 kg energy)
- Give advice suitable for an Indian urban user unless stated otherwise.
- Keep tone friendly, helpful, and specific.

User Profile: {profile}

CO₂ Analyzer Values:
Total: {totals['total']} kg/month
Energy: {totals['energy']} kg
Travel: {totals['travel']} kg
Food: {totals['food']} kg
Goods: {totals['goods']} kg

Highest-impact area: {highest}
"""

    user_prompt = """
Return **ONLY a JSON list**, no intro text.
"""

    # -----------------------------
    # Call Groq LLM
    # -----------------------------
    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.25,
            max_tokens=900,
        )
        raw = resp.choices[0].message.content

    except Exception as e:
        print("ERROR contacting Groq:", e)
        return fallback_recs(totals, highest, profile)

    print("=== RAW LLM OUTPUT START ===")
    print(raw)
    print("=== RAW LLM OUTPUT END ===")

    parsed = _extract_json_from_text(raw)

    if not parsed or not isinstance(parsed, list):
        print("LLM returned NO valid JSON → fallback.")
        return fallback_recs(totals, highest, profile)

    recommendations = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict):
            continue

        recommendations.append({
            "title": item.get("title", f"Recommendation {i+1}"),
            "text": item.get("text", ""),
            "impact_kg_month": int(item.get("impact_kg_month") or 0),
            "confidence": float(item.get("confidence") or 0.7),
            "steps": item.get("steps") if isinstance(item.get("steps"), list) else [],
            "category": item.get("category", "General")
        })

    if not recommendations:
        return fallback_recs(totals, highest, profile)

    return recommendations

# ---------------------------------------------------
# Chat Assistant (Groq)
# ---------------------------------------------------
def generate_chat_response(payload):
    """Generate a higher-quality, memory-aware response using Groq."""

    question = payload.get("user_question", "")
    history = payload.get("chat_history", [])
    totals = payload.get("totals", {})

    total = totals.get("total", 0)
    energy = totals.get("energy", 0)
    travel = totals.get("travel", 0)
    food = totals.get("food", 0)
    goods = totals.get("goods", 0)

    profile = payload.get("profile", "your lifestyle")

    # Determine highest-impact category
    highest = max(
        [("energy", energy), ("travel", travel), ("food", food), ("goods", goods)],
        key=lambda x: x[1]
    )[0]

    # Improved system message
    system_prompt = f"""
You are a friendly, highly accurate carbon footprint coach.

RULES YOU MUST FOLLOW:
- Use ONLY the values provided below — NEVER guess.
- Give guidance in a warm, encouraging tone.
- When explaining numbers, cite them like this: “(Analyzer: 50 kg energy)”
- Provide 1–2 specific next steps when helpful.
- Keep responses concise but helpful.
- Maintain conversational memory.

User Profile: {profile}

CO2 VALUES — DO NOT ALTER:
Total: {total} kg/month
Energy: {energy} kg
Travel: {travel} kg
Food: {food} kg
Goods: {goods} kg

Highest-impact category: {highest}
"""

    # Convert chat_history → proper LLM message format
    formatted_history = []
    for msg in history:
        if msg["role"] == "user":
            formatted_history.append({"role": "user", "content": msg["content"]})
        else:
            formatted_history.append({"role": "assistant", "content": msg["content"]})

    # Include conversation memory + new question
    messages = [
        {"role": "system", "content": system_prompt},
        *formatted_history,
        {"role": "user", "content": question}
    ]

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.25,
            max_tokens=350
        )

        # Groq returns ChatCompletionMessage object, not dict
        content = resp.choices[0].message.content
        return content

    except Exception as e:
        print("CHAT MODEL ERROR:", e)
        return f"AI unavailable — based on your analyzer, your highest-impact area is **{highest}**."
