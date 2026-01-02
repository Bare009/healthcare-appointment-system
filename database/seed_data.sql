USE healthcare_db;

-- Insert specializations
INSERT INTO specializations (spec_name, description) VALUES
('Cardiology', 'Heart and cardiovascular system'),
('Neurology', 'Brain and nervous system'),
('Orthopedics', 'Bones, joints, muscles'),
('General Medicine', 'Primary care and general health'),
('Dermatology', 'Skin, hair, nails'),
('ENT', 'Ear, Nose, Throat'),
('Pediatrics', 'Child healthcare'),
('Gastroenterology', 'Digestive system');

-- Insert sample doctors
INSERT INTO doctors (name, phone, qualification, experience_years, spec_id, available) VALUES
('Dr. Ramesh Rao', '9876543210', 'MBBS, MD (Cardiology)', 15, 1, TRUE),
('Dr. Anjali Mehta', '9876543211', 'MBBS, DM (Neurology)', 12, 2, TRUE),
('Dr. Vikram Singh', '9876543212', 'MBBS, MS (Orthopedics)', 10, 3, TRUE),
('Dr. Suresh Kumar', '9876543213', 'MBBS, MD (General Medicine)', 8, 4, TRUE),
('Dr. Neha Gupta', '9876543214', 'MBBS, MD (Dermatology)', 7, 5, TRUE),
('Dr. Kavita Joshi', '9876543215', 'MBBS, MS (ENT)', 9, 6, TRUE),
('Dr. Priya Sharma', '9876543216', 'MBBS, MD (General Medicine)', 6, 4, TRUE),
('Dr. Arun Reddy', '9876543217', 'MBBS, DM (Cardiology)', 14, 1, TRUE);

-- Insert reference diseases
INSERT INTO diseases (disease_name, description, typical_urgency) VALUES
('Myocardial Infarction', 'Heart attack', 10),
('Acute Migraine', 'Severe headache', 7),
('Hypertension', 'High blood pressure', 5),
('Common Cold', 'Upper respiratory infection', 2),
('Allergic Rhinitis', 'Seasonal allergies', 2),
('Osteoarthritis', 'Joint degeneration', 4),
('Gastritis', 'Stomach inflammation', 5);

-- Verify insertions
SELECT COUNT(*) as doctor_count FROM doctors;
SELECT COUNT(*) as specialization_count FROM specializations;
