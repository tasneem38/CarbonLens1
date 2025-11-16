import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="CarbonLens — Personal CO₂ Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ Inject CSS with Animations
st.markdown("""
<style>
/* Full-page background */
body, html, .main, .block-container, .appview-container {
    min-height: 100vh;
    margin: 0;
    padding: 0;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)), 
                url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee') center/cover no-repeat fixed !important;
    background-attachment: fixed !important;
}

/* Hero container - Reduced min-height to tighten spacing */
.hero-container {
    min-height: 60vh;  /* Reduced from 80vh to bring buttons closer */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

/* Titles with Fade-in Animation */
.title {
    font-size: 54px;
    font-weight: 800;
    color: #e0f0d9;
    animation: fadeInUp 1.5s ease-out;
}

.tagline {
    font-size: 28px;
    font-weight: 600;
    color: #e0f0d9;
    margin-bottom: 20px;
    animation: fadeInUp 1.5s ease-out 0.3s both;
}

.subtitle {
    font-size: 18px;
    color: #c8d5ca;
    margin-bottom: 20px;  /* Reduced from 40px to further tighten spacing */
    animation: fadeInUp 1.5s ease-out 0.6s both;
}

/* Keyframe Animations */
@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ✅ BUTTON ROW - True Centered Flexbox */
.button-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 24px; /* controls space between buttons */
    margin-top: 10px;
    animation: fadeInUp 1.5s ease-out 0.9s both;
}

/* ✅ BUTTON STYLE - Increased padding and font size with Enhanced Hover */
button.custom-btn {
    background: linear-gradient(135deg, #00c853, #43a047);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 18px 36px;  /* Increased padding for larger box size */
    font-size: 18px;     /* Increased font size */
    transition: all 0.3s ease;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

button.custom-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

button.custom-btn:hover::before {
    left: 100%;
}

button.custom-btn:hover {
    transform: translateY(-4px) scale(1.05);
    background: linear-gradient(135deg, #66bb6a, #388e3c);
    box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.5);
}

/* Features Section */
.features-section {
    text-align: center;
    padding: 60px 20px 80px 20px;
    background: transparent !important;
    position: relative;
    z-index: 2;
    animation: fadeInUp 1.5s ease-out 1.2s both;
}

.features-section h2 {
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 40px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.features-grid {
    display: flex;
    gap: 28px;
    justify-content: center;
    align-items: stretch;
    flex-wrap: nowrap;
    padding: 20px;
    overflow-x: auto;
}

.feature-card {
    min-width: 280px;
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255,255,255,0.4);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 32px 24px;
    text-align: center;
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    flex-shrink: 0;
    transition: all 0.3s ease;
    animation: slideIn 1s ease-out both;
}

.feature-card:nth-child(1) { animation-delay: 1.5s; }
.feature-card:nth-child(2) { animation-delay: 1.7s; }
.feature-card:nth-child(3) { animation-delay: 1.9s; }
.feature-card:nth-child(4) { animation-delay: 2.1s; }

@keyframes slideIn {
    0% {
        opacity: 0;
        transform: translateX(-50px);
    }
    100% {
        opacity: 1;
        transform: translateX(0);
    }
}

.feature-card:hover {
    transform: translateY(-8px) scale(1.02);
    background: rgba(255, 255, 255, 0.3);
    box-shadow: 0 12px 32px rgba(109, 226, 141, 0.5);
    border: 1px solid rgba(109, 226, 141, 0.6);
}

.feature-card .icon {
    font-size: 44px;
    margin-bottom: 12px;
    color: #6de28d;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-10px);
    }
    60% {
        transform: translateY(-5px);
    }
}

.feature-card h4 {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #ffffff;
}

.feature-card p {
    font-size: 14px;
    color: #e8f5e9;
}
</style>
""", unsafe_allow_html=True)

# ✅ HERO SECTION with Emojis
st.markdown("""
<div class="hero-container">
    <div class="hero-content">
        <h1 class="title">🌍 CarbonLens 🌱</h1>
        <p class="tagline">Track. Reduce. Inspire. 🚀</p>
        <p class="subtitle">
            A dynamic way to understand your carbon footprint — powered by AI recommendations, 
            and actionable simulations. 💡
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ✅ BUTTONS (Centered Layout using 5 columns to center the 3 buttons)
col1, col2, col3, col4, col5 = st.columns(5)
with col2:
    if st.button("🔍 Start Footprint Analysis", key="analysis"):
        st.switch_page("pages/1_Analyze_Footprint.py")

with col3:
    if st.button("🛠 Try What-If Simulator", key="simulator"):
        st.switch_page("pages/3_Simulation_Scenarios.py")

with col4:
    if st.button("🏅 Leaderboard", key="leaderboard"):
        st.switch_page("pages/4_Leaderboard_and_Badges.py")

# ✅ FEATURES SECTION with Enhanced Emojis
st.markdown("""
<div class="features-section">
    <h2>Why CarbonLens? 🌟</h2>
    <div class="features-grid">
        <div class="feature-card">
            <div class="icon">🤖</div>
            <h4>AI-Driven Suggestions</h4>
            <p>Smart tips tailored to your lifestyle and habits. 🧠</p>
        </div>
        <div class="feature-card">
            <div class="icon">📊</div>
            <h4>Live Carbon Dashboard</h4>
            <p>Instant visualization across energy, travel, and food. 📈</p>
        </div>
        <div class="feature-card">
            <div class="icon">🎮</div>
            <h4>Gamified Challenges</h4>
            <p>Earn badges, climb the leaderboard, and inspire others. 🏆</p>
        </div>
        <div class="feature-card">
            <div class="icon">🧪</div>
            <h4>What-If Simulations</h4>
            <p>See CO₂ savings before lifestyle changes. 🔬</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
