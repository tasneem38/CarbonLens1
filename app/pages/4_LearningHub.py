import streamlit as st

st.set_page_config(page_title="Why It Matters", page_icon="🌍", layout="wide")

# ---------------------------------------------------------
# CSS STYLES
# ---------------------------------------------------------
st.markdown("""
<style>
:root {
    --neon1:#45f1a0;
    --neon2:#37b3f5;
    --muted:#94a3b8;
    --accent-red: #ff5f5f; /* For high impact text */
}

html, body, .block-container {
    background: linear-gradient(135deg, #0f172a, #0b1220) !important;
    color: white !important;
    font-family: Inter, system-ui;
}

.story-section {
    padding: 40px 0px;
    border-radius: 20px;
}

.big-title {
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, var(--neon1), var(--neon2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtle {
    color: var(--muted);
    font-size: 1.1rem;
    text-align: center;
    margin-top: -10px;
    margin-bottom: 30px;
}

.card {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    margin-bottom: 18px;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.card h3 {
    color: white;
    margin-bottom: 8px;
    font-size: 1.4rem;
}
.card p {
    color: var(--muted);
    font-size: 1rem;
    flex-grow: 1;
}

.warning {
    border-left: 4px solid #ff5f5f;
    padding-left: 20px;
}

.impact-point {
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}
.impact-point strong {
    color: var(--neon1);
    font-weight: 600;
}

.cta-btn {
    padding: 16px 28px;
    font-size: 1.1rem;
    color: white;
    border: none;
    border-radius: 14px;
    background: linear-gradient(135deg,var(--neon2),var(--neon1));
    cursor: pointer;
    font-weight: 700;
    transition: 0.25s;
}

.cta-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 18px rgba(70,255,200,0.4);
}

.stMetric > div:first-child {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 15px;
}
.stMetric label {
    font-size: 0.9rem !important;
    color: var(--muted) !important;
}
.stMetric .css-1hv607w { 
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--neon1) !important;
}

/* Custom styling for the Beach Metaphor block */
.beach-metaphor {
    background: rgba(15, 23, 42, 0.9);
    padding: 30px;
    border-radius: 18px;
    border: 2px solid var(--neon2);
    text-align: center;
    font-style: italic;
    font-size: 1.2rem;
    line-height: 1.8;
}
.beach-metaphor strong {
    color: var(--accent-red);
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# STORY SECTION 1 — The World Right Now
# ---------------------------------------------------------
st.markdown('<div class="story-section">', unsafe_allow_html=True)

st.markdown('<div class="big-title">The World Is Changing Faster Than We Are</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">And this story concerns all of us — including you.</div>', unsafe_allow_html=True)

# Refined Beach Metaphor block
st.markdown("""
<div class="beach-metaphor">
    Imagine you’re standing on a beach you’ve visited since childhood.<br>
    The waves are closer than you remember.<br>
    The air feels harsher.<br>
    The sky is hotter than it should be.
    <hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px auto;">
    This isn't imagination.
    It’s the world quietly reshaping itself — because of the <strong>carbon we emit every day</strong>.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STORY SECTION 2 — What’s Happening (Metrics & Consequence - IMPROVED NATIVE STYLE)
# ---------------------------------------------------------
st.markdown('<div class="story-section">', unsafe_allow_html=True)

st.markdown("### 🌡️ The Planet’s Vital Signs Are Changing")
st.markdown('<div class="subtle" style="margin-bottom: 20px;">Small numbers, huge consequences.</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="CO₂ in Atmosphere (ppm)", value="421", delta="Highest in millions of years")
with col2:
    st.metric(label="Global Temperature Rise", value="+1.2°C", delta="Tipping point in sight")
with col3:
    st.metric(label="Extreme Weather Disasters", value="780+", delta="Storms, fires, and floods annually")

# --- REPLACEMENT FOR THE RAW HTML BLOCK ---
st.markdown("<br>", unsafe_allow_html=True) # Add some spacing
with st.container(border=True):
    # Use a subheader for a clean, bold title
    st.subheader("❗ This is not abstract.")
    
    # Use st.write for the main paragraph
    st.write(
        """
        <p style='font-size: 1.15rem; color: #f0f0f0;'>
        A degree on a graph translates directly to homes lost, dreams interrupted, and families displaced.
        </p>
        """, 
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STORY SECTION 3 — Why Your Footprint Matters
# ---------------------------------------------------------
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🌍 Your Choices Are Your Power")
st.markdown('<div class="subtle">Your carbon footprint is the story of your everyday life.</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div class='impact-point'>
        <strong>✈️ How you travel:</strong> Flights, commuting, and car choice.
    </div>
    <div class='impact-point'>
        <strong>🍽️ How you eat:</strong> Meat consumption vs. plant-based meals.
    </div>
    <div class='impact-point'>
        <strong>🏠 How you live:</strong> Energy for cooling, heating, and household waste.
    </div>
    <div class='impact-point'>
        <strong>🛍️ What you buy:</strong> The lifespan and sourcing of your possessions.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    with st.container(border=True):
        st.subheader("Why Measure Your Impact?")
        st.info("Tracking your footprint is not about guilt. It’s about **clarity** and **empowerment**.")
        st.markdown("""
        It tells you precisely:
        * **Where** is your biggest impact?
        * **What** changes yield the largest reduction?
        
        Every choice you make sends a signal and contributes to the collective total.
        """)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# STORY SECTION 4 — What Happens If We Do Nothing
# ---------------------------------------------------------
st.markdown('<div class="story-section">', unsafe_allow_html=True)

st.markdown("## ⚠️ The Cost of Inaction")
st.markdown('<div class="subtle">If we continue on the current path, the world will fundamentally change for the worse.</div>', unsafe_allow_html=True)

col_warn1, col_warn2 = st.columns(2)

with col_warn1:
    st.markdown("""
    <div class="card warning">
    <b>🌡️ Deadly Heat Becomes Normal.</b><br>
    Cities across the globe will become dangerously hot for weeks each year, making outdoor life untenable.
    </div>
    <div class="card warning">
    <b>🔥 Wildfires Spread 3× Faster.</b><br>
    Forests that once protected us will turn into fuel, destroying homes and polluting air quality globally.
    </div>
    """, unsafe_allow_html=True)

with col_warn2:
    st.markdown("""
    <div class="card warning">
    <b>🌊 Coastal Displacement.</b><br>
    Rising seas will swallow coastlines, displacing an estimated 200–300 million people from megacities like Mumbai and Dhaka.
    </div>
    <div class="card warning">
    <b>🥀 Ecosystems Collapse.</b><br>
    Coral reefs die, essential crops fail, and food and clean water become scarcer and more expensive.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# STORY SECTION 5 — The Hopeful Part
# ---------------------------------------------------------
st.markdown('<div class="story-section">', unsafe_allow_html=True)

st.markdown("## 🌱 The Good News")

tab1, tab2 = st.tabs(["Individual Impact", "The Bigger Picture"])

with tab1:
    st.markdown("""
    ### Small Changes, Big Signals
    We are not powerless. Small changes—done consistently—reshape the future.

    <div class='card' style='margin-top:15px;'>
        <ul>
            <li>Diet: One plant-based day a week saves significant emissions.</li>
            <li>Energy: Switching to energy-efficient appliances or LED lighting.</li>
            <li>Commute: A public transit ride instead of driving (even once a week).</li>
            <li>Consumption: Repairing items instead of immediately replacing them.</li>
        </ul>
        <p style='margin-top:15px; color:white;'>These are not small acts. They are signals that, when multiplied by millions, change everything.</p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    ### Collective Momentum
    The biggest change comes when consumer demand drives industry.

    <div class='card' style='margin-top:15px;'>
        <p>Your individual choice creates a market signal for sustainable alternatives (electric vehicles, renewable energy, ethical supply chains).</p>
        <p>This pressure accelerates innovation and makes eco-friendly choices the new, affordable normal for everyone.</p>
        <p style='margin-top:15px; color:var(--neon2); font-weight:600;'>The future is built on millions of small, daily decisions.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# STORY SECTION 6 — CTA
# ---------------------------------------------------------
st.markdown('<div class="story-section" style="text-align:center;">', unsafe_allow_html=True)

st.markdown("### Ready to understand your own impact — and change it?")

# Use markdown for the button to apply the CSS class
st.markdown("""
<button class='cta-btn' onclick="window.location.href='pages/Analyze_Footprint'">
    Start Tracking Today
</button>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)