# app/pages/leaderboard.py
import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="Leaderboard & Badges", page_icon="🏆", layout="wide")

# Minimal CSS consistent with Analyzer look
st.markdown("""
<style>
.page-title {
    font-size: 2.4rem; font-weight:800; text-align:center;
    background: linear-gradient(135deg,#00d4aa,#6c63ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom:6px;
}
.subtitle { text-align:center; color:#94a3b8; margin-bottom:20px; }
.leader-card { background: rgba(30,41,59,0.88); border-radius:14px; padding:18px; border:1px solid rgba(255,255,255,0.04); }
.top-1 { box-shadow: 0 20px 40px rgba(255,215,0,0.06); transform: translateY(-6px); }
.trophy { font-size:36px; }
.rank-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.muted { color:#94a3b8; }
.badge-score { font-weight:900; font-size:28px; background: linear-gradient(135deg,#37b3f5,#45f1a0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.small-muted { color:#94a3b8; font-size:13px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🏆 CarbonLens Leaderboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Compete, improve, and level up your sustainability journey 🌱</div>', unsafe_allow_html=True)

API = os.getenv("CARBONLENS_API") or os.getenv("BACKEND_URL") or "http://localhost:8000"

def fetch(path: str, timeout=4):
    try:
        r = requests.get(API.rstrip("/") + path, timeout=timeout)
        r.raise_for_status()
        return True, r.json()
    except Exception as e:
        return False, str(e)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    ok, data = fetch("/leaderboard")
    if not ok:
        st.warning("⚠️ API unavailable — leaderboard data could not be fetched.")
        st.info("Make sure backend is running (e.g. `uvicorn backend.main:app --reload`) and DB exists.")
        st.markdown("---")
    else:
        rows = data or []
        if not rows:
            st.info("No leaderboard data yet. Run the Analyzer to create footprint runs.")
        else:
            # Top 3 visual
            top = rows[:3]
            cols_top = st.columns(3)
            trophies = ["🥇","🥈","🥉"]
            for i, entry in enumerate(top):
                with cols_top[i]:
                    extra_class = "top-1" if i == 0 else ""
                    st.markdown(f"<div class='leader-card {extra_class}'>", unsafe_allow_html=True)
                    st.markdown(f"<div style='display:flex;align-items:center;gap:10px;'><div class='trophy'>{trophies[i]}</div><div><div style='font-weight:800'>{entry['name']}</div><div class='small-muted'>Tier: {entry.get('tier','-')} • XP: {entry.get('xp',0)}</div></div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='margin-top:10px'><div class='muted'>Score</div><div class='badge-score'>{entry['score']}</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🌱 Full Leaderboard (Top 20)")
            for idx, entry in enumerate(rows[:20], start=1):
                created = entry.get("created_at")
                if isinstance(created, str):
                    created_s = created
                else:
                    created_s = created.strftime("%Y-%m-%d") if created else ""
                st.markdown(f"""
                    <div class='leader-card' style='margin-bottom:10px;'>
                        <div class='rank-row'><div><b>#{idx} {entry['name']}</b></div>
                        <div style='text-align:right'><div class='muted'>{created_s}</div><div class='badge-score'>{entry['score']}</div></div></div>
                        <div style='margin-top:6px' class='small-muted'>Tier: {entry.get('tier','-')} • XP: {entry.get('xp',0)}</div>
                    </div>
                """, unsafe_allow_html=True)

# Right column: monthly leaderboard quick view & controls
with col3:
    ok_m, monthly = fetch("/leaderboard/monthly")
    st.markdown("<div style='padding:12px;border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700'>This month</div>", unsafe_allow_html=True)
    if not ok_m:
        st.markdown("<div class='small-muted'>Monthly leaderboard not available — backend unreachable.</div>", unsafe_allow_html=True)
    else:
        ml = monthly or []
        if not ml:
            st.markdown("<div class='small-muted'>No runs this month yet.</div>", unsafe_allow_html=True)
        else:
            for m in ml[:6]:
                st.markdown(f"<div style='margin-bottom:8px'><b>{m['name']}</b> — <span class='small-muted'>{m['score']} pts</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer / diagnostics
st.markdown("---")
st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;'><div class='small-muted'>Tip: Run Analyzer to add leaderboard entries.</div><div class='small-muted'>API: {}</div></div>".format(API), unsafe_allow_html=True)
