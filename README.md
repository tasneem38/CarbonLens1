# 🌍 CarbonLens — Personal Carbon Footprint Analyzer

### *Track. Understand. Reduce. — Powered by AI.*

CarbonLens is a smart, interactive carbon-footprint analysis platform that helps users understand their environmental impact and take meaningful actions to reduce it. Designed with **visual dashboards**, **AI-generated recommendations**, and a **story-driven user experience**, CarbonLens makes climate action **simple**, **personal**, and **actionable**.

---

## 🚀 Features

### **🌱 Lifestyle Analyzer**
- Calculate total CO₂ emissions (kg/month) from simple lifestyle inputs
- Category-wise breakdown (Energy, Travel, Food, Goods)
- Personalized Green Score (0–100)
- Trend forecast for the next 6 months

### **📊 Interactive Dashboard**
- Beautiful Streamlit dashboard with donut charts and trend graphs
- Energy/Travel/Food KPIs with gauge meters
- Green Score interpretation ranges
- Profile-based expected score comparisons

### **🎯 Personalized Profiles**
- **Preset Profiles**: Urban Commuter, Student Hostel, Frequent Flyer, Eco Warrior
- **Custom Profile Builder**: 5-step questionnaire covering housing, transportation, food, shopping, and sustainability behavior

### **🤖 AI Recommendations**
- Powered by **Groq (Llama-3.1 models)** with fallback local logic
- High-impact personalized tips with CO₂ savings estimates
- Confidence scoring for each recommendation
- Context-aware responses using full chat history

### **💬 CarbonLens Chat Assistant**
- Neon-themed conversational AI assistant
- Explains scores and suggests improvements
- Expands tips into actionable checklists
- Functions as a personal sustainability coach

### **📚 Why-It-Matters Page (Story Mode)**
- Emotional storytelling with global climate statistics
- Animated climate visuals and impact data
- Educational content on CO₂ rise and extreme weather
- Clear call-to-action to start tracking

### **🔍 Data Assumptions & Sources**
- Transparent emission factors displayed in clean cards
- Electricity: **0.82 kg/kWh** (CEA Baseline v18)
- Travel: Car/Bus/Train factors (IEA/MoEFCC)
- Food: **120/160/216 kg/mo** (FAO/IPCC)
- Source tags and methodology disclaimers

### **🗂️ SQLite Leaderboard**
- Anonymous footprint runs and score-based ranking
- (Optional feature - can be enabled/disabled)

---

## 🛠️ Tech Stack

### **Frontend**
- **Streamlit** - Modern UI with neon aesthetics
- Responsive cards, hover motion, gradients
- Modular tabs (Analyzer, Dashboard, AI)

### **Backend**
- **FastAPI** - Structured schemas with Pydantic validation
- **SQLAlchemy** - Database models and operations
- Clear service separation architecture

### **AI Integration**
- **Groq**: `llama-3.1-70b`, `llama-3.1-8b-instant`
- Custom logic for personalized recommendations
- Chat model with memory and automatic fallback

### **Database**
- **SQLite** with tables: `footprint_runs`, `leaderboard`, `users`

---

## 🧪 Installation & Setup

### **Prerequisites**
- Python 3.8+
- Groq API key (optional, for enhanced AI features)

### **1. Clone Repository**
git clone https://github.com/yourusername/carbonlens.git
cd carbonlens

### **2. Install Dependencies**
pip install -r requirements.txt

### **3. Environment Configuration**
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://127.0.0.1:8080

### **4. Start Backend Server**
cd backend
uvicorn main:app --reload --port 8080

### **5. Start Frontend Application**
streamlit run app/Home.py

### **6. Access Application**
Frontend: http://localhost:8501
Backend API: http://localhost:8080
API Documentation: http://localhost:8080/docs

## 🔌API Endpoints
### **Footprint Calculation**
http
POST /footprint/compute
Calculate CO₂ emissions from lifestyle data
Returns breakdown by category and Green Score

### **AI Recommendations**
http
POST /reco/generate
Generate personalized reduction recommendations
Supports both Groq AI and fallback logic

### **Chat Assistant**
http
POST /reco/chat
Conversational interface with chat memory
Context-aware sustainability coaching

## 🌟 Why CarbonLens?
CarbonLens turns climate awareness into daily action. Instead of overwhelming users with charts, it:
Personalizes climate impact understanding
Simplifies complex emissions data
Provides actionable guidance people can actually follow
Uses AI as a personal sustainability coach
Motivates behavioral change through storytelling
Builds climate awareness in an engaging way

**It isn't just a calculator — it's a platform to help people live greener lives.**

## 🤝 Contributing
We welcome contributions! Whether you're improving UI, backend logic, or AI quality:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

## 🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.

📄 Citation
If you use CarbonLens in your research or project, please cite:

CarbonLens - Personal Carbon Footprint Analyzer. 
Track. Understand. Reduce. — Powered by AI.
👥 Authors
tasneem38 - Initial work - YourUsername

## 🙏 Acknowledgments
Emission factors sourced from CEA, IEA, MoEFCC, FAO, and IPCC
UI inspiration from modern climate tech applications
Groq for providing fast LLM inference capabilities
