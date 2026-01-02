"""
Appointment Service
Handles appointment creation, scheduling, and queue management
Demonstrates: JOINs, Transactions, Sorting, Indexing
"""

from database.connection import execute_query, get_connection
from mysql.connector import Error
from datetime import datetime, timedelta, time
import random

def save_prediction(symptom_id, diagnosis_result):
    """
    Store AI prediction in database
    
    Args:
        symptom_id (int): Symptom ID
        diagnosis_result (dict): AI diagnosis output
    
    Returns:
        int: prediction_id or None
    """
    query = """
    INSERT INTO predictions 
    (symptom_id, predicted_disease, probability, urgency_level, urgency_reason)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        symptom_id,
        diagnosis_result['predicted_disease'],
        diagnosis_result['probability'],
        diagnosis_result['urgency_level'],
        diagnosis_result.get('urgency_reason', '')
    )
    
    try:
        prediction_id = execute_query(query, params)
        if prediction_id:
            print(f"✅ Prediction saved. ID: {prediction_id}")
        return prediction_id
    except Exception as e:
        print(f"❌ Error saving prediction: {e}")
        return None

def find_available_doctor(specialization_name, appointment_date):
    """
    Find available doctor for given specialization and date
    Selects doctor with least appointments that day
    
    Args:
        specialization_name (str): Specialization (e.g., 'Cardiology')
        appointment_date (date): Appointment date
    
    Returns:
        dict: Doctor info or None
    """
    query = """
    SELECT 
        d.doctor_id, 
        d.name, 
        d.qualification,
        COUNT(a.appointment_id) as appointment_count
    FROM doctors d
    INNER JOIN specializations s ON d.spec_id = s.spec_id
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id 
        AND a.appointment_date = %s
        AND a.status IN ('Confirmed', 'Pending')
    WHERE s.spec_name = %s AND d.available = TRUE
    GROUP BY d.doctor_id
    HAVING appointment_count < 16
    ORDER BY appointment_count ASC
    LIMIT 1
    """
    
    result = execute_query(query, (appointment_date, specialization_name), 
                          fetch=True, fetch_one=True)
    
    if result:
        print(f"✅ Doctor assigned: {result['name']} ({result['appointment_count']} appointments)")
    else:
        print(f"⚠️ No available doctor for {specialization_name} on {appointment_date}")
    
    return result

def generate_time_slot(urgency_level, existing_appointments_count):
    """
    Generate appointment time based on urgency
    High urgency gets earlier slots
    
    Args:
        urgency_level (int): 1-10
        existing_appointments_count (int): Number of appointments already scheduled
    
    Returns:
        time: Appointment time
    """
    # Time slots: 9 AM to 5 PM, 30-minute intervals
    base_hour = 9
    
    if urgency_level >= 8:  # High priority - morning slots
        slot_offset = existing_appointments_count % 6  # 9 AM - 12 PM
    elif urgency_level >= 4:  # Medium - afternoon
        slot_offset = 6 + (existing_appointments_count % 6)  # 12 PM - 3 PM
    else:  # Low - evening
        slot_offset = 12 + (existing_appointments_count % 4)  # 3 PM - 5 PM
    
    hour = base_hour + (slot_offset // 2)
    minute = 0 if slot_offset % 2 == 0 else 30
    
    return time(hour, minute)

def create_appointment(patient_id, doctor_id, symptom_id, urgency_level, 
                      appointment_date, appointment_time=None, mode='Offline'):
    """
    Create appointment record with transaction safety
    
    Args:
        patient_id (int): Patient ID
        doctor_id (int): Doctor ID
        symptom_id (int): Symptom ID
        urgency_level (int): 1-10
        appointment_date (date): Appointment date
        appointment_time (time): Specific time (optional, auto-generated if None)
        mode (str): 'Online' or 'Offline'
    
    Returns:
        int: appointment_id or None
    """
    # Auto-generate time if not provided
    if appointment_time is None:
        # Count existing appointments for this doctor on this date
        count_query = """
        SELECT COUNT(*) as count FROM appointments 
        WHERE doctor_id = %s AND appointment_date = %s
        """
        result = execute_query(count_query, (doctor_id, appointment_date), 
                             fetch=True, fetch_one=True)
        appointment_count = result['count'] if result else 0
        appointment_time = generate_time_slot(urgency_level, appointment_count)
    
    query = """
    INSERT INTO appointments 
    (patient_id, doctor_id, symptom_id, urgency_level, 
     appointment_date, appointment_time, status, mode)
    VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed', %s)
    """
    params = (patient_id, doctor_id, symptom_id, urgency_level,
              appointment_date, appointment_time, mode)
    
    try:
        appointment_id = execute_query(query, params)
        if appointment_id:
            print(f"✅ Appointment created. ID: APT-{appointment_id:03d}")
        return appointment_id
    except Exception as e:
        print(f"❌ Error creating appointment: {e}")
        return None

def get_appointment_queue(date_filter=None, urgency_filter=None, specialization_filter=None):
    """
    Fetch sorted appointment queue
    **MAIN DBMS SHOWCASE QUERY** - Demonstrates:
    - Multi-table JOINs (5 tables)
    - Filtering with WHERE conditions
    - Sorting by urgency (using index)
    - Aggregate data retrieval
    
    Args:
        date_filter (date): Filter by specific date
        urgency_filter (str): 'High', 'Medium', 'Low', or None
        specialization_filter (str): Specialization name or None
    
    Returns:
        list: Sorted appointment records
    """
    query = """
    SELECT 
        a.appointment_id,
        a.appointment_date,
        a.appointment_time,
        a.status,
        a.mode,
        a.urgency_level,
        p.patient_id,
        p.full_name AS patient_name,
        p.age,
        p.gender,
        p.phone,
        s.symptom_text,
        pred.predicted_disease,
        pred.probability,
        pred.urgency_reason,
        d.doctor_id,
        d.name AS doctor_name,
        d.qualification,
        spec.spec_name AS specialization,
        CONCAT('APT-', LPAD(a.appointment_id, 3, '0')) AS appointment_code
    FROM appointments a
    INNER JOIN patients p ON a.patient_id = p.patient_id
    INNER JOIN symptoms s ON a.symptom_id = s.symptom_id
    INNER JOIN predictions pred ON s.symptom_id = pred.symptom_id
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    INNER JOIN specializations spec ON d.spec_id = spec.spec_id
    WHERE a.status IN ('Confirmed', 'Pending')
    """
    
    params = []
    
    # Apply filters
    if date_filter:
        query += " AND a.appointment_date = %s"
        params.append(date_filter)
    
    if urgency_filter:
        if urgency_filter == 'High':
            query += " AND a.urgency_level >= 8"
        elif urgency_filter == 'Medium':
            query += " AND a.urgency_level BETWEEN 4 AND 7"
        elif urgency_filter == 'Low':
            query += " AND a.urgency_level <= 3"
    
    if specialization_filter and specialization_filter != 'All':
        query += " AND spec.spec_name = %s"
        params.append(specialization_filter)
    
    # Critical sorting: urgency DESC, then date, then time
    query += " ORDER BY a.urgency_level DESC, a.appointment_date ASC, a.appointment_time ASC"
    
    results = execute_query(query, tuple(params) if params else None, fetch=True)
    return results or []

def get_appointment_by_id(appointment_id):
    """
    Get detailed appointment information
    
    Args:
        appointment_id (int): Appointment ID
    
    Returns:
        dict: Complete appointment record
    """
    query = """
    SELECT 
        a.*,
        p.full_name AS patient_name,
        p.phone,
        d.name AS doctor_name,
        spec.spec_name AS specialization,
        s.symptom_text,
        pred.predicted_disease,
        pred.urgency_level
    FROM appointments a
    INNER JOIN patients p ON a.patient_id = p.patient_id
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    INNER JOIN specializations spec ON d.spec_id = spec.spec_id
    INNER JOIN symptoms s ON a.symptom_id = s.symptom_id
    INNER JOIN predictions pred ON s.symptom_id = pred.symptom_id
    WHERE a.appointment_id = %s
    """
    return execute_query(query, (appointment_id,), fetch=True, fetch_one=True)

def get_appointment_statistics():
    """
    Get appointment statistics for dashboard
    
    Returns:
        dict: Various statistics
    """
    stats = {}
    
    # Total appointments today
    query_today = """
    SELECT COUNT(*) as count FROM appointments 
    WHERE appointment_date = CURDATE() AND status = 'Confirmed'
    """
    result = execute_query(query_today, fetch=True, fetch_one=True)
    stats['today_total'] = result['count'] if result else 0
    
    # High priority count today
    query_high = """
    SELECT COUNT(*) as count FROM appointments 
    WHERE appointment_date = CURDATE() 
    AND urgency_level >= 8 
    AND status = 'Confirmed'
    """
    result = execute_query(query_high, fetch=True, fetch_one=True)
    stats['today_high_priority'] = result['count'] if result else 0
    
    # Specialization distribution
    query_spec = """
    SELECT spec.spec_name, COUNT(a.appointment_id) as count
    FROM appointments a
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    INNER JOIN specializations spec ON d.spec_id = spec.spec_id
    WHERE a.appointment_date = CURDATE()
    GROUP BY spec.spec_name
    ORDER BY count DESC
    """
    stats['specialization_distribution'] = execute_query(query_spec, fetch=True) or []
    
    return stats

def get_all_specializations():
    """
    Get list of all specializations (for dropdown)
    
    Returns:
        list: Specialization names
    """
    query = "SELECT spec_name FROM specializations ORDER BY spec_name"
    results = execute_query(query, fetch=True)
    return [r['spec_name'] for r in results] if results else []
