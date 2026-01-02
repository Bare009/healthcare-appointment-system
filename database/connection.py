import mysql.connector
from mysql.connector import Error, pooling
from config import DB_CONFIG
import streamlit as st

connection_pool = None

def initialize_pool():
    """Initialize MySQL connection pool"""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="healthcare_pool",
            pool_size=5,
            **DB_CONFIG
        )
        print("✅ Connection pool created successfully")
        return True
    except Error as e:
        print(f"❌ Error creating connection pool: {e}")
        st.error(f"Database connection failed: {e}")
        return False

def get_connection():
    """Get connection from pool"""
    try:
        if connection_pool is None:
            initialize_pool()
        return connection_pool.get_connection()
    except Error as e:
        st.error(f"Failed to get database connection: {e}")
        return None

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Execute SQL query with error handling
    """
    connection = get_connection()
    if not connection:
        return None
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.lastrowid
            
    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Test function
def test_connection():
    """Test database connection"""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as doctor_count FROM doctors")
            result = cursor.fetchone()
            print(f"✅ Database connected! Found {result[0]} doctors")
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"❌ Connection test failed: {e}")
        return False
