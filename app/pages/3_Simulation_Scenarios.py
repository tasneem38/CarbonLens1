# app/pages/3_Simulation_Scenarios.py
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Tuple
import math
import os

st.set_page_config(page_title="What-If Scenarios", page_icon="🕹️", layout="wide")

# -------------------------
# Styling (match analyzer theme)
# -------------------------
st.markdown("""
<style>
:root {
    --primary: #00d4aa;
    --primary-light: #00f5d4;
    --primary-dark: #00b894;
    --secondary: #6c63ff;
    --secondary-light: #8a84ff;
    --accent: #ff6b6b;
    --success: #00d4aa;
    --warning: #ffd93d;
    --danger: #ff6b6b;
    --dark-bg: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.75);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
}

body {
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1e293b 100%);
}

/* TITLE */
.page-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1.15rem;
    margin-bottom: 2.5rem;
}

/* Scenario Cards */
.scenario-row {
    display:grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap:25px;
    margin: 1.5rem 0;
}

.scenario-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.75));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 22px;
    padding: 1.8rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.35);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.scenario-card:hover {
    transform: translateY(-10px);
    border-color: var(--primary);
    box-shadow: 0 25px 50px rgba(0, 212, 170, 0.18);
}

.scenario-card::before {
    content: "";
    position: absolute;
    top: -2px;
    left: 0;
    height: 4px;
    width: 100%;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}

/* Titles */
.scenario-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
}

.scenario-sub, .scenario-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin: 0.5rem 0 1rem;
}

/* Tags */
.pill {
    display:inline-block;
    padding:6px 12px;
    border-radius: 20px;
    background: rgba(255,255,255,0.08);
    color: var(--primary-light);
    font-size: 0.8rem;
    margin: 4px 6px 4px 0;
    border: 1px solid rgba(0,212,170,0.2);
}

/* Apply Button */
.stButton button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white !important;
    border-radius: 14px;
    padding: 12px 20px;
    width: 100%;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.25s ease;
    border: none;
}

.stButton button:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px rgba(0,212,170,0.35);
}

/* KPI cards */
.card {
    background: var(--card-bg);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 1.5rem;
    box-shadow: 0 12px 36px rgba(0,0,0,0.3);
    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-6px);
    border-color: var(--primary);
}

.metric-big {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
}

.small-muted {
    color: var(--text-secondary);
}

/* TRANSITION FIXES */
hr {
    border-color: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helpers
# -------------------------
def derive_inputs_from_result(result: Dict) -> Dict:
    """
    If Analyzer saved raw 'inputs' use them. Otherwise estimate inputs from breakdown.
    Returns dict with keys: electricityKwh, naturalGasTherms, carKm, busKm, foodEmissions, goodsEmissions
    """
    # Try direct inputs first
    if isinstance(result, dict) and "inputs" in result and isinstance(result["inputs"], dict) and result["inputs"]:
        inputs = result["inputs"]
        # ensure keys exist (provide sensible defaults)
        return {
            "electricityKwh": inputs.get("electricityKwh", 0),
            "naturalGasTherms": inputs.get("naturalGasTherms", 0),
            "carKm": inputs.get("carKm", 0),
            "busKm": inputs.get("busKm", 0),
            "foodEmissions": inputs.get("foodEmissions", 3.5),
            "goodsEmissions": inputs.get("goodsEmissions", result.get("totals", {}).get("goods", 0) if result.get("totals") else 0)
        }

    # Otherwise approximate from breakdown
    breakdown = result.get("breakdown", {}) if isinstance(result, dict) else {}
    totals = result.get("totals", {}) if isinstance(result, dict) else {}

    # Safe defaults and invert the typical emission factors used elsewhere
    ELECTRICITY_FACTOR = 0.82  # kgCO2 per kWh
    NATURAL_GAS_FACTOR = 5.3   # kgCO2 per therm
    CAR_FACTOR = 0.21
    BUS_FACTOR = 0.09

    elec_kg = breakdown.get("electricity") or breakdown.get("electricity_kwh", 0) or breakdown.get("energy", 0) * 0.5
    gas_kg = breakdown.get("natural_gas") or breakdown.get("naturalGas", 0) or 0
    car_kg = breakdown.get("car") or 0
    bus_kg = breakdown.get("bus") or 0
    food_kg = breakdown.get("food") or totals.get("food") or 0
    goods_kg = breakdown.get("goods") or totals.get("goods") or 0

    # invert to estimate activity numbers (guard divide-by-zero)
    est_electricity_kwh = round(elec_kg / ELECTRICITY_FACTOR, 1) if ELECTRICITY_FACTOR and elec_kg else 0
    est_natural_gas_therms = round(gas_kg / NATURAL_GAS_FACTOR, 1) if NATURAL_GAS_FACTOR and gas_kg else 0
    est_car_km = round(car_kg / CAR_FACTOR, 1) if CAR_FACTOR and car_kg else 0
    est_bus_km = round(bus_kg / BUS_FACTOR, 1) if BUS_FACTOR and bus_kg else 0
    est_food_daily = round((food_kg / 30.0), 2) if food_kg else 3.5

    return {
        "electricityKwh": est_electricity_kwh,
        "naturalGasTherms": est_natural_gas_therms,
        "carKm": est_car_km,
        "busKm": est_bus_km,
        "foodEmissions": est_food_daily,
        "goodsEmissions": goods_kg
    }


def simulate_from_inputs(base_inputs: Dict,
                         car_pct: float,
                         elec_pct: float,
                         diet_pct: float,
                         renew_pct: float,
                         waste_pct: float,
                         shop_pct: float) -> Tuple[Dict, Dict, float]:
    """
    Percentages are 0-100 reductions or adoption.
    Returns (before_dict, after_dict, estimated_score)
    """
    # emission factors
    ELECTRICITY_FACTOR = 0.82
    NATURAL_GAS_FACTOR = 5.3
    CAR_FACTOR = 0.21
    BUS_FACTOR = 0.09

    elec_kwh = base_inputs.get("electricityKwh", 0)
    gas_therms = base_inputs.get("naturalGasTherms", 0)
    car_km = base_inputs.get("carKm", 0)
    bus_km = base_inputs.get("busKm", 0)
    food_daily = base_inputs.get("foodEmissions", 3.5)
    goods = base_inputs.get("goodsEmissions", 0)

    energy_before = elec_kwh * ELECTRICITY_FACTOR + gas_therms * NATURAL_GAS_FACTOR
    travel_before = car_km * CAR_FACTOR + bus_km * BUS_FACTOR
    food_before = food_daily * 30
    goods_before = goods
    total_before = energy_before + travel_before + food_before + goods_before

    # Apply reductions
    energy_after = energy_before * (1 - elec_pct / 100.0) * (1 - renew_pct / 200.0)
    travel_after = travel_before * (1 - car_pct / 100.0)
    food_after = food_before * (1 - diet_pct / 100.0) * (1 - waste_pct / 200.0)
    goods_after = goods_before * (1 - shop_pct / 100.0)
    total_after = max(0.0, energy_after + travel_after + food_after + goods_after)

    # estimate score: start from baseline score if available, else heuristic
    baseline_score = st.session_state.get("last_result", {}).get("score")
    if baseline_score is None:
        baseline_score = max(10, min(95, 100 - (total_before / 600.0) * 100))
    improvement = (total_before - total_after) / total_before if total_before > 0 else 0
    estimated_score = min(100.0, max(0.0, baseline_score + improvement * 40.0))

    before = {"Energy": round(energy_before, 1), "Travel": round(travel_before, 1),
              "Food": round(food_before, 1), "Goods": round(goods_before, 1)}
    after = {"Energy": round(energy_after, 1), "Travel": round(travel_after, 1),
             "Food": round(food_after, 1), "Goods": round(goods_after, 1)}

    return before, after, round(estimated_score, 1)


# -------------------------
# Scenario presets (percentages)
# -------------------------
SCENARIOS = {
    "Eco Beginner": {
        "desc": "Entry-level behavioural shifts requiring low friction: LEDs, turning off devices, modest transit & diet changes.",
        "bullets": [
            "10–20% energy savings (LEDs, turn devices off)",
            "10–25% car reduction (plan trips, carpool)",
            "10–20% dietary shift (1 meat-free day/week)",
            "10–15% food waste reduction"
        ],
        "changes": {"car": 20, "elec": 15, "diet": 12, "renew": 10, "waste": 12, "shop": 10}
    },
    "Green Warrior": {
        "desc": "Committed lifestyle shifts consistent with motivated households (WWF-style).",
        "bullets": [
            "40–60% car reduction (switch to transit/cycling)",
            "40–60% energy reduction (efficiency + partial renewables)",
            "40–60% plant-forward diet adoption",
            "40% shopping reduction"
        ],
        "changes": {"car": 50, "elec": 50, "diet": 50, "renew": 40, "waste": 30, "shop": 40}
    },
    "Minimalist": {
        "desc": "Deep sustainability transformation: low-consumption lifestyles found in eco communities.",
        "bullets": [
            "70–90% shopping reduction",
            "60–80% travel reduction",
            "70–90% renewables adoption",
            "70–90% dietary shift"
        ],
        "changes": {"car": 75, "elec": 75, "diet": 75, "renew": 80, "waste": 60, "shop": 80}
    }
}

# -------------------------
# Load actual/demo footprint and derive inputs if needed
# -------------------------
if "last_result" in st.session_state and st.session_state.get("last_result"):
    last_result = st.session_state["last_result"]
else:
    last_result = {}

# if last_result has 'totals' and 'breakdown' use them, else demo fallback
if last_result:
    totals = last_result.get("totals", {})
    current_score = last_result.get("score", 0)
else:
    totals = {}
    current_score = 0

# derive inputs (uses provided inputs if available; otherwise estimates)
inputs = derive_inputs_from_result(last_result) if last_result else {
    "electricityKwh": 350, "naturalGasTherms": 60, "carKm": 600, "busKm": 100,
    "foodEmissions": 3.5, "goodsEmissions": 250
}

# ensure sim state variables exist
if "sim_car" not in st.session_state: st.session_state.sim_car = 0
if "sim_elec" not in st.session_state: st.session_state.sim_elec = 0
if "sim_diet" not in st.session_state: st.session_state.sim_diet = 0
if "sim_renew" not in st.session_state: st.session_state.sim_renew = 0
if "sim_waste" not in st.session_state: st.session_state.sim_waste = 0
if "sim_shop" not in st.session_state: st.session_state.sim_shop = 0

# Top header (KPIs)
st.markdown("<h1 class='page-title'>🕹️ What-If Scenarios</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Visualize how lifestyle shifts impact your carbon footprint — inspired by your Analyzer results.</div>", unsafe_allow_html=True)

# KPIs row
k1, k2, k3, k4 = st.columns([1,1,1,1])
with k1:
    st.markdown("<div class='card' style='text-align:left;'><div class='small-muted'>Green Score</div><div class='metric-big'>{}</div></div>".format(current_score), unsafe_allow_html=True)
with k2:
    st.markdown("<div class='card' style='text-align:left;'><div class='small-muted'>Monthly CO₂</div><div class='metric-big'>{:.1f} kg</div></div>".format(totals.get("total", 0.0)), unsafe_allow_html=True)
with k3:
    highest = max(("energy","travel","food","goods"), key=lambda k: totals.get(k,0)) if isinstance(totals, dict) and totals else None
    highest_label = (highest or "N/A").title()
    st.markdown("<div class='card' style='text-align:left;'><div class='small-muted'>Highest Impact</div><div class='metric-big'>{}</div></div>".format(highest_label), unsafe_allow_html=True)
with k4:
    profile = st.session_state.get("selected_profile") or (st.session_state.get("demo_data") and st.session_state.get("selected_profile")) or "Your Profile"
    st.markdown("<div class='card' style='text-align:left;'><div class='small-muted'>Profile</div><div class='metric-big'>{}</div></div>".format(profile), unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Scenario cards (3 in a row)
# -------------------------
st.markdown("<div class='scenario-row'>", unsafe_allow_html=True)
for name, meta in SCENARIOS.items():
    # Build HTML for card content then render Streamlit button underneath
    card_html = "<div class='scenario-card'>"
    card_html += f"<div><div class='scenario-title'>{name}</div>"
    card_html += f"<div class='scenario-sub'>{meta['desc']}</div></div>"
    card_html += f"<div class='scenario-desc'><b>Based on:</b> "
    if name == "Eco Beginner":
        card_html += "studies showing beginners adopt low-friction changes."
    elif name == "Green Warrior":
        card_html += "behavioural & WWF-style studies for motivated households."
    else:
        card_html += "patterns from low-consumption eco-communities."
    card_html += "</div>"
    card_html += "<div class='scenario-list'>"
    for bullet in meta["bullets"]:
        card_html += f"<span class='pill'>{bullet}</span>"
    card_html += "</div>"
    ch = meta["changes"]
    approx = f"Approx. changes: Energy {ch['elec']}%, Transport {ch['car']}%, Diet {ch['diet']}%"
    card_html += f"<div style='color:var(--muted); margin-top:10px;'>{approx}</div>"
    card_html += "</div>"

    st.markdown(card_html, unsafe_allow_html=True)

    # Place Apply button (full width)
    btn_key = f"apply_{name.replace(' ','_')}"
    if st.button(f"Apply {name}", key=btn_key):
        st.session_state.sim_car = ch["car"]
        st.session_state.sim_elec = ch["elec"]
        st.session_state.sim_diet = ch["diet"]
        st.session_state.sim_renew = ch.get("renew", 0)
        st.session_state.sim_waste = ch.get("waste", 0)
        st.session_state.sim_shop = ch.get("shop", 0)
        st.session_state.applied_scenario = name
        # immediate rerun so pies update
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Compute simulation based on current session_state percentages
# -------------------------
before_vals, after_vals, est_score = simulate_from_inputs(
    inputs,
    st.session_state.sim_car,
    st.session_state.sim_elec,
    st.session_state.sim_diet,
    st.session_state.sim_renew,
    st.session_state.sim_waste,
    st.session_state.sim_shop
)

# -------------------------
# Show big comparison (Before / After pies and score)
# -------------------------
col_b, col_a, col_s = st.columns([1,1,0.7])
with col_b:
    st.markdown("<div class='card'><b>Actual (Before)</b></div>", unsafe_allow_html=True)
    fig_b = go.Figure(data=[go.Pie(labels=list(before_vals.keys()), values=list(before_vals.values()), hole=0.45, textinfo='label+percent')])
    fig_b.update_layout(margin=dict(t=6,b=6,l=6,r=6), paper_bgcolor='rgba(0,0,0,0)', font_color='#e6eef2', legend=dict(orientation="h"))
    st.plotly_chart(fig_b, use_container_width=True)

with col_a:
    st.markdown("<div class='card'><b>Simulated (After)</b></div>", unsafe_allow_html=True)
    fig_a = go.Figure(data=[go.Pie(labels=list(after_vals.keys()), values=list(after_vals.values()), hole=0.45, textinfo='label+percent')])
    fig_a.update_layout(margin=dict(t=6,b=6,l=6,r=6), paper_bgcolor='rgba(0,0,0,0)', font_color='#e6eef2', legend=dict(orientation="h"))
    st.plotly_chart(fig_a, use_container_width=True)

with col_s:
    st.markdown("<div class='card' style='text-align:center;'><div class='subtle'>Current Green Score</div><div class='metric-big'>{}</div><hr /><div class='subtle'>Estimated After Score</div><div style='font-size:28px; font-weight:800; color:#00d4aa;'>{}</div></div>".format(current_score, est_score), unsafe_allow_html=True)
    delta = est_score - current_score
    if delta > 0:
        st.success(f"Projected +{delta:.1f} points")
    elif delta < 0:
        st.error(f"Projected {delta:.1f} points")
    else:
        st.info("No change projected")

st.markdown("---")

# -------------------------
# Before vs After bar comparison
# -------------------------
st.markdown("<div class='card'><b>Comparison: Before vs After (kg CO₂ / mo)</b>", unsafe_allow_html=True)
cats = list(before_vals.keys())
before_list = [before_vals[c] for c in cats]
after_list = [after_vals[c] for c in cats]
fig_cmp = go.Figure()
fig_cmp.add_trace(go.Bar(name="Before", x=cats, y=before_list))
fig_cmp.add_trace(go.Bar(name="After", x=cats, y=after_list))
fig_cmp.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e6eef2', legend=dict(orientation="h"))
st.plotly_chart(fig_cmp, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Quick summary and applied scenario info
# -------------------------
st.markdown("<div style='margin-top:12px; display:flex; gap:20px; align-items:center;'>", unsafe_allow_html=True)
st.markdown(f"<div class='small-muted'><b>Active scenario:</b> {st.session_state.get('applied_scenario','None')}</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Tip: Press 'Apply' on a scenario to see results instantly. You can later implement multiple changes in real life and re-run Analyzer to record actual savings.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Optional debug (you can comment this out)
if st.button("Toggle debug inputs", key="toggle_debug_inputs"):
    st.session_state._show_sim_debug = not st.session_state.get("_show_sim_debug", False)

if st.session_state.get("_show_sim_debug"):
    st.markdown("### DEBUG: Derived inputs (used by simulator)")
    st.json(inputs)
    st.markdown("### RAW last_result (from Analyzer)")
    st.json(last_result)
