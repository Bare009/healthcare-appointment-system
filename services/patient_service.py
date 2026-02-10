"""
Patient Service
Handles all patient-related database operations
"""

from database.connection import execute_query
from datetime import date
import hashlib


def _hash_password(password):
    """Simple SHA-256 hash for lab project."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_patient(first_name, last_name, gender, age, phone, allergies=None):
    """
    Insert new patient into database
    
    Args:
        first_name (str): Patient's first name
        last_name (str): Patient's last name (optional)
        gender (str): Male/Female/Other
        age (int): Patient age
        phone (str): Contact number
        allergies (str): Known allergies (optional)
    
    Returns:
        int: patient_id if successful, None if failed
    """
    # Generate full_name
    full_name = f"{first_name} {last_name or ''}".strip()
    
    query = """
    INSERT INTO patients (first_name, last_name, full_name, gender, age, phone, allergies)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (first_name, last_name, full_name, gender, age, phone, allergies)
    
    try:
        patient_id = execute_query(query, params)
        if patient_id:
            print(f"✅ Patient created successfully. ID: {patient_id}")
        return patient_id
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        return None

def get_patient_by_id(patient_id):
    """
    Fetch patient details by ID
    
    Args:
        patient_id (int): Patient ID
    
    Returns:
        dict: Patient record or None
    """
    query = "SELECT * FROM patients WHERE patient_id = %s"
    result = execute_query(query, (patient_id,), fetch=True, fetch_one=True)
    return result

def get_patient_by_phone(phone):
    """
    Check if patient exists by phone number
    Useful for returning patients
    
    Args:
        phone (str): Phone number
    
    Returns:
        dict: Patient record or None
    """
    query = "SELECT * FROM patients WHERE phone = %s"
    result = execute_query(query, (phone,), fetch=True, fetch_one=True)
    return result

def update_patient_allergies(patient_id, allergies):
    """
    Update patient's allergy information
    
    Args:
        patient_id (int): Patient ID
        allergies (str): Updated allergy text
    
    Returns:
        bool: True if successful
    """
    query = "UPDATE patients SET allergies = %s WHERE patient_id = %s"
    result = execute_query(query, (allergies, patient_id))
    return result is not None

def get_all_patients(limit=50):
    """
    Fetch all patients (for admin view)
    
    Args:
        limit (int): Maximum records to return
    
    Returns:
        list: List of patient records
    """
    query = """
    SELECT patient_id, full_name, age, gender, phone, created_at
    FROM patients
    ORDER BY created_at DESC
    LIMIT %s
    """
    return execute_query(query, (limit,), fetch=True) or []

def get_patient_statistics():
    """
    Get patient statistics for dashboard
    
    Returns:
        dict: Statistics (total patients, age distribution, etc.)
    """
    queries = {
        'total_patients': "SELECT COUNT(*) as count FROM patients",
        'avg_age': "SELECT AVG(age) as avg_age FROM patients",
        'gender_distribution': """
            SELECT gender, COUNT(*) as count 
            FROM patients 
            GROUP BY gender
        """
    }
    
    stats = {}
    stats['total_patients'] = execute_query(queries['total_patients'], 
                                            fetch=True, fetch_one=True)['count']
    stats['avg_age'] = round(execute_query(queries['avg_age'], 
                                           fetch=True, fetch_one=True)['avg_age'] or 0, 1)
    stats['gender_distribution'] = execute_query(queries['gender_distribution'], 
                                                 fetch=True)
    
    return stats


def set_patient_password(patient_id, password):
    """Set a hashed password for patient login."""
    hashed = _hash_password(password)
    query = "UPDATE patients SET password_hash = %s WHERE patient_id = %s"
    return execute_query(query, (hashed, patient_id)) is not None


def verify_patient_login(phone, password):
    """
    Verify patient credentials.
    Returns patient dict on success, None on failure.
    """
    hashed = _hash_password(password)
    query = """
    SELECT patient_id, first_name, last_name, full_name, gender, age, phone, allergies
    FROM patients
    WHERE phone = %s AND password_hash = %s
    """
    return execute_query(query, (phone, hashed), fetch=True, fetch_one=True)


def patient_has_password(phone):
    """Check if patient has a password set."""
    query = "SELECT password_hash FROM patients WHERE phone = %s"
    result = execute_query(query, (phone,), fetch=True, fetch_one=True)
    if result and result.get('password_hash'):
        return True
    return False
