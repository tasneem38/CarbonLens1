# app/pages/2_AI_Recommendations.py
"""
AI Recommendations — upgraded full page.

Features:
- Uses Analyzer result in st.session_state['last_result']
- Calls local backend functions if available, else tries /reco/generate endpoints
- 2-column grid layout (desktop), 1-column on narrow screens
- Glowing outlined cards similar to Analyzer profile cards
- Confidence badge, category color badges
- Collapsible details & implementation checkbox (unique keys)
- Fallback steps generator if AI doesn't provide steps
"""
import os
import json
import random
import requests
import html
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# Backend connection config
# -----------------------
BACKEND_URL = os.environ.get("BACKEND_URL")
CANDIDATES = []
if BACKEND_URL:
    CANDIDATES.append(BACKEND_URL.rstrip("/"))
CANDIDATES += ["http://127.0.0.1:8080", "http://localhost:8080", "http://127.0.0.1:8000", "http://localhost:8000"]
API_BASE_CANDIDATES = []
for c in CANDIDATES:
    if c and c not in API_BASE_CANDIDATES:
        API_BASE_CANDIDATES.append(c)

RECO_ENDPOINTS = ["{base}/reco/generate", "{base}/api/reco/generate"]
CHAT_ENDPOINTS = ["{base}/reco/chat", "{base}/api/reco/chat"]

# Prefer local import (fast path) if backend code is available in same venv/project
LOCAL_BACKEND_AVAILABLE = False
_local_generate_tips = None
_local_generate_chat = None
try:
    from backend.services.recommender import generate_tips as _local_generate_tips
    from backend.services.recommender import generate_chat_response as _local_generate_chat
    LOCAL_BACKEND_AVAILABLE = True
except Exception:
    LOCAL_BACKEND_AVAILABLE = False

# -----------------------
# Helpers: call backend or local function
# -----------------------
def call_reco_backend(payload, timeout=6):
    # try local
    if LOCAL_BACKEND_AVAILABLE and _local_generate_tips:
        try:
            tips = _local_generate_tips(payload)
            if isinstance(tips, list):
                return {"success": True, "recommendations": tips, "source": "local"}
            if isinstance(tips, dict) and "tips" in tips:
                return {"success": True, "recommendations": tips["tips"], "source": "local"}
        except Exception:
            pass

    # try http endpoints
    for base in API_BASE_CANDIDATES:
        for tmpl in RECO_ENDPOINTS:
            url = tmpl.format(base=base)
            try:
                r = requests.post(url, json=payload, timeout=timeout)
                if r.status_code == 200:
                    try:
                        j = r.json()
                    except Exception:
                        j = r.text
                    # normalize a bit
                    if isinstance(j, dict) and "tips" in j:
                        return {"success": True, "recommendations": j["tips"], "source": url}
                    if isinstance(j, list):
                        return {"success": True, "recommendations": j, "source": url}
                    if isinstance(j, dict) and "recommendations" in j:
                        return {"success": True, "recommendations": j["recommendations"], "source": url}
                    return {"success": True, "recommendations": j, "source": url}
            except Exception:
                continue
    return {"success": False, "error": "No reachable recommendation backend."}


def call_chat_backend(payload, timeout=8):
    # try local
    if LOCAL_BACKEND_AVAILABLE and _local_generate_chat:
        try:
            resp = _local_generate_chat(payload)
            if isinstance(resp, dict):
                text = resp.get("response") or resp.get("reply") or str(resp)
            else:
                text = str(resp)
            return {"success": True, "response": text, "source": "local"}
        except Exception:
            pass

    for base in API_BASE_CANDIDATES:
        for tmpl in CHAT_ENDPOINTS:
            url = tmpl.format(base=base)
            try:
                r = requests.post(url, json=payload, timeout=timeout)
                if r.status_code == 200:
                    try:
                        j = r.json()
                    except Exception:
                        return {"success": True, "response": r.text, "source": url}
                    if isinstance(j, dict):
                        return {"success": True, "response": j.get("response") or j.get("reply") or j.get("message") or str(j), "source": url}
                    return {"success": True, "response": str(j), "source": url}
            except Exception:
                continue
    return {"success": False, "error": "No reachable chat backend."}


# -----------------------
# UI Styling (match Analyzer)
# -----------------------
st.set_page_config(page_title="AI Recommendations - CarbonLens", page_icon="🤖", layout="wide")
st.markdown("""
<style>
:root{
  --bg: #0f172a;
  --card-start: rgba(8,20,31,0.85);
  --card-end: rgba(12,20,31,0.9);
  --muted: #94a3b8;
  --accent: #00d4aa;
  --accent2: #6c63ff;
}
body, html, .main, .block-container {
  background: linear-gradient(135deg,#0f172a,#0b1220) !important;
  color: #e6eef6;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}


/* header row */
.reco-top { display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
.reco-left { display:flex; gap:12px; flex-direction:column; }
.reco-title { font-size:20px; font-weight:800; color: #fff; margin:0; }
.reco-sub { color: var(--muted); margin-top:6px; font-size:14px; }

/* badges and pills */
.badge { padding:6px 10px; border-radius:999px; font-weight:700; font-size:12px; display:inline-block; }
.badge-food { background: rgba(255,100,100,0.07); color:#ffb3b3; border:1px solid rgba(255,100,100,0.12); }
.badge-energy { background: rgba(0,212,170,0.07); color:var(--accent); border:1px solid rgba(0,212,170,0.12); }
.badge-travel { background: rgba(108,99,255,0.07); color:var(--accent2); border:1px solid rgba(108,99,255,0.12); }
.badge-general { background: rgba(145,145,145,0.07); color:var(--muted); border:1px solid rgba(145,145,145,0.08); }

.conf-pill { padding:6px 12px; border-radius:999px; font-weight:700; font-size:13px; background: linear-gradient(90deg,var(--accent),var(--accent2)); color:white; }

/* description area */
.reco-desc { color:var(--muted); margin-top:12px; margin-bottom:10px; }

/* expander override for visuals */
.stExpander > div > div { background: transparent !important; border-radius: 10px !important; color: var(--muted) !important; }

/* progress bar mimic (small) */
.savings-meta { text-align:right; color:var(--muted); font-size:13px; }

/* small layout */
.row { display:flex; gap:12px; align-items:center; }
.right { margin-left:auto; }
</style>
""", unsafe_allow_html=True)
# -----------------------
# Page Header (Matches Analyzer Style)
# -----------------------
st.markdown("""
<style>
.ai-header {
    text-align: center;
    margin-top: -20px;
    margin-bottom: 25px;
}

.ai-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #3bc9db, #5f3dc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.ai-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-top: -8px;
}
</style>

<div class="ai-header">
    <div class="ai-title">♻️ AI Recommendations</div>
    <div class="ai-subtitle">Personalized, prioritized recommendations — based on your Analyzer results.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Load Analyzer result
# -----------------------
if "last_result" not in st.session_state or not st.session_state.get("last_result"):
    st.error("⚠️ No analysis data found. Please run the Analyzer (Compute My Carbon Footprint) first.")
    st.stop()

result = st.session_state["last_result"]
if isinstance(result, dict) and "totals" in result:
    totals = result["totals"]
    score = result.get("score", None)
    breakdown = result.get("breakdown", {})
    trend = result.get("trend", [])
else:
    totals = result if isinstance(result, dict) else {"total": 0}
    score = result.get("score") if isinstance(result, dict) else None
    breakdown = {}
    trend = []

# determine highest category
candidate_keys = [k for k in ("energy", "travel", "food", "goods") if k in totals]
highest_category = max(candidate_keys, key=lambda k: totals.get(k, 0)) if candidate_keys else None
profile = st.session_state.get("selected_profile") or st.session_state.get("demo_data") and st.session_state.get("selected_profile") or "Your Profile"

# top metrics row (avoid repeating multiple times)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Green Score", f"{score}/100" if score is not None else "N/A")
with c2:
    st.metric("Monthly CO₂", f"{totals.get('total', 0)} kg")
with c3:
    st.metric("Highest Impact", highest_category.replace("_"," ").title() if highest_category else "N/A")
with c4:
    st.metric("Profile", profile)

st.markdown("---")

# -----------------------
# Recommendation retrieval & normalization
# -----------------------
def fallback_recs(totals, highest_category, profile):
    # simple fallback recs and include steps
    recs = [
        {
            "id": f"r_food_{random.randint(1000,9999)}",
            "title": "Replace two red meat meals per week with plant-based alternatives",
            "text": "Swap two red-meat meals weekly for plant-based alternatives to cut food-related emissions.",
            "impact_kg_month": max(10, int(totals.get("food", 0) * 0.12)),
            "confidence": 0.75,
            "steps": [
                "Identify two red-meat meals to replace this week.",
                "Find 3 simple plant-based recipes to try (e.g., lentil curry, chickpea tacos).",
                "Plan meals and grocery list for the week; repeat for 4 weeks."
            ],
            "category": "Food"
        },
        {
            "id": f"r_energy_{random.randint(1000,9999)}",
            "title": "Conduct a home energy audit to identify hidden energy drains",
            "text": "A home energy audit surfaces leaks, inefficient appliances and helps prioritize actions.",
            "impact_kg_month": max(8, int(totals.get("energy", 0) * 0.08)),
            "confidence": 0.80,
            "steps": [
                "Walk every room to identify drafts around doors/windows.",
                "List major appliances older than 8 years for replacement consideration.",
                "Measure standby loads (smart plugs) and reduce phantom power."
            ],
            "category": "General"
        }
    ]
    return recs

if "ai_recommendations" not in st.session_state:
    payload = {
        **(breakdown if isinstance(breakdown, dict) else {}),
        **(totals if isinstance(totals, dict) else {}),
        "score": score,
        "profile": profile
    }
    resp = call_reco_backend(payload)
    if resp.get("success"):
        raw = resp.get("recommendations") or []
        normalized = []
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                continue
            rec_id = item.get("id") or f"rec_{i}_{random.randint(0,9999)}"
            title = item.get("title") or item.get("text") or item.get("area") or f"Recommendation {i+1}"
            text = item.get("text") or item.get("description") or ""
            impact = item.get("impact_kg_month") or item.get("potential_savings") or item.get("impact") or 0
            confidence = float(item.get("confidence", 0.75))
            steps = item.get("steps") if isinstance(item.get("steps"), list) else []
            category = item.get("category") or item.get("area") or "General"
            # ensure steps: fill default if empty
            if not steps:
                # category-aware default steps
                if "energy" in category.lower() or ("energy" in title.lower()):
                    steps = [
                        "Check thermostat settings and program a 1–2°C setback.",
                        "Replace incandescent bulbs with LED bulbs across the home.",
                        "Unplug rarely-used devices or use smart power strips."
                    ]
                elif "travel" in category.lower() or ("car" in title.lower()):
                    steps = [
                        "Track weekly driving distance for one week.",
                        "Identify 1–2 trips per week you can combine or use transit for.",
                        "Explore carpool options and a monthly transit pass."
                    ]
                elif "food" in category.lower():
                    steps = [
                        "List your weekly meals and highlight red-meat dishes.",
                        "Look up 3 plant-based swaps and try them this week.",
                        "Gradually increase plant-based meals to 3 per week."
                    ]
                else:
                    steps = [
                        "Run a quick assessment of your home and behavior patterns.",
                        "Pick one small change this week and measure its impact.",
                        "Re-evaluate after 2–4 weeks and scale what works."
                    ]
            normalized.append({
                "id": rec_id,
                "title": title,
                "text": text,
                "impact_kg_month": int(impact),
                "confidence": confidence,
                "steps": steps,
                "category": category
            })
        rec_list = normalized or fallback_recs(totals, highest_category, profile)
    else:
        rec_list = fallback_recs(totals, highest_category, profile)
    # dedupe by title
    seen_titles = set()
    deduped = []
    for r in rec_list:
        t = r["title"].strip().lower()
        if t in seen_titles:
            continue
        seen_titles.add(t)
        deduped.append(r)
    # prioritize highest_category
    if highest_category:
        prioritized = [r for r in deduped if highest_category.lower() in r.get("category","").lower()]
        others = [r for r in deduped if r not in prioritized]
        deduped = prioritized + others
    st.session_state.ai_recommendations = deduped

reco_list = st.session_state.ai_recommendations or []

# -----------------------
# Render recommendations in a 2-column grid (desktop)
# -----------------------
def badge_class(category):
    c = (category or "General").lower()
    if "food" in c:
        return "badge badge-food"
    if "energy" in c:
        return "badge badge-energy"
    if "travel" in c or "transport" in c:
        return "badge badge-travel"
    return "badge badge-general"

# Build grid: two columns
st.markdown("<div class='reco-grid'>", unsafe_allow_html=True)

for rec in reco_list:
    rec_id = rec.get("id") or f"rec_{random.randint(1000,9999)}"
    title = html.escape(rec.get("title", "Recommendation"))
    desc = rec.get("text", "")
    impact = rec.get("impact_kg_month", 0)
    confidence = rec.get("confidence", 0.75)
    steps = rec.get("steps", [])
    category = rec.get("category", "General")

    # Unique widget keys (safe)
    checkbox_key = f"impl_{rec_id}"
    # Ensure default exists but DO NOT write after widget creation (let checkbox manage session state)
    if checkbox_key not in st.session_state:
        st.session_state[checkbox_key] = False

    # Determine outline style: highlight if matches highest_category
    outline_class = "reco-card outline" if (highest_category and highest_category.lower() in category.lower()) else "reco-card"

    # Render card HTML container
    st.markdown(f"<div class='{outline_class}'>", unsafe_allow_html=True)

    # Top row: title left, savings+confidence right
    top_cols = st.columns([6, 2, 1])
    with top_cols[0]:
        st.markdown(f"<div class='reco-left'><div class='reco-title'>{title}</div>"
                    f"<div style='margin-top:6px'><span class='{badge_class(category)}'>{category}</span></div>"
                    f"<div class='reco-sub'>{html.escape(desc)}</div></div>", unsafe_allow_html=True)
    with top_cols[1]:
        st.markdown(f"<div class='savings-meta' style='text-align:right'><div style='font-weight:700'>{impact} kg/mo</div><div style='color:var(--muted);font-size:12px'>savings</div></div>", unsafe_allow_html=True)
    with top_cols[2]:
        st.markdown(f"<div style='text-align:right'><span class='conf-pill'>{int(confidence*100)}%</span></div>", unsafe_allow_html=True)

    # Collapsible details & steps (use expander without key to avoid older Streamlit mismatch)
    with st.expander("Details & Steps", expanded=False):
        if steps:
            for s in steps:
                st.markdown(f"- {html.escape(s)}")
        else:
            st.markdown("- No detailed steps provided. Ask the assistant to expand this into a plan.")

    # Action row with checkbox (key used, but don't mutate st.session_state after)
    action_cols = st.columns([4, 1])
    with action_cols[0]:
        st.markdown("<div style='color:var(--muted);margin-top:6px'>Mark this as implemented to track progress.</div>", unsafe_allow_html=True)
    with action_cols[1]:
        # Use st.checkbox with key -> Streamlit will keep state in st.session_state[checkbox_key]
        checked_val = st.checkbox("Done", value=st.session_state.get(checkbox_key, False), key=checkbox_key)

    # close card container
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close grid

st.markdown("---")

# -----------------------
# Chat assistant
# -----------------------
st.markdown("### 💬 Carbon Reduction Assistant")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# sanitize chat_history
st.session_state.chat_history = [m for m in st.session_state.chat_history if isinstance(m, dict) and "role" in m and "content" in m]

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask about your recommendations or highest-impact actions", "")
    send = st.form_submit_button("Send")

if send and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
    chat_payload = {
        "user_question": user_input.strip(),
        "energy_kg": totals.get("energy", 0),
        "travel_kg": totals.get("travel", 0),
        "food_kg": totals.get("food", 0),
        "goods_kg": totals.get("goods", 0),
        "totals": totals,
        "breakdown": breakdown,
        "score": score,
        "profile": profile,
        "chat_history": st.session_state.chat_history
    }
    chat_resp = call_chat_backend(chat_payload)
    if chat_resp.get("success"):
        assistant_text = chat_resp.get("response") or "No response returned by AI backend."
    else:
        assistant_text = (
            f"I can't reach the AI backend. Based on your Analyzer, prioritize reducing "
            f"{(highest_category or 'your main source')}. Example: {reco_list[0]['title'] if reco_list else 'Start with a home energy audit.'}"
        )
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
    # rerun to reflect chat and any UI changes (st.rerun is available in current Streamlit)
    try:
        st.rerun()
    except Exception:
        pass

# show chat history
for m in st.session_state.chat_history:
    if m["role"] == "user":
        st.markdown(f"**You:** {m['content']}")
    else:
        st.markdown(f"**Assistant:** {m['content']}")

# -----------------------
# Quick controls
# -----------------------
cols = st.columns(3)
with cols[0]:
    if st.button("Refresh AI recommendations"):
        st.session_state.pop("ai_recommendations", None)
        st.rerun()
with cols[1]:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
with cols[2]:
    st.markdown(f"Backend: {API_BASE_CANDIDATES[0] if API_BASE_CANDIDATES else 'auto (127.0.0.1)'}")
