-- ============================================================
-- MySQL TRIGGERS for Audit Logging
-- ============================================================
-- NOTE: These triggers require SUPER privilege when binary
-- logging is enabled. If you can run these on your MySQL
-- installation, they will auto-log all activity.
--
-- If not, the application layer (services/audit_service.py)
-- performs equivalent logging.
--
-- To enable trigger creation without SUPER:
--   SET GLOBAL log_bin_trust_function_creators = 1;
-- (requires root/SUPER access)
-- ============================================================

USE healthcare_db;

-- Trigger 1: Log new appointments
DROP TRIGGER IF EXISTS trg_appointment_insert;
DELIMITER //
CREATE TRIGGER trg_appointment_insert
AFTER INSERT ON appointments
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (action_type, table_name, record_id, performed_by, new_values, description)
    VALUES (
        'INSERT',
        'appointments',
        NEW.appointment_id,
        'system',
        CONCAT('patient_id=', NEW.patient_id, ', doctor_id=', NEW.doctor_id,
               ', date=', NEW.appointment_date, ', urgency=', NEW.urgency_level),
        CONCAT('New appointment APT-', LPAD(NEW.appointment_id, 3, '0'), ' created')
    );
END //
DELIMITER ;

-- Trigger 2: Log appointment status changes
DROP TRIGGER IF EXISTS trg_appointment_update;
DELIMITER //
CREATE TRIGGER trg_appointment_update
AFTER UPDATE ON appointments
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_log (action_type, table_name, record_id, performed_by, old_values, new_values, description)
        VALUES (
            'UPDATE',
            'appointments',
            NEW.appointment_id,
            'doctor',
            CONCAT('status=', OLD.status),
            CONCAT('status=', NEW.status),
            CONCAT('Appointment APT-', LPAD(NEW.appointment_id, 3, '0'),
                   ' status changed: ', OLD.status, ' → ', NEW.status)
        );
    END IF;
END //
DELIMITER ;

-- Trigger 3: Log new patients
DROP TRIGGER IF EXISTS trg_patient_insert;
DELIMITER //
CREATE TRIGGER trg_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (action_type, table_name, record_id, performed_by, new_values, description)
    VALUES (
        'INSERT',
        'patients',
        NEW.patient_id,
        'system',
        CONCAT('name=', NEW.full_name, ', phone=', NEW.phone),
        CONCAT('New patient registered: ', NEW.full_name)
    );
END //
DELIMITER ;

-- Trigger 4: Log new medical records
DROP TRIGGER IF EXISTS trg_medical_record_insert;
DELIMITER //
CREATE TRIGGER trg_medical_record_insert
AFTER INSERT ON medical_records
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (action_type, table_name, record_id, performed_by, new_values, description)
    VALUES (
        'INSERT',
        'medical_records',
        NEW.record_id,
        'doctor',
        CONCAT('appointment_id=', NEW.appointment_id, ', diagnosis=', LEFT(NEW.diagnosis, 100)),
        CONCAT('Medical record created for appointment #', NEW.appointment_id)
    );
END //
DELIMITER ;

-- Trigger 5: Log feedback submissions
DROP TRIGGER IF EXISTS trg_feedback_insert;
DELIMITER //
CREATE TRIGGER trg_feedback_insert
AFTER INSERT ON feedback
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (action_type, table_name, record_id, performed_by, new_values, description)
    VALUES (
        'INSERT',
        'feedback',
        NEW.feedback_id,
        'patient',
        CONCAT('rating=', NEW.rating, ', appointment_id=', NEW.appointment_id),
        CONCAT('Patient feedback submitted: ', NEW.rating, '/5 stars')
    );
END //
DELIMITER ;
