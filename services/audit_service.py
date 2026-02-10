"""
Audit Service
Handles audit log retrieval and manual log entries
Demonstrates: INSERT with TIMESTAMP, filtering, ORDER BY DESC
"""

from database.connection import execute_query


def log_action(action_type, table_name, record_id=None,
               performed_by="system", old_values=None,
               new_values=None, description=None):
    """Write an entry to the audit log."""
    query = """
    INSERT INTO audit_log
        (action_type, table_name, record_id, performed_by,
         old_values, new_values, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (
        action_type, table_name, record_id,
        performed_by, old_values, new_values, description
    ))


def get_audit_logs(limit=100, action_filter=None, table_filter=None):
    """Fetch recent audit log entries with optional filters."""
    query = """
    SELECT log_id, action_type, table_name, record_id,
           performed_by, old_values, new_values,
           description, performed_at
    FROM audit_log
    WHERE 1=1
    """
    params = []

    if action_filter and action_filter != "All":
        query += " AND action_type = %s"
        params.append(action_filter)

    if table_filter and table_filter != "All":
        query += " AND table_name = %s"
        params.append(table_filter)

    query += " ORDER BY performed_at DESC LIMIT %s"
    params.append(limit)

    return execute_query(query, tuple(params), fetch=True) or []


def get_audit_action_types():
    """Distinct action types in the log."""
    query = "SELECT DISTINCT action_type FROM audit_log ORDER BY action_type"
    rows = execute_query(query, fetch=True) or []
    return [r['action_type'] for r in rows]


def get_audit_table_names():
    """Distinct table names in the log."""
    query = "SELECT DISTINCT table_name FROM audit_log ORDER BY table_name"
    rows = execute_query(query, fetch=True) or []
    return [r['table_name'] for r in rows]


def get_audit_summary():
    """Aggregated audit stats."""
    query = """
    SELECT 
        action_type,
        COUNT(*) AS count
    FROM audit_log
    GROUP BY action_type
    ORDER BY count DESC
    """
    return execute_query(query, fetch=True) or []
