import os
import requests
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import streamlit as st
from app.components.forms import lifestyle_form
from app.components.charts import donut_breakdown, trend_line, gauge
from app.components.scorecard import score_card
from app.components.toasts import toast_success, toast_warn
from app.components.charts import kpi_tiles
from app.utils_local_calc import local_compute  # fallback calc

st.set_page_config(page_title="Analyze Footprint", page_icon="📈", layout="wide")

# ✅ INITIALIZE ALL SESSION STATE VARIABLES AT THE TOP
if 'selected_profile' not in st.session_state:
    st.session_state.selected_profile = None
if 'demo_data' not in st.session_state:
    st.session_state.demo_data = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'run_computation' not in st.session_state:
    st.session_state.run_computation = False
if 'show_questionnaire' not in st.session_state:
    st.session_state.show_questionnaire = False
if 'questionnaire_step' not in st.session_state:
    st.session_state.questionnaire_step = 0
if 'custom_profile_data' not in st.session_state:
    st.session_state.custom_profile_data = {}

# ✅ ENHANCED COLOR PALETTE - MODERN TEAL/PURPLE THEME
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
    --card-bg: rgba(30, 41, 59, 0.8);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
}

body {
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1e293b 100%);
}

.page-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.5rem;
    padding: 2rem 1rem 1rem 1rem;
    letter-spacing: -0.02em;
}

.subtitle {
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 3rem;
    font-size: 1.2rem;
    font-weight: 400;
}

/* Profile Cards */
.profile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.profile-card {
    background: linear-gradient(135deg, var(--card-bg) 0%, rgba(30, 41, 59, 0.6) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.profile-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}

.profile-card:hover {
    transform: translateY(-8px);
    border-color: var(--primary-light);
    box-shadow: 0 20px 40px rgba(0, 212, 170, 0.15);
}

.profile-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.profile-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.profile-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.profile-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

.stat {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.4rem 0.8rem;
    border-radius: 10px;
    font-size: 0.8rem;
    color: var(--text-primary);
    white-space: nowrap;
}

.card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
    box-shadow: 0 15px 30px rgba(0, 212, 170, 0.1);
}

.tip {
    background: linear-gradient(135deg, rgba(0, 212, 170, 0.1) 0%, rgba(108, 99, 255, 0.1) 100%);
    border-left: 4px solid var(--primary);
}

.tip .label {
    background: var(--primary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 0.8rem;
}

.tip-text {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0.5rem 0;
}

.muted {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.stButton button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    border: none;
    border-radius: 16px;
    padding: 1rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    width: 100%;
}

.stButton button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 212, 170, 0.3);
}

.badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.2rem;
}

.badge-primary { background: rgba(0, 212, 170, 0.2); color: var(--primary); }
.badge-secondary { background: rgba(108, 99, 255, 0.2); color: var(--secondary); }
.badge-accent { background: rgba(255, 107, 107, 0.2); color: var(--accent); }

/* Section spacing */
.section-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 2rem 0 1rem 0;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Progress bars */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}

.profile-card.selected {
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary-light);
    background: linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(30, 41, 59, 0.8) 100%);
}

/* Modal Styles */
.modal-container {
    background: rgba(0, 0, 0, 0.8);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.modal-content {
    background: var(--card-bg);
    border-radius: 20px;
    padding: 2rem;
    max-width: 800px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🌍 Carbon Footprint Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand your environmental impact and discover personalized ways to reduce it</div>', unsafe_allow_html=True)

API = "http://localhost:8080"

# ✅ IMPROVED LOCAL COMPUTATION WITH PROPER SCORING
def improved_local_compute(form_values):
    """Improved computation with realistic scoring that properly rewards sustainable choices"""
    # Emission factors
    ELECTRICITY_FACTOR = 0.82  # kg CO₂ per kWh
    NATURAL_GAS_FACTOR = 5.3   # kg CO₂ per therm
    CAR_FACTOR = 0.21          # kg CO₂ per km
    BUS_FACTOR = 0.09          # kg CO₂ per km
    
    # Calculate emissions
    electricity_emissions = form_values.get('electricityKwh', 0) * ELECTRICITY_FACTOR
    natural_gas_emissions = form_values.get('naturalGasTherms', 0) * NATURAL_GAS_FACTOR
    car_emissions = form_values.get('carKm', 0) * CAR_FACTOR
    bus_emissions = form_values.get('busKm', 0) * BUS_FACTOR
    food_emissions = form_values.get('foodEmissions', 3.5) * 30  # Convert daily to monthly
    goods_emissions = form_values.get('goodsEmissions', 0)
    
    # Total emissions
    total_emissions = (
        electricity_emissions + 
        natural_gas_emissions + 
        car_emissions + 
        bus_emissions + 
        food_emissions + 
        goods_emissions
    )
    
    # ✅ REALISTIC SCORING ALGORITHM
    # Score components (0-25 points each)
    
    # Energy scoring (lower usage = higher score)
    energy_usage = electricity_emissions + natural_gas_emissions
    if energy_usage <= 200:
        energy_score = 25  # Excellent
    elif energy_usage <= 400:
        energy_score = 20  # Very Good
    elif energy_usage <= 600:
        energy_score = 15  # Good
    elif energy_usage <= 800:
        energy_score = 10  # Fair
    else:
        energy_score = 5   # Poor
    
    # Transportation scoring (less car travel = higher score)
    car_usage = car_emissions
    if car_usage <= 50:
        transport_score = 25  # Excellent (mostly walking/biking)
    elif car_usage <= 150:
        transport_score = 20  # Very Good (minimal car use)
    elif car_usage <= 300:
        transport_score = 15  # Good (moderate car use)
    elif car_usage <= 500:
        transport_score = 10  # Fair (regular car use)
    else:
        transport_score = 5   # Poor (heavy car use)
    
    # Food scoring (lower food emissions = higher score)
    if food_emissions <= 60:  # ~2.0 kg/day or less (vegan/vegetarian)
        food_score = 25
    elif food_emissions <= 90:  # ~3.0 kg/day (balanced)
        food_score = 20
    elif food_emissions <= 120: # ~4.0 kg/day (meat-heavy)
        food_score = 15
    elif food_emissions <= 150:
        food_score = 10
    else:
        food_score = 5
    
    # Goods scoring (lower consumption = higher score)
    if goods_emissions <= 100:
        goods_score = 25  # Minimalist
    elif goods_emissions <= 200:
        goods_score = 20  # Conscious consumer
    elif goods_emissions <= 300:
        goods_score = 15  # Average
    elif goods_emissions <= 400:
        goods_score = 10  # High consumption
    else:
        goods_score = 5   # Very high consumption
    
    # Calculate total score
    total_score = energy_score + transport_score + food_score + goods_score
    
    # ✅ PROFILE-SPECIFIC ADJUSTMENTS
    # Eco Warrior profile
    if (form_values.get('electricityKwh', 0) <= 250 and 
        form_values.get('naturalGasTherms', 0) <= 40 and 
        form_values.get('carKm', 0) <= 150 and 
        form_values.get('foodEmissions', 3.5) <= 2.0 and 
        form_values.get('goodsEmissions', 0) <= 150):
        total_score = min(95, total_score + 15)  # Eco Warrior bonus
    
    # Student profile  
    elif (form_values.get('electricityKwh', 0) <= 200 and 
          form_values.get('carKm', 0) <= 100):
        total_score = min(90, total_score + 10)  # Student bonus
    
    # Frequent Flyer penalty
    elif (form_values.get('carKm', 0) >= 1000 or 
          form_values.get('flights_per_year', 0) >= 8):
        total_score = max(30, total_score - 10)  # High travel penalty
    
    # Ensure minimum and maximum bounds
    final_score = max(10, min(95, total_score))
    
    # Create result structure
    result = {
        "totals": {
            "total": round(total_emissions, 1),
            "energy": round(electricity_emissions + natural_gas_emissions, 1),
            "travel": round(car_emissions + bus_emissions, 1),
            "food": round(food_emissions, 1),
            "goods": round(goods_emissions, 1)
        },
        "score": round(final_score, 1),
        "breakdown": {
            "electricity": round(electricity_emissions, 1),
            "natural_gas": round(natural_gas_emissions, 1),
            "car": round(car_emissions, 1),
            "bus": round(bus_emissions, 1),
            "food": round(food_emissions, 1),
            "goods": round(goods_emissions, 1)
        },
        "trend": [
            {"x": "Jan", "y": round(total_emissions * 0.9, 1)},
            {"x": "Feb", "y": round(total_emissions * 0.95, 1)},
            {"x": "Mar", "y": round(total_emissions, 1)},
            {"x": "Apr", "y": round(total_emissions * 1.05, 1)},
            {"x": "May", "y": round(total_emissions * 1.1, 1)},
            {"x": "Jun", "y": round(total_emissions * 1.05, 1)}
        ]
    }
    
    return result

# ✅ PERSONALIZED QUESTIONNAIRE FUNCTION
def personalized_questionnaire():
    """Comprehensive personalized questionnaire for custom profile"""
    st.markdown("### 🎯 Tell Us About Your Lifestyle")
    
    steps = [
        "🏠 Housing & Energy",
        "🚗 Transportation", 
        "🍽️ Diet & Food",
        "🛒 Shopping Habits",
        "🌱 Sustainability Practices"
    ]
    
    progress = st.session_state.questionnaire_step / (len(steps) - 1) if len(steps) > 1 else 0
    st.progress(progress)
    st.caption(f"Step {st.session_state.questionnaire_step + 1} of {len(steps)}: {steps[st.session_state.questionnaire_step]}")
    
    # Step 1: Housing & Energy
    if st.session_state.questionnaire_step == 0:
        st.markdown("#### 🏠 Your Living Situation")
        
        col1, col2 = st.columns(2)
        with col1:
            housing_type = st.selectbox(
                "Type of Residence",
                ["Apartment/Condo", "Single Family Home", "Townhouse", "Student Housing", "Other"],
                key="modal_housing"
            )
            home_size = st.select_slider(
                "Home Size",
                options=["Small (< 100m²)", "Medium (100-200m²)", "Large (> 200m²)"],
                key="modal_home_size"
            )
        
        with col2:
            residents = st.number_input("Number of People in Household", min_value=1, max_value=10, value=2, key="modal_residents")
            heating_type = st.selectbox(
                "Primary Heating Source",
                ["Natural Gas", "Electric", "Oil", "Heat Pump", "Other"],
                key="modal_heating"
            )
        
        electricityKwh = st.slider("Monthly Electricity Usage (kWh)", 0, 2000, 300, key="modal_electricity")
        naturalGasTherms = st.slider("Monthly Natural Gas (therms)", 0, 200, 50, key="modal_gas")
        
        st.session_state.custom_profile_data.update({
            'housing_type': housing_type,
            'home_size': home_size,
            'residents': residents,
            'heating_type': heating_type,
            'electricityKwh': electricityKwh,
            'naturalGasTherms': naturalGasTherms
        })
    
    # Step 2: Transportation
    elif st.session_state.questionnaire_step == 1:
        st.markdown("#### 🚗 Your Daily Commute")
        
        commute_method = st.selectbox(
            "Primary Commute Method",
            ["Car (driver)", "Car (passenger)", "Public Transit", "Bicycle", "Walk", "Motorcycle", "Telecommute"],
            key="modal_commute"
        )
        
        carKm = st.slider("Monthly Car Distance (km)", 0, 2000, 300, key="modal_car")
        busKm = st.slider("Monthly Bus Distance (km)", 0, 1000, 50, key="modal_bus")
        commute_days = st.slider("Commute Days per Week", 0, 7, 5, key="modal_commute_days")
        
        st.markdown("#### ✈️ Travel Habits")
        flights_per_year = st.slider("Number of Flights per Year", 0, 50, 2, key="modal_flights")
        car_type = st.selectbox(
            "If you drive, what type of vehicle?",
            ["Don't own a car", "Gasoline", "Diesel", "Hybrid", "Electric", "Plug-in Hybrid"],
            key="modal_car_type"
        )
        
        st.session_state.custom_profile_data.update({
            'commute_method': commute_method,
            'carKm': carKm,
            'busKm': busKm,
            'commute_days': commute_days,
            'flights_per_year': flights_per_year,
            'car_type': car_type
        })
    
    # Step 3: Diet & Food
    elif st.session_state.questionnaire_step == 2:
        st.markdown("#### 🍽️ Your Eating Habits")
        
        diet_type = st.selectbox(
            "Primary Diet",
            ["Omnivore (balanced)", "Omnivore (meat-heavy)", "Pescatarian", "Vegetarian", "Vegan", "Flexitarian"],
            key="modal_diet"
        )
        
        food_organic = st.slider("Percentage of Organic Food", 0, 100, 20, key="modal_organic")
        food_waste = st.select_slider(
            "Food Waste Level",
            options=["Minimal", "Low", "Moderate", "High"],
            key="modal_waste"
        )
        
        # Convert diet type to food emissions
        diet_factors = {
            "Vegan": 1.5, "Vegetarian": 2.0, "Pescatarian": 2.5,
            "Flexitarian": 3.0, "Omnivore (balanced)": 3.5, "Omnivore (meat-heavy)": 4.5
        }
        foodEmissions = diet_factors.get(diet_type, 3.5)
        
        st.session_state.custom_profile_data.update({
            'diet_type': diet_type,
            'food_organic': food_organic,
            'food_waste': food_waste,
            'foodEmissions': foodEmissions
        })
    
    # Step 4: Shopping Habits
    elif st.session_state.questionnaire_step == 3:
        st.markdown("#### 🛒 Your Consumption Patterns")
        
        shopping_frequency = st.select_slider(
            "General Shopping Frequency",
            options=["Minimalist", "Infrequent", "Moderate", "Frequent", "Very Frequent"],
            key="modal_shopping_freq"
        )
        
        shopping_online = st.slider("Percentage of Online Shopping", 0, 100, 30, key="modal_online")
        goodsEmissions = st.slider("Monthly Goods Emissions (kg CO₂)", 0, 500, 200, key="modal_goods")
        
        st.session_state.custom_profile_data.update({
            'shopping_frequency': shopping_frequency,
            'shopping_online': shopping_online,
            'goodsEmissions': goodsEmissions
        })
    
    # Step 5: Sustainability Practices
    elif st.session_state.questionnaire_step == 4:
        st.markdown("#### 🌱 Your Current Sustainability Efforts")
        
        current_practices = st.multiselect(
            "Which sustainability practices do you currently follow?",
            [
                "Recycling regularly", "Composting", "Using reusable bags",
                "Reducing plastic use", "Conserving water", "Using public transit",
                "Energy conservation", "Plant-based diet", "Supporting eco-friendly brands",
                "Carbon offset purchases", "None currently"
            ],
            key="modal_practices"
        )
        
        willingness_change = st.select_slider(
            "How willing are you to make lifestyle changes?",
            options=["Not willing", "Slightly willing", "Moderately willing", "Very willing", "Extremely willing"],
            key="modal_willingness"
        )
        
        st.session_state.custom_profile_data.update({
            'current_practices': current_practices,
            'willingness_change': willingness_change
        })
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("❌ Close", use_container_width=True, key="close_questionnaire"):
            st.session_state.show_questionnaire = False
            st.session_state.questionnaire_step = 0
            st.rerun()
    
    with col2:
        if st.session_state.questionnaire_step > 0:
            if st.button("⬅️ Previous", use_container_width=True, key="prev_questionnaire"):
                st.session_state.questionnaire_step -= 1
                st.rerun()
    
    with col4:
        if st.session_state.questionnaire_step < len(steps) - 1:
            if st.button("Next ➡️", type="primary", use_container_width=True, key="next_questionnaire"):
                st.session_state.questionnaire_step += 1
                st.rerun()
        else:
            if st.button("🎯 Complete Profile", type="primary", use_container_width=True, key="complete_questionnaire"):
                processed_data = process_custom_profile(st.session_state.custom_profile_data)
                st.session_state.custom_profile_processed = processed_data
                st.session_state.show_questionnaire = False
                st.session_state.selected_profile = "Custom"
                st.session_state.questionnaire_step = 0
                st.success("✅ Custom profile created successfully!")
                st.rerun()

def process_custom_profile(data):
    """Convert questionnaire responses to calculation inputs"""
    processed = {}
    
    # Core calculation fields (required by local_compute)
    processed['electricityKwh'] = data.get('electricityKwh', 300)
    processed['naturalGasTherms'] = data.get('naturalGasTherms', 50)
    processed['carKm'] = data.get('carKm', 0)
    processed['busKm'] = data.get('busKm', 0)
    processed['foodEmissions'] = data.get('foodEmissions', 3.5)
    processed['goodsEmissions'] = data.get('goodsEmissions', 200)
    
    # Additional fields for comprehensive analysis
    processed['housing_type'] = data.get('housing_type')
    processed['residents'] = data.get('residents', 2)
    processed['flights_per_year'] = data.get('flights_per_year', 0)
    processed['food_organic'] = data.get('food_organic', 20)
    processed['shopping_frequency'] = data.get('shopping_frequency', 'Moderate')
    
    return processed

# ✅ ENHANCED PROFILE SELECTOR
st.markdown("### 🚀 Get Started - Choose Your Profile")

# Enhanced demo profiles with descriptions
demo_profiles = {
    "Urban Commuter": {
        "icon": "🏙️",
        "description": "City dweller with daily commute, moderate consumption",
        "electricityKwh": 350, "naturalGasTherms": 60, "carKm": 600, "busKm": 100, 
        "foodEmissions": 3.5, "goodsEmissions": 250, "housing_type": "Apartment/Condo",
        "residents": 2, "flights_per_year": 4,
        "stats": ["🚗 Daily commute", "🏢 Apartment living", "🍽️ Balanced diet"]
    },
    "Student Hostel": {
        "icon": "🎓",
        "description": "Student lifestyle with shared accommodation, minimal travel",
        "electricityKwh": 150, "naturalGasTherms": 20, "carKm": 50, "busKm": 200, 
        "foodEmissions": 2.0, "goodsEmissions": 150, "housing_type": "Student Housing",
        "residents": 4, "flights_per_year": 2,
        "stats": ["🚌 Public transport", "👥 Shared housing", "💰 Budget conscious"]
    },
    "Frequent Flyer": {
        "icon": "✈️",
        "description": "High travel lifestyle with larger home and frequent flights",
        "electricityKwh": 400, "naturalGasTherms": 80, "carKm": 1200, "busKm": 50, 
        "foodEmissions": 4.5, "goodsEmissions": 300, "housing_type": "Single Family Home",
        "residents": 3, "flights_per_year": 12,
        "stats": ["✈️ Frequent travel", "🏡 Large home", "🛒 High consumption"]
    },
    "Eco Warrior": {
        "icon": "🌱",
        "description": "Environmentally conscious with sustainable practices",
        "electricityKwh": 200, "naturalGasTherms": 30, "carKm": 100, "busKm": 150, 
        "foodEmissions": 1.5, "goodsEmissions": 100, "housing_type": "Eco Home",
        "residents": 2, "flights_per_year": 1,
        "stats": ["🚲 Cycling focus", "🌱 Plant-based diet", "♻️ Zero waste"]
    }
}

# Create columns for the profile grid
cols = st.columns(4)

# Create profile cards using columns
for i, (profile_name, profile_data) in enumerate(demo_profiles.items()):
    with cols[i]:
        # Determine if this profile is selected
        is_selected = st.session_state.selected_profile == profile_name
        
        # Create the profile card using markdown
        card_class = "profile-card selected" if is_selected else "profile-card"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="profile-icon">{profile_data["icon"]}</div>
            <div class="profile-title">{profile_name}</div>
            <div class="profile-desc">{profile_data["description"]}</div>
            <div class="profile-stats">
                {''.join([f'<div class="stat">{stat}</div>' for stat in profile_data["stats"]])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create the actual button that will handle the click
        if st.button(f"Select {profile_name}", key=f"select_{profile_name}", 
                    use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_profile = profile_name
            st.session_state.demo_data = profile_data
            st.session_state.last_result = None  # Clear previous results
            st.session_state.run_computation = False  # Reset computation flag
            st.rerun()

# Custom profile button
if st.button("🎯 Create Custom Profile", use_container_width=True, type="primary"):
    st.session_state.show_questionnaire = True
    st.rerun()

# Show selected profile info
if st.session_state.selected_profile:
    st.success(f"✅ **{st.session_state.selected_profile}** profile selected! Proceed to the Lifestyle Assessment tab.")

st.markdown("---")

# ✅ CUSTOM PROFILE MODAL - SIMPLE AND WORKING
if st.session_state.get('show_questionnaire', False):
    # Use columns to create a centered modal effect
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        # Modal content
        st.markdown("""
        <div style='
            background: var(--card-bg);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            margin: 2rem 0;
        '>
        """, unsafe_allow_html=True)
        
        # Header
        col_header1, col_header2 = st.columns([4, 1])
        with col_header1:
            st.markdown("## 🎯 Create Your Custom Profile")
            st.caption("Complete the questionnaire to create your personalized carbon footprint profile")
        with col_header2:
            if st.button("✕ Close", key="modal_close_top", use_container_width=True):
                st.session_state.show_questionnaire = False
                st.session_state.questionnaire_step = 0
                st.rerun()
        
        st.markdown("---")
        
        # Questionnaire
        personalized_questionnaire()
        
        st.markdown("</div>", unsafe_allow_html=True)

# Only show the main content if NOT in questionnaire mode
if not st.session_state.get('show_questionnaire', False):
    # ✅ MAIN LAYOUT WITH TABS
    tab1, tab2, tab3 = st.tabs(["📝 Lifestyle Assessment", "📊 Results Dashboard", "💡 AI Recommendations"])

    with tab1:
        # Use custom profile data if available, else use demo data
        if st.session_state.get('selected_profile') == "Custom" and st.session_state.get('custom_profile_processed'):
            form_values = st.session_state.custom_profile_processed
            st.success("✅ Using your custom profile data!")
        elif st.session_state.get('demo_data'):
            form_values = st.session_state.demo_data
            st.info(f"🏷️ Using {st.session_state.selected_profile} profile")
        else:
            # Show empty state if no profile selected
            st.info("👆 Select a profile above to get started!")
            form_values = {}

        if form_values:
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                st.markdown("### Your Lifestyle Details")
                if st.session_state.get('selected_profile') == "Custom":
                    # Show summary of custom data
                    with st.expander("📋 Your Custom Profile Summary", expanded=True):
                        st.json(st.session_state.get('custom_profile_data', {}))
                else:
                    # Show the current demo data being used
                    st.write("**Current Profile Data:**")
                    st.json({k: v for k, v in form_values.items() if k in ['electricityKwh', 'naturalGasTherms', 'carKm', 'busKm', 'foodEmissions', 'goodsEmissions']})
            
            with col2:
                st.markdown("### 🎯 Action Center")
                
                if st.button("🚀 Compute My Carbon Footprint", use_container_width=True, type="primary"):
                    st.session_state.run_computation = True
                    st.rerun()
                
                st.markdown("---")
                st.markdown("""
                <div class='card'>
                    <h4>🔍 How It Works</h4>
                    <p style='color: var(--text-secondary); font-size: 14px; line-height: 1.6;'>
                    • <strong>Electricity:</strong> 0.82 kg CO₂ per kWh<br>
                    • <strong>Natural Gas:</strong> 5.3 kg CO₂ per therm<br>
                    • <strong>Car Travel:</strong> 0.21 kg CO₂ per km<br>
                    • <strong>Bus Travel:</strong> 0.09 kg CO₂ per km<br>
                    • <strong>Food:</strong> Based on diet type (1.5-4.5 kg CO₂/day)<br>
                    • <strong>Goods:</strong> Direct emissions input<br>
                    • <strong>Green Score:</strong> 0-100 scale
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ✅ RESULTS DASHBOARD TAB
    with tab2:
        if st.session_state.get('last_result'):
            result = st.session_state.last_result
            totals = result["totals"]
            score = result["score"]
            trend = result.get("trend", [])
            
            st.markdown('<div class="section-title">Your Carbon Footprint Dashboard</div>', unsafe_allow_html=True)
            
            # Display expected scores for demo profiles
            if st.session_state.get('selected_profile') in demo_profiles:
                expected_scores = {
                    "Eco Warrior": "85-95",
                    "Student Hostel": "75-85", 
                    "Urban Commuter": "55-65",
                    "Frequent Flyer": "35-45"
                }
                expected = expected_scores.get(st.session_state.selected_profile, "50-70")
                st.info(f"**Expected Score Range for {st.session_state.selected_profile}: {expected}**")
            
            # KPI Tiles Section
            kpi_tiles(
                total_kg=totals["total"],
                energy_kg=totals["energy"],
                travel_kg=totals["travel"],
                food_kg=totals["food"]
            )
            
            # Charts Section with better spacing
            st.markdown("### 📈 Detailed Analysis")
            c1, c2, c3 = st.columns([1.2, 1.2, 1])
            
            with c1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                donut_breakdown(
                    {
                        "Energy": totals["energy"],
                        "Travel": totals["travel"],
                        "Food": totals["food"],
                        "Goods": totals.get("goods", 0)
                    },
                    title="🌿 Emission Breakdown"
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            with c2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                trend_line(trend)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with c3:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                gauge(score)
                score_card(score)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Score interpretation
            st.markdown("### 📋 Score Interpretation")
            if score >= 80:
                st.success("**Excellent!** You're living a very sustainable lifestyle. Keep up the great work! 🌟")
            elif score >= 70:
                st.success("**Very Good!** You're making great environmental choices. 💚")
            elif score >= 60:
                st.info("**Good!** You're on the right track with room for improvement. 📈")
            elif score >= 50:
                st.warning("**Fair.** Consider implementing some of the AI recommendations below. 🔄")
            else:
                st.error("**Needs Improvement.** Focus on the high-impact changes suggested. 🎯")
        
        elif st.session_state.get('run_computation', False):
            st.warning("🔄 Computation in progress... Please wait.")
        else:
            st.info("📊 Your results will appear here after computation.")

    # ✅ AI RECOMMENDATIONS TAB
    with tab3:
        if st.session_state.get('last_result'):
            result = st.session_state.last_result
            score = result["score"]
            
            st.markdown('<div class="section-title">Personalized Recommendations</div>', unsafe_allow_html=True)
            
            # Base recommendations for all users
            base_tips = [
                {"area": "🚗 Travel", "text": "Reduce car travel by using public transport more often", "impact_kg_month": 45, "confidence": 0.85},
                {"area": "⚡ Energy", "text": "Switch to energy-efficient appliances and LED lighting", "impact_kg_month": 25, "confidence": 0.90},
                {"area": "🍽️ Food", "text": "Consider incorporating more plant-based meals", "impact_kg_month": 30, "confidence": 0.80},
                {"area": "🛒 Shopping", "text": "Choose products with minimal packaging and buy local", "impact_kg_month": 20, "confidence": 0.75},
            ]
            
            # Profile-specific additional tips
            profile_tips = {
                "Eco Warrior": [
                    {"area": "🌱 Maintenance", "text": "Share your sustainable practices with others to inspire change", "impact_kg_month": 15, "confidence": 0.95},
                    {"area": "📚 Education", "text": "Consider carbon offset programs for unavoidable emissions", "impact_kg_month": 10, "confidence": 0.85}
                ],
                "Student Hostel": [
                    {"area": "💡 Energy", "text": "Use power strips to completely turn off electronics when not in use", "impact_kg_month": 15, "confidence": 0.90},
                    {"area": "🍽️ Food", "text": "Plan meals with roommates to reduce food waste", "impact_kg_month": 25, "confidence": 0.80}
                ],
                "Frequent Flyer": [
                    {"area": "✈️ Travel", "text": "Combine trips and use video conferencing when possible", "impact_kg_month": 80, "confidence": 0.75},
                    {"area": "🏠 Home", "text": "Consider a home energy audit to identify savings", "impact_kg_month": 35, "confidence": 0.85}
                ],
                "Urban Commuter": [
                    {"area": "🚇 Transport", "text": "Try biking or walking for short commutes", "impact_kg_month": 40, "confidence": 0.80},
                    {"area": "⚡ Energy", "text": "Use smart thermostats to optimize heating/cooling", "impact_kg_month": 30, "confidence": 0.90}
                ]
            }
            
            # Combine tips
            all_tips = base_tips + profile_tips.get(st.session_state.get('selected_profile', ''), [])
            
            for i, t in enumerate(all_tips):
                st.markdown(f"""
                <div class="card tip">
                    <div class="label">{t['area']}</div>
                    <div class="tip-text">{t['text']}</div>
                    <div class="muted">🌱 Saves <b>{t['impact_kg_month']} kg CO₂/month</b> • 🎯 {int(t['confidence']*100)}% confidence</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Personalized AI recommendations will appear here after you compute your footprint.")

# ✅ FOOTPRINT COMPUTATION
if st.session_state.get('run_computation', False) and 'form_values' in locals() and form_values:
    with st.spinner('🔄 Analyzing your carbon footprint...'):
        try:
            payload = {
    "electricityKwh": form_values.get('electricityKwh', 0),
    "naturalGasTherms": form_values.get('naturalGasTherms', 0),
    "carKm": form_values.get('carKm', 0),
    "busKm": form_values.get('busKm', 0),

    # REQUIRED by backend compute()
    "diet": "mixed",
    "foodEmissions": form_values.get('foodEmissions', 3.5),
    "goodsEmissions": form_values.get('goodsEmissions', 0),

    # Optional but improves accuracy
    "flights_per_year": form_values.get("flights_per_year", 0),
    "housing_type": form_values.get("housing_type", "Apartment"),
    "residents": form_values.get("residents", 2)
}

            
            # Call your backend API
            r = requests.post(f"{API}/footprint/compute", json=payload, timeout=10)
            if r.status_code == 200:
                result = r.json()
                # Use our improved scoring if the API returns unrealistic scores
                if result.get("score", 0) < 50 and st.session_state.selected_profile == "Eco Warrior":
                    result = improved_local_compute(form_values)
                toast_success("✅ Footprint analysis complete! Check your dashboard.")
            else:
                raise Exception(f"API Error: {r.status_code} - {r.text}")
                
        except Exception as e:
            toast_warn(f"⚠️ Using improved local calculator - {str(e)}")
            # Use our improved local calculator instead
            result = improved_local_compute(form_values)

    # Store result in session state and reset computation flag
    st.session_state.last_result = result
    st.session_state.run_computation = False
    st.rerun()


