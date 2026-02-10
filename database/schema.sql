-- Healthcare Appointment System - Database Schema
USE healthcare_db;

-- Drop existing tables if re-running (careful in production!)
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS specializations;
DROP TABLE IF EXISTS diseases;

-- 1. Specializations (Reference table)
CREATE TABLE specializations (
    spec_id INT PRIMARY KEY AUTO_INCREMENT,
    spec_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 2. Doctors
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    qualification VARCHAR(100),
    experience_years INT CHECK (experience_years >= 0),
    spec_id INT NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (spec_id) REFERENCES specializations(spec_id),
    INDEX idx_specialization (spec_id),
    INDEX idx_availability (available)
);

-- 3. Patients
CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    age INT CHECK (age > 0 AND age < 150),
    phone VARCHAR(15) UNIQUE,
    allergies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone)
);

-- 4. Symptoms (1NF - atomic entries)
CREATE TABLE symptoms (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    symptom_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_submitted (submitted_at)
);

-- 5. Diseases (Reference)
CREATE TABLE diseases (
    disease_id INT PRIMARY KEY AUTO_INCREMENT,
    disease_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    typical_urgency INT CHECK (typical_urgency BETWEEN 1 AND 10)
);

-- 6. Predictions (AI results)
CREATE TABLE predictions (
    prediction_id INT PRIMARY KEY AUTO_INCREMENT,
    symptom_id INT NOT NULL,
    predicted_disease VARCHAR(100) NOT NULL,
    probability DECIMAL(5,2) CHECK (probability BETWEEN 0 AND 100),
    urgency_level INT NOT NULL CHECK (urgency_level BETWEEN 1 AND 10),
    urgency_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id) ON DELETE CASCADE,
    INDEX idx_urgency (urgency_level DESC)
);

-- 7. Appointments (Core table)
CREATE TABLE appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    symptom_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Confirmed',
    mode ENUM('Online', 'Offline') DEFAULT 'Offline',
    urgency_level INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id) ON DELETE CASCADE,
    INDEX idx_urgency_date (urgency_level DESC, appointment_date),
    INDEX idx_doctor_date (doctor_id, appointment_date),
    INDEX idx_status (status),
    UNIQUE KEY unique_doctor_slot (doctor_id, appointment_date, appointment_time)
);

-- 8. Medical Records
CREATE TABLE medical_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT UNIQUE NOT NULL,
    diagnosis TEXT NOT NULL,
    notes TEXT,
    record_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

-- 9. Prescriptions
CREATE TABLE prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    medicine_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    duration VARCHAR(50),
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id) ON DELETE CASCADE
);

-- 10. Feedback
CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    appointment_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    UNIQUE KEY unique_feedback (patient_id, appointment_id)
);

-- Show all tables
SHOW TABLES;
