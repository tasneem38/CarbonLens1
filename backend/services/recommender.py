import os
import google.generativeai as genai
import yaml
from typing import List, Dict
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        test_response = model.generate_content("Hello")
        print("✅ Gemini AI configured successfully and working!")
        AI_ENABLED = True
    except Exception as e:
        print(f"❌ Gemini AI configuration failed: {e}")
        AI_ENABLED = False
else:
    print("⚠️ GEMINI_API_KEY not found in .env file")
    AI_ENABLED = False

def generate_ai_recommendations(inputs: dict) -> List[Dict]:
    """Generate AI-powered recommendations using Gemini"""
    
    if not AI_ENABLED:
        print("🔄 Using fallback recommendations (AI not enabled)")
        return generate_fallback_recommendations(inputs)
    
    try:
        # Prepare comprehensive context for AI
        total_emissions = inputs.get('energy_kg', 0) + inputs.get('travel_kg', 0) + inputs.get('food_kg', 0)
        
        context = f"""You are an expert carbon footprint advisor. Generate personalized carbon reduction recommendations based on this user data:

USER FOOTPRINT DATA (USE THESE EXACT NUMBERS):
- Total monthly emissions: {total_emissions} kg CO₂
- Energy: {inputs.get('energy_kg', 0)} kg CO₂ ({inputs.get('electricityKwh', 0)} kWh electricity, {inputs.get('naturalGasTherms', 0)} therms gas)
- Travel: {inputs.get('travel_kg', 0)} kg CO₂ ({inputs.get('carKm', 0)} km car, {inputs.get('busKm', 0)} km bus)
- Food: {inputs.get('food_kg', 0)} kg CO₂ (diet: {inputs.get('diet', 'mixed')})
- Goods: {inputs.get('goods_kg', 0)} kg CO₂

Generate 3-5 specific, actionable recommendations. For each, provide:
- Area (Energy, Travel, Food, Shopping, General)
- Specific actionable advice
- Realistic monthly CO₂ reduction estimate
- Confidence score (0.7-0.95)

Return ONLY valid JSON in this exact format:
[
  {{
    "area": "Energy",
    "text": "Specific advice here based on their {inputs.get('electricityKwh', 0)} kWh usage",
    "impact_kg_month": 25,
    "confidence": 0.85
  }}
]

Make recommendations highly specific to their actual numbers above."""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(context)
        
        print(f"🔍 Raw AI response received")
        
        # Parse the JSON response
        try:
            response_text = response.text.strip()
            print(f"AI Response: {response_text}")
            
            # Clean the response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            tips = json.loads(response_text)
            
            # Validate structure
            if isinstance(tips, list) and len(tips) > 0:
                validated_tips = []
                for tip in tips:
                    if all(key in tip for key in ['area', 'text', 'impact_kg_month', 'confidence']):
                        validated_tips.append(tip)
                
                if validated_tips:
                    print(f"✅ AI generated {len(validated_tips)} recommendations")
                    return validated_tips
                else:
                    raise ValueError("No valid tips in response")
            else:
                raise ValueError("Invalid response format")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ AI response parsing failed: {e}")
            return generate_fallback_recommendations(inputs)
        
    except Exception as e:
        print(f"❌ AI recommendation error: {e}")
        return generate_fallback_recommendations(inputs)

def generate_ai_chat_response(user_question: str, inputs: dict) -> str:
    """Generate AI response for chat interface using Gemini"""
    
    if not AI_ENABLED:
        print("🔄 Using fallback chat response (AI not enabled)")
        return generate_fallback_chat_response(user_question, inputs)
    
    try:
        total_emissions = inputs.get('energy_kg', 0) + inputs.get('travel_kg', 0) + inputs.get('food_kg', 0)
        
        context = f"""You are a helpful Carbon Coach AI. Answer the user's question based on their actual carbon footprint data:

USER'S ACTUAL DATA (USE THESE EXACT NUMBERS):
- Total: {total_emissions} kg CO₂/month
- Energy: {inputs.get('energy_kg', 0)} kg CO₂ ({inputs.get('electricityKwh', 0)} kWh electricity)
- Travel: {inputs.get('travel_kg', 0)} kg CO₂ ({inputs.get('carKm', 0)} km car, {inputs.get('busKm', 0)} km bus)
- Food: {inputs.get('food_kg', 0)} kg CO₂ (diet: {inputs.get('diet', 'mixed')})

USER QUESTION: "{user_question}"

IMPORTANT: 
- Use the exact numbers provided above
- Be specific and actionable
- Provide realistic estimates
- Ask a follow-up question to continue conversation
- Keep response conversational but informative
- Focus on solutions, not just problems"""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(context)
        
        ai_response = response.text.strip()
        print(f"✅ AI Chat response: {ai_response}")
        return ai_response
        
    except Exception as e:
        print(f"❌ AI chat error: {e}")
        return generate_fallback_chat_response(user_question, inputs)

def generate_fallback_recommendations(inputs: dict) -> List[Dict]:
    """Generate rule-based recommendations when AI fails"""
    electricity = inputs.get("electricityKwh", 0)
    car_km = inputs.get("carKm", 0)
    diet = inputs.get("diet", "mixed")
    food_emissions = inputs.get("foodEmissions", 3.5)
    goods_emissions = inputs.get("goodsEmissions", 0)
    
    tips = []
    
    # Energy recommendations
    if electricity > 250:
        tips.append({
            "area": "Energy",
            "text": "Install a smart thermostat to optimize heating and cooling schedules",
            "impact_kg_month": round(electricity * 0.82 * 0.12),
            "confidence": 0.85
        })
    
    # Travel recommendations
    if car_km > 200:
        tips.append({
            "area": "Travel",
            "text": "Use public transport or carpool for 30% of your current car trips",
            "impact_kg_month": round(car_km * 0.3 * (0.21 - 0.09)),
            "confidence": 0.8
        })
    
    # Food recommendations
    if diet == "nonveg" or food_emissions > 3.0:
        tips.append({
            "area": "Food",
            "text": "Replace two red meat meals per week with plant-based alternatives",
            "impact_kg_month": 25,
            "confidence": 0.75
        })
    
    # Shopping recommendations
    if goods_emissions > 150:
        tips.append({
            "area": "Shopping",
            "text": "Choose products with minimal packaging and support sustainable brands",
            "impact_kg_month": round(goods_emissions * 0.15),
            "confidence": 0.7
        })
    
    # Ensure minimum 3 recommendations
    while len(tips) < 3:
        tips.append({
            "area": "General",
            "text": "Conduct a home energy audit to identify hidden energy drains",
            "impact_kg_month": 15,
            "confidence": 0.8
        })
    
    return tips[:5]

def generate_fallback_chat_response(question: str, inputs: dict) -> str:
    """Generate fallback chat responses"""
    question_lower = question.lower()
    totals = {
        'energy': inputs.get('energy_kg', 0),
        'travel': inputs.get('travel_kg', 0),
        'food': inputs.get('food_kg', 0)
    }
    total_emissions = totals['energy'] + totals['travel'] + totals['food']
    
    if any(word in question_lower for word in ["energy", "electric", "power", "ac", "heating"]):
        return f"""Based on your energy usage of {totals['energy']} kg CO₂/month, I recommend focusing on efficiency upgrades like smart thermostats, LED lighting, and eliminating phantom loads. These could save you ~{round(totals['energy'] * 0.15)} kg CO₂ monthly. What specific energy concerns do you have?"""
    
    elif any(word in question_lower for word in ["travel", "car", "bus", "commute"]):
        return f"""For your travel emissions of {totals['travel']} kg CO₂/month, consider public transport, carpooling, or active transportation. Small changes could reduce this by ~{round(totals['travel'] * 0.2)} kg monthly. What's your current commute like?"""
    
    elif any(word in question_lower for word in ["food", "diet", "eat", "meal", "vegetarian"]):
        return f"""Regarding your food emissions of {totals['food']} kg CO₂/month, consider reducing meat consumption, choosing local produce, and minimizing food waste. This could save ~{round(totals['food'] * 0.15)} kg monthly. Any specific dietary questions?"""
    
    elif any(word in question_lower for word in ["big", "largest", "main", "primary", "major", "source"]):
        main_source = max(totals, key=totals.get)
        source_percentage = round((totals[main_source] / total_emissions) * 100)
        return f"""Your biggest emission source is {main_source} at {totals[main_source]} kg CO₂/month ({source_percentage}% of total). This is your best opportunity for reduction! Want specific {main_source} reduction tips?"""
    
    else:
        return f"""I'd be happy to help you reduce your carbon footprint of {total_emissions} kg CO₂/month! Your main opportunities are in energy efficiency ({totals['energy']} kg), sustainable transportation ({totals['travel']} kg), and diet optimization ({totals['food']} kg). What specific area interests you?"""

def generate_tips(inputs: dict):
    """Main function to generate recommendations"""
    return generate_ai_recommendations(inputs)

def generate_chat_response(payload: dict) -> str:
    """Generate AI response for chat interface"""
    user_question = payload.get("user_question", "")
    inputs = payload
    return generate_ai_chat_response(user_question, inputs)
