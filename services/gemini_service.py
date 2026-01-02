"""
Gemini AI Service
Handles symptom analysis using Google Gemini API
"""

import google.generativeai as genai
from config import GEMINI_API_KEY
import json
import re

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_symptoms(symptom_text):
    """
    Analyze patient symptoms using Gemini AI
    
    Args:
        symptom_text (str): Detailed symptom description
    
    Returns:
        dict: {
            'predicted_disease': str,
            'probability': float (0-100),
            'urgency_level': int (1-10),
            'urgency_reason': str,
            'secondary_conditions': list
        }
        None if API fails
    """
    
    prompt = f"""
You are a medical AI assistant analyzing patient symptoms for triage purposes.

PATIENT SYMPTOMS:
{symptom_text}

Analyze these symptoms and provide a structured medical assessment.

RESPOND ONLY IN VALID JSON FORMAT (no markdown, no code blocks):
{{
  "predicted_disease": "most likely medical condition",
  "probability": 75,
  "urgency_level": 7,
  "urgency_reason": "brief medical explanation for this urgency score",
  "secondary_conditions": [
    {{"disease": "alternative diagnosis 1", "probability": 15}},
    {{"disease": "alternative diagnosis 2", "probability": 10}}
  ]
}}

URGENCY SCALE GUIDELINES:
1-2: Minor issues (common cold, mild allergies, routine check-up needed)
3-4: Non-urgent but requires attention (chronic pain, skin rash, minor infections)
5-6: Moderate priority (persistent fever, severe headache, respiratory infection)
7-8: High priority - needs same-day attention (chest discomfort, severe pain, difficulty breathing)
9-10: CRITICAL EMERGENCY (heart attack symptoms, stroke signs, severe trauma, uncontrolled bleeding)

Consider severity, duration, and potential complications when assigning urgency.
"""
    
    try:
        print("🤖 Calling Gemini API for diagnosis...")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean the response (remove markdown code blocks if present)
        if "```json" in result_text:
            result_text = result_text.split("```json").split("```").strip()[1]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Remove any leading/trailing whitespace or newlines
        result_text = result_text.strip()
        
        # Parse JSON
        diagnosis = json.loads(result_text)
        
        # Validate required fields
        required_fields = ['predicted_disease', 'probability', 'urgency_level']
        for field in required_fields:
            if field not in diagnosis:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate ranges
        diagnosis['probability'] = max(0, min(100, float(diagnosis['probability'])))
        diagnosis['urgency_level'] = max(1, min(10, int(diagnosis['urgency_level'])))
        
        # Ensure urgency_reason exists
        if 'urgency_reason' not in diagnosis or not diagnosis['urgency_reason']:
            diagnosis['urgency_reason'] = f"Urgency level {diagnosis['urgency_level']} based on symptom analysis"
        
        # Ensure secondary_conditions is a list
        if 'secondary_conditions' not in diagnosis:
            diagnosis['secondary_conditions'] = []
        
        print(f"✅ AI Analysis Complete: {diagnosis['predicted_disease']} (Urgency: {diagnosis['urgency_level']}/10)")
        return diagnosis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw response: {result_text[:200]}...")
        return create_fallback_response(symptom_text)
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return create_fallback_response(symptom_text)

def create_fallback_response(symptom_text):
    """
    Create fallback response when AI fails
    Uses simple keyword matching for basic triage
    
    Args:
        symptom_text (str): Symptom description
    
    Returns:
        dict: Basic diagnosis structure
    """
    symptom_lower = symptom_text.lower()
    
    # Critical keywords
    critical_keywords = ['chest pain', 'heart attack', 'stroke', 'bleeding', 
                         'unconscious', 'seizure', 'severe trauma']
    high_keywords = ['severe pain', 'high fever', 'difficulty breathing', 
                     'vomiting blood', 'cannot walk']
    moderate_keywords = ['fever', 'pain', 'cough', 'headache', 'diarrhea']
    
    # Determine urgency based on keywords
    if any(keyword in symptom_lower for keyword in critical_keywords):
        urgency = 9
        disease = "Emergency Medical Condition"
        reason = "Critical symptoms detected - immediate medical attention required"
    elif any(keyword in symptom_lower for keyword in high_keywords):
        urgency = 7
        disease = "Acute Medical Condition"
        reason = "Severe symptoms - same-day medical consultation recommended"
    elif any(keyword in symptom_lower for keyword in moderate_keywords):
        urgency = 5
        disease = "Medical Condition Requiring Evaluation"
        reason = "Moderate symptoms - consultation within 24-48 hours recommended"
    else:
        urgency = 3
        disease = "General Medical Consultation"
        reason = "Symptoms require professional evaluation"
    
    return {
        'predicted_disease': disease,
        'probability': 50,
        'urgency_level': urgency,
        'urgency_reason': reason + " (AI analysis unavailable - manual review required)",
        'secondary_conditions': []
    }

def get_urgency_label(urgency_level):
    """
    Convert urgency number to label
    
    Args:
        urgency_level (int): 1-10
    
    Returns:
        str: HIGH/MEDIUM/LOW
    """
    if urgency_level >= 8:
        return "HIGH"
    elif urgency_level >= 4:
        return "MEDIUM"
    else:
        return "LOW"

def get_urgency_color(urgency_level):
    """
    Get color code for urgency level (for UI)
    
    Args:
        urgency_level (int): 1-10
    
    Returns:
        str: Color name or hex code
    """
    if urgency_level >= 8:
        return "🔴"  # Red
    elif urgency_level >= 4:
        return "🟡"  # Orange/Yellow
    else:
        return "🟢"  # Green
