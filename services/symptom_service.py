"""
Symptom Service
Handles symptom submission and retrieval
"""

from database.connection import execute_query
from datetime import datetime

def save_symptom(patient_id, symptom_text):
    """
    Save patient symptom description
    
    Args:
        patient_id (int): Patient ID
        symptom_text (str): Detailed symptom description
    
    Returns:
        int: symptom_id if successful, None if failed
    """
    # Validate minimum length
    if len(symptom_text.strip()) < 10:
        print("❌ Symptom text too short (minimum 10 characters)")
        return None
    
    query = """
    INSERT INTO symptoms (patient_id, symptom_text)
    VALUES (%s, %s)
    """
    
    try:
        symptom_id = execute_query(query, (patient_id, symptom_text.strip()))
        if symptom_id:
            print(f"✅ Symptom recorded. ID: {symptom_id}")
        return symptom_id
    except Exception as e:
        print(f"❌ Error saving symptom: {e}")
        return None

def get_symptom_by_id(symptom_id):
    """
    Fetch symptom details by ID
    
    Args:
        symptom_id (int): Symptom ID
    
    Returns:
        dict: Symptom record with patient info
    """
    query = """
    SELECT 
        s.symptom_id,
        s.symptom_text,
        s.submitted_at,
        p.full_name as patient_name,
        p.age,
        p.gender
    FROM symptoms s
    INNER JOIN patients p ON s.patient_id = p.patient_id
    WHERE s.symptom_id = %s
    """
    return execute_query(query, (symptom_id,), fetch=True, fetch_one=True)

def get_symptoms_by_patient(patient_id, limit=10):
    """
    Get patient's symptom history
    
    Args:
        patient_id (int): Patient ID
        limit (int): Maximum records to return
    
    Returns:
        list: List of symptom records
    """
    query = """
    SELECT 
        s.symptom_id,
        s.symptom_text,
        s.submitted_at,
        pred.predicted_disease,
        pred.urgency_level
    FROM symptoms s
    LEFT JOIN predictions pred ON s.symptom_id = pred.symptom_id
    WHERE s.patient_id = %s
    ORDER BY s.submitted_at DESC
    LIMIT %s
    """
    return execute_query(query, (patient_id, limit), fetch=True) or []

def get_recent_symptoms(days=7, limit=20):
    """
    Get recent symptoms across all patients (for analytics)
    
    Args:
        days (int): Number of days to look back
        limit (int): Maximum records
    
    Returns:
        list: Recent symptom submissions
    """
    query = """
    SELECT 
        s.symptom_id,
        p.full_name as patient_name,
        s.symptom_text,
        s.submitted_at,
        pred.urgency_level
    FROM symptoms s
    INNER JOIN patients p ON s.patient_id = p.patient_id
    LEFT JOIN predictions pred ON s.symptom_id = pred.symptom_id
    WHERE s.submitted_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    ORDER BY s.submitted_at DESC
    LIMIT %s
    """
    return execute_query(query, (days, limit), fetch=True) or []

def count_symptoms_today():
    """
    Count symptom submissions today
    
    Returns:
        int: Count of today's submissions
    """
    query = """
    SELECT COUNT(*) as count 
    FROM symptoms 
    WHERE DATE(submitted_at) = CURDATE()
    """
    result = execute_query(query, fetch=True, fetch_one=True)
    return result['count'] if result else 0
