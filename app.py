from flask import Flask, request, jsonify, session, send_from_directory, make_response
from flask_cors import CORS
import secrets
from datetime import datetime
import random
import re
import os

app = Flask(__name__, static_folder="public", static_url_path="")
app.config['SECRET_KEY'] = secrets.token_hex(16)
CORS(app, supports_credentials=True)

# Medical Knowledge Base
MEDICAL_KB = {
    # Common Diseases
    "cold": {
        "symptoms": ["runny nose", "cough", "sore throat", "sneezing", "mild fever"],
        "causes": "Viral infection, usually rhinovirus",
        "treatment": "Rest, fluids, vitamin C, over-the-counter cold medicine",
        "prevention": "Wash hands frequently, avoid close contact with sick people",
        "severity": "mild"
    },
    "flu": {
        "symptoms": ["high fever", "body aches", "fatigue", "dry cough", "headache"],
        "causes": "Influenza virus",
        "treatment": "Rest, fluids, antiviral medications if prescribed, pain relievers",
        "prevention": "Annual flu vaccine, good hygiene",
        "severity": "moderate"
    },
    "fever": {
        "symptoms": ["elevated body temperature above 100.4°F (38°C)", "chills", "sweating"],
        "causes": "Infection, inflammation, heat exhaustion",
        "treatment": "Paracetamol, hydration, cool compress, rest",
        "prevention": "Maintain hygiene, avoid infections",
        "severity": "mild"
    },
    "diabetes": {
        "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing wounds"],
        "causes": "Insulin deficiency or resistance",
        "treatment": "Insulin, oral medications, diet control, regular exercise",
        "prevention": "Healthy diet, exercise, maintain healthy weight",
        "severity": "chronic"
    },
    "hypertension": {
        "symptoms": ["headaches", "dizziness", "chest pain", "shortness of breath"],
        "causes": "Genetics, poor diet, lack of exercise, stress",
        "treatment": "Blood pressure medications, lifestyle changes, low-salt diet",
        "prevention": "Exercise, healthy diet, stress management, limit alcohol",
        "severity": "chronic"
    },
    "asthma": {
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "coughing"],
        "causes": "Allergens, pollution, exercise, cold air",
        "treatment": "Inhalers (bronchodilators), corticosteroids, avoid triggers",
        "prevention": "Identify and avoid triggers, maintain clean environment",
        "severity": "moderate"
    }
}

# First Aid Procedures
FIRST_AID = {
    "burn": "Cool the burn under running water for 10-20 minutes. Cover with sterile bandage. For severe burns, seek medical help immediately.",
    "cut": "Apply pressure with clean cloth to stop bleeding. Clean with water, apply antibiotic ointment, and cover with bandage.",
    "choking": "Perform Heimlich maneuver: Stand behind person, make fist above navel, grasp with other hand, thrust inward and upward.",
    "fracture": "Immobilize the injured area. Don't try to realign. Apply ice pack. Seek medical attention immediately.",
    "nosebleed": "Lean forward, pinch soft part of nose for 10 minutes. Apply cold compress. If bleeding continues, see a doctor.",
    "sprain": "RICE method: Rest, Ice, Compression, Elevation. Apply ice for 20 minutes every 2-3 hours."
}

# Medications Information
MEDICATIONS = {
    "paracetamol": {
        "use": "Pain relief and fever reduction",
        "dosage": "Adults: 500-1000mg every 4-6 hours, max 4000mg/day",
        "side_effects": "Rare, but can include liver damage if overdosed",
        "precautions": "Avoid alcohol, don't exceed recommended dose"
    },
    "ibuprofen": {
        "use": "Pain, inflammation, fever reduction",
        "dosage": "Adults: 200-400mg every 4-6 hours, max 1200mg/day",
        "side_effects": "Stomach upset, ulcers with long-term use",
        "precautions": "Take with food, avoid if history of stomach ulcers"
    },
    "aspirin": {
        "use": "Pain relief, fever reduction, blood thinning",
        "dosage": "Adults: 325-650mg every 4 hours as needed",
        "side_effects": "Stomach irritation, bleeding risk",
        "precautions": "Not for children under 16, avoid if bleeding disorder"
    }
}

# Emergency Keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "difficulty breathing",
    "unconscious", "suicide", "severe bleeding", "stroke", "seizure",
    "choking", "poisoning", "severe burn"
]

# Intents and Patterns
INTENTS = [
    {
        "tag": "greeting",
        "patterns": ["hi", "hello", "hey", "good morning", "good evening"],
        "responses": [
            "Hello! I'm your Medical Information Assistant. How can I help you today? 🏥",
            "Hi there! I'm here to provide medical information. What can I help you with? 👨‍⚕️",
            "Greetings! Ask me about symptoms, conditions, or first aid! 💊"
        ]
    },
    {
        "tag": "disclaimer",
        "patterns": ["disclaimer", "legal", "warning"],
        "responses": [
            "⚠️ IMPORTANT: This chatbot provides general medical information only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult healthcare professionals for medical concerns."
        ]
    },
    {
        "tag": "capabilities",
        "patterns": ["what can you do", "help", "features", "capabilities"],
        "responses": [
            "I can help with:\n• Common illness information\n• Symptoms guidance\n• First aid instructions\n• Medication info\n• Healthy lifestyle tips\n• When to see a doctor\n\nWhat would you like to know? 🩺"
        ]
    },
    {
        "tag": "thanks",
        "patterns": ["thanks", "thank you", "appreciate"],
        "responses": ["You're welcome! Stay healthy! 💚", "Happy to help! Take care! 🌟"]
    },
    {
        "tag": "goodbye",
        "patterns": ["bye", "goodbye", "see you"],
        "responses": ["Goodbye! Remember to consult a doctor for serious concerns. Stay healthy! 👋"]
    }
]

def match_intent(text):
    """Match user input with predefined intents"""
    text_lower = text.lower()
    
    # Check for emergency
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return "🚨 EMERGENCY: If you're experiencing " + keyword + ", please call emergency services (911/108) immediately or go to the nearest hospital!"
    
    # Check intents
    for intent in INTENTS:
        for pattern in intent["patterns"]:
            if pattern in text_lower:
                return random.choice(intent["responses"])
    
    # Check diseases
    for disease, info in MEDICAL_KB.items():
        if disease in text_lower or any(symptom in text_lower for symptom in info["symptoms"]):
            response = f"📋 **{disease.upper()}**\n\n"
            response += f"**Symptoms:** {', '.join(info['symptoms'])}\n\n"
            response += f"**Causes:** {info['causes']}\n\n"
            response += f"**Treatment:** {info['treatment']}\n\n"
            response += f"**Prevention:** {info['prevention']}\n\n"
            if info["severity"] == "chronic":
                response += "⚠️ This is a chronic condition. Please consult a doctor for proper management."
            return response
    
    # Check first aid
    for injury, procedure in FIRST_AID.items():
        if injury in text_lower or "first aid" in text_lower:
            return f"🩹 **FIRST AID for {injury.upper()}:**\n\n{procedure}\n\n⚠️ Seek professional medical help if condition is serious."
    
    # Check medications
    for med, info in MEDICATIONS.items():
        if med in text_lower or "medication" in text_lower or "medicine" in text_lower:
            response = f"💊 **{med.upper()}**\n\n"
            response += f"**Use:** {info['use']}\n\n"
            response += f"**Dosage:** {info['dosage']}\n\n"
            response += f"**Side Effects:** {info['side_effects']}\n\n"
            response += f"**Precautions:** {info['precautions']}\n\n"
            response += "⚠️ Always consult a doctor before taking any medication."
            return response
    
    # Symptom checker
    if "symptom" in text_lower or "feel" in text_lower or "pain" in text_lower:
        return "I can help you understand symptoms. Please describe what you're experiencing (e.g., 'I have a headache and fever'). Remember, this is NOT a diagnosis - please see a doctor for proper evaluation. 👨‍⚕️"
    
    # Default fallback
    return "I'm not sure about that. I can help with:\n• Common illnesses (cold, flu, fever, diabetes, etc.)\n• First aid (burns, cuts, sprains)\n• Medications\n• Symptoms\n\nTry asking about a specific condition! 🏥"

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(8)
    return session['session_id']

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/message", methods=["POST"])
def message():
    try:
        data = request.get_json()
        user_text = data.get("message", "").strip()
        
        if not user_text:
            return jsonify({"error": "Empty message"}), 400
        
        # Get bot response
        reply = match_intent(user_text)
        
        return jsonify({
            "reply": reply,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Medical Chatbot Server Starting...")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("⚕️  Medical Information Assistant Ready!")
    print("=" * 60)
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)