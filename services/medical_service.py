"""
Medical Record Service
Handles medical records, prescriptions, and feedback
Demonstrates: Multi-table INSERT, Foreign Keys, Transactions, Aggregation
"""

from database.connection import execute_query, get_connection
from mysql.connector import Error
from datetime import date


# ── Medical Records ──

def create_medical_record(appointment_id, diagnosis, notes=""):
    """
    Create a medical record for a completed appointment.
    Uses transaction to also mark appointment as Completed.
    """
    conn = get_connection()
    if not conn:
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        # Insert medical record
        cursor.execute("""
            INSERT INTO medical_records (appointment_id, diagnosis, notes, record_date)
            VALUES (%s, %s, %s, %s)
        """, (appointment_id, diagnosis, notes, date.today()))

        record_id = cursor.lastrowid

        # Mark appointment as Completed
        cursor.execute("""
            UPDATE appointments SET status = 'Completed' WHERE appointment_id = %s
        """, (appointment_id,))

        conn.commit()
        print(f"✅ Medical record created. ID: {record_id}")
        return record_id

    except Error as e:
        conn.rollback()
        print(f"❌ Error creating medical record: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_medical_record_by_appointment(appointment_id):
    """Fetch medical record for a specific appointment."""
    query = """
    SELECT mr.*, 
           a.appointment_date,
           p.full_name AS patient_name,
           d.name AS doctor_name
    FROM medical_records mr
    INNER JOIN appointments a ON mr.appointment_id = a.appointment_id
    INNER JOIN patients p ON a.patient_id = p.patient_id
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE mr.appointment_id = %s
    """
    return execute_query(query, (appointment_id,), fetch=True, fetch_one=True)


# ── Prescriptions ──

def add_prescription(record_id, medicine_name, dosage, duration):
    """Add a single prescription line to a medical record."""
    query = """
    INSERT INTO prescriptions (record_id, medicine_name, dosage, duration)
    VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (record_id, medicine_name, dosage, duration))


def add_prescriptions_bulk(record_id, prescriptions_list):
    """
    Add multiple prescriptions in one transaction.
    prescriptions_list: list of dicts with keys medicine_name, dosage, duration
    """
    conn = get_connection()
    if not conn:
        return False
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO prescriptions (record_id, medicine_name, dosage, duration)
            VALUES (%s, %s, %s, %s)
        """
        for p in prescriptions_list:
            cursor.execute(query, (record_id, p['medicine_name'], p['dosage'], p['duration']))
        conn.commit()
        print(f"✅ {len(prescriptions_list)} prescriptions added for record {record_id}")
        return True
    except Error as e:
        conn.rollback()
        print(f"❌ Error adding prescriptions: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_prescriptions_by_record(record_id):
    """Fetch all prescriptions for a medical record."""
    query = """
    SELECT prescription_id, medicine_name, dosage, duration
    FROM prescriptions
    WHERE record_id = %s
    ORDER BY prescription_id
    """
    return execute_query(query, (record_id,), fetch=True) or []


def get_prescriptions_by_appointment(appointment_id):
    """Fetch all prescriptions via appointment → medical_record → prescriptions."""
    query = """
    SELECT p.prescription_id, p.medicine_name, p.dosage, p.duration,
           mr.diagnosis, mr.notes, mr.record_date
    FROM prescriptions p
    INNER JOIN medical_records mr ON p.record_id = mr.record_id
    WHERE mr.appointment_id = %s
    ORDER BY p.prescription_id
    """
    return execute_query(query, (appointment_id,), fetch=True) or []


# ── Feedback ──

def submit_feedback(patient_id, appointment_id, rating, comment=""):
    """Submit patient feedback for a completed appointment."""
    query = """
    INSERT INTO feedback (patient_id, appointment_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """
    try:
        return execute_query(query, (patient_id, appointment_id, rating, comment))
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
        return None


def get_feedback_by_appointment(appointment_id):
    """Get feedback for a specific appointment."""
    query = """
    SELECT f.*, p.full_name AS patient_name
    FROM feedback f
    INNER JOIN patients p ON f.patient_id = p.patient_id
    WHERE f.appointment_id = %s
    """
    return execute_query(query, (appointment_id,), fetch=True, fetch_one=True)


def get_doctor_avg_rating(doctor_id):
    """Get average rating for a doctor using aggregation."""
    query = """
    SELECT 
        ROUND(AVG(f.rating), 1) AS avg_rating,
        COUNT(f.feedback_id) AS total_reviews
    FROM feedback f
    INNER JOIN appointments a ON f.appointment_id = a.appointment_id
    WHERE a.doctor_id = %s
    """
    return execute_query(query, (doctor_id,), fetch=True, fetch_one=True)


def check_feedback_exists(patient_id, appointment_id):
    """Check if feedback already exists (UNIQUE constraint)."""
    query = """
    SELECT feedback_id FROM feedback
    WHERE patient_id = %s AND appointment_id = %s
    """
    return execute_query(query, (patient_id, appointment_id), fetch=True, fetch_one=True) is not None
