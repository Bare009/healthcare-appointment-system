-- ============================================================
-- Migration: Add audit_log table + patient passwords
-- Run this AFTER the original schema.sql and seed_data.sql
-- ============================================================
USE healthcare_db;

-- 11. Audit Log (Activity Tracking)
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    action_type VARCHAR(50) NOT NULL,          -- INSERT, UPDATE, DELETE, LOGIN, etc.
    table_name VARCHAR(50) NOT NULL,           -- Which table was affected
    record_id INT,                             -- PK of affected row
    performed_by VARCHAR(100),                 -- Who did the action (doctor/patient/system)
    old_values TEXT,                            -- Previous values (JSON-like)
    new_values TEXT,                            -- New values (JSON-like)
    description TEXT,                           -- Human-readable description
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_action (action_type),
    INDEX idx_table (table_name),
    INDEX idx_time (performed_at DESC)
);

-- Add password column to patients (for patient login)
-- Ignore error if column already exists
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_SCHEMA = 'healthcare_db' 
                   AND TABLE_NAME = 'patients' 
                   AND COLUMN_NAME = 'password_hash');
SET @sql = IF(@col_exists = 0, 
              'ALTER TABLE patients ADD COLUMN password_hash VARCHAR(255) DEFAULT NULL',
              'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- NOTE ON TRIGGERS:
-- MySQL triggers require SUPER privilege when binary logging
-- is enabled. If you have SUPER access, uncomment and run
-- the trigger section below.
--
-- In this project, audit logging is done at the APPLICATION
-- layer (services/audit_service.py) which achieves the same
-- result and works without SUPER privilege.
-- ============================================================

-- ============================================================
-- Helpful VIEWS for analytics
-- ============================================================

-- View: Doctor workload summary
CREATE OR REPLACE VIEW v_doctor_workload AS
SELECT 
    d.doctor_id,
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
GROUP BY d.doctor_id, d.name, s.spec_name;

-- View: Disease frequency
CREATE OR REPLACE VIEW v_disease_frequency AS
SELECT 
    pred.predicted_disease,
    COUNT(*) AS occurrence_count,
    ROUND(AVG(pred.urgency_level), 1) AS avg_urgency,
    ROUND(AVG(pred.probability), 1) AS avg_confidence
FROM predictions pred
GROUP BY pred.predicted_disease
ORDER BY occurrence_count DESC;

-- View: Daily appointment summary
CREATE OR REPLACE VIEW v_daily_summary AS
SELECT 
    a.appointment_date,
    COUNT(*) AS total_appointments,
    SUM(CASE WHEN a.urgency_level >= 8 THEN 1 ELSE 0 END) AS `high_priority`,
    SUM(CASE WHEN a.urgency_level >= 4 AND a.urgency_level <= 7 THEN 1 ELSE 0 END) AS `medium_priority`,
    SUM(CASE WHEN a.urgency_level < 4 THEN 1 ELSE 0 END) AS `low_priority`,
    ROUND(AVG(a.urgency_level), 1) AS avg_urgency
FROM appointments a
GROUP BY a.appointment_date
ORDER BY a.appointment_date DESC;

SELECT 'Migration completed successfully!' AS status;
