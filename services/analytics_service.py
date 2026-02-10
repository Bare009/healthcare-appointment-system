"""
Analytics Service
Provides data for charts and dashboards
Demonstrates: GROUP BY, COUNT, AVG, HAVING, DATE functions, VIEWs, Subqueries
"""

from database.connection import execute_query


def get_disease_distribution(limit=10):
    """Top predicted diseases by frequency."""
    query = """
    SELECT 
        predicted_disease,
        COUNT(*) AS occurrence_count,
        ROUND(AVG(urgency_level), 1) AS avg_urgency,
        ROUND(AVG(probability), 1) AS avg_confidence
    FROM predictions
    GROUP BY predicted_disease
    ORDER BY occurrence_count DESC
    LIMIT %s
    """
    return execute_query(query, (limit,), fetch=True) or []


def get_doctor_workload():
    """Appointment count per doctor with status breakdown."""
    query = """
    SELECT 
        d.name AS doctor_name,
        s.spec_name AS specialization,
        COUNT(a.appointment_id) AS total_appointments,
        SUM(CASE WHEN a.status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
        ROUND(AVG(a.urgency_level), 1) AS avg_urgency
    FROM doctors d
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    INNER JOIN specializations s ON d.spec_id = s.spec_id
    GROUP BY d.doctor_id, d.name, s.spec_name
    ORDER BY total_appointments DESC
    """
    return execute_query(query, fetch=True) or []


def get_daily_trends(days=14):
    """Appointment counts per day for trend chart."""
    query = """
    SELECT 
        a.appointment_date AS apt_date,
        COUNT(*) AS total,
        SUM(CASE WHEN a.urgency_level >= 8 THEN 1 ELSE 0 END) AS high,
        SUM(CASE WHEN a.urgency_level BETWEEN 4 AND 7 THEN 1 ELSE 0 END) AS medium,
        SUM(CASE WHEN a.urgency_level < 4 THEN 1 ELSE 0 END) AS low
    FROM appointments a
    WHERE a.appointment_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    GROUP BY a.appointment_date
    ORDER BY a.appointment_date
    """
    return execute_query(query, (days,), fetch=True) or []


def get_urgency_distribution():
    """Count of appointments per urgency level."""
    query = """
    SELECT 
        urgency_level,
        COUNT(*) AS count
    FROM appointments
    GROUP BY urgency_level
    ORDER BY urgency_level
    """
    return execute_query(query, fetch=True) or []


def get_specialization_demand():
    """Appointments per specialization."""
    query = """
    SELECT 
        s.spec_name AS specialization,
        COUNT(a.appointment_id) AS appointment_count,
        ROUND(AVG(a.urgency_level), 1) AS avg_urgency
    FROM specializations s
    LEFT JOIN doctors d ON s.spec_id = d.spec_id
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    GROUP BY s.spec_id, s.spec_name
    HAVING appointment_count > 0
    ORDER BY appointment_count DESC
    """
    return execute_query(query, fetch=True) or []


def get_gender_age_stats():
    """Patient demographics from appointments."""
    query = """
    SELECT 
        p.gender,
        COUNT(DISTINCT p.patient_id) AS patient_count,
        ROUND(AVG(p.age), 1) AS avg_age,
        MIN(p.age) AS min_age,
        MAX(p.age) AS max_age
    FROM patients p
    GROUP BY p.gender
    """
    return execute_query(query, fetch=True) or []


def get_feedback_summary():
    """Overall feedback statistics."""
    query = """
    SELECT 
        COUNT(*) AS total_feedback,
        ROUND(AVG(rating), 2) AS avg_rating,
        SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) AS positive,
        SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS negative
    FROM feedback
    """
    return execute_query(query, fetch=True, fetch_one=True)


def get_overview_counts():
    """Quick counts for the top metric cards."""
    result = {}

    q = "SELECT COUNT(*) AS c FROM patients"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['total_patients'] = r['c'] if r else 0

    q = "SELECT COUNT(*) AS c FROM appointments"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['total_appointments'] = r['c'] if r else 0

    q = "SELECT COUNT(*) AS c FROM doctors"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['total_doctors'] = r['c'] if r else 0

    q = "SELECT COUNT(*) AS c FROM medical_records"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['total_records'] = r['c'] if r else 0

    q = "SELECT COUNT(*) AS c FROM feedback"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['total_feedback'] = r['c'] if r else 0

    q = "SELECT COUNT(DISTINCT predicted_disease) AS c FROM predictions"
    r = execute_query(q, fetch=True, fetch_one=True)
    result['unique_diseases'] = r['c'] if r else 0

    return result
