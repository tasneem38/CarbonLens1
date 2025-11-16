import yaml
import streamlit as st
from pathlib import Path

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Data Assumptions & Sources", page_icon="🔍", layout="wide")

# ---------- GLOBAL PAGE STYLE (CarbonLens THEME) ----------
st.markdown("""
<style>

/* Main Container Width */
.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
}

/* Title */
.page-title {
    font-size: 38px;
    font-weight: 700;
    color: #222;
    text-align: left;
    margin-bottom: 5px;
}

/* Subtitle */
.sub-text {
    color: #555;
    margin-top: -5px;
    margin-bottom: 30px;
    font-size: 17px;
}

/* Cards Grid */
.card-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
    gap: 28px;
    margin-top: 15px;
}

/* Individual Card */
.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border: 1px solid #e8e8e8;
    transition: 0.25s ease;
}

/* Hover Motion */
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    border-color: #4CAF50;
}

/* Card Heading */
.card h4 {
    margin-bottom: 12px;
    font-size: 20px;
    font-weight: 650;
    color: #222;
}

/* Source tag */
.source-tag {
    font-size: 13px;
    background: #E8F5E9;
    padding: 5px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 12px;
    color: #1B5E20;
}

/* Disclaimer Box */
.disclaimer-box {
    background: #fffaf0;
    padding: 18px 22px;
    border-radius: 14px;
    border-left: 6px solid #FFB300;
    margin-top: 40px;
    font-size: 15px;
    color: #3d3d3d;
}

</style>
""", unsafe_allow_html=True)


# ---------- TITLE AREA ----------
st.markdown('<div class="page-title">🔍 Data Assumptions & Sources</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Reference emission factors used for calculating your CarbonLens footprint.</div>', unsafe_allow_html=True)


# ---------- LOAD YAML ----------
EF_PATH = Path(__file__).resolve().parents[2] / "config" / "emission_factors.yaml"

try:
    with open(EF_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
except Exception:
    data = {
        "factors": {
            "electricity_kg_per_kwh": 0.82,
            "travel": {"car_kg_per_km": 0.21, "bus_kg_per_km": 0.09, "train_kg_per_km": 0.04},
            "food_monthly_kg": {"veg": 120, "mixed": 160, "nonveg": 216}
        }
    }


# ---------- CARD GRID ----------
st.markdown('<div class="card-container">', unsafe_allow_html=True)

# ELECTRICITY CARD
st.markdown(f"""
<div class="card">
    <h4>⚡ Electricity</h4>
    <p><b>{data["factors"]["electricity_kg_per_kwh"]} kg CO₂</b> per kWh</p>
    <div class="source-tag">Source: CEA Baseline v18</div>
</div>
""", unsafe_allow_html=True)

# TRAVEL CARD
st.markdown(f"""
<div class="card">
    <h4>🚗 Travel</h4>
    <p>
        Car: <b>{data["factors"]["travel"]["car_kg_per_km"]}</b> kg/km<br>
        Bus: <b>{data["factors"]["travel"]["bus_kg_per_km"]}</b> kg/km<br>
        Train: <b>{data["factors"]["travel"]["train_kg_per_km"]}</b> kg/km
    </p>
    <div class="source-tag">Source: IEA / MoEFCC</div>
</div>
""", unsafe_allow_html=True)

# FOOD CARD
st.markdown(f"""
<div class="card">
    <h4>🍽️ Monthly Food Emissions</h4>
    <p>
        Vegetarian: <b>{data["factors"]["food_monthly_kg"]["veg"]}</b> kg/month<br>
        Mixed: <b>{data["factors"]["food_monthly_kg"]["mixed"]}</b> kg/month<br>
        Non-Veg: <b>{data["factors"]["food_monthly_kg"]["nonveg"]}</b> kg/month
    </p>
    <div class="source-tag">Source: FAO / IPCC</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ---------- DISCLAIMER ----------
st.markdown("""
<div class="disclaimer-box">
<b>Disclaimer:</b> These emission values are estimates sourced from IPCC, IEA, FAO, and CEA India.  
Actual emissions vary depending on location, grid mix, travel mode, and dietary patterns.
</div>
""", unsafe_allow_html=True)
