# 🏥 AI-Driven Smart Healthcare & Diagnosis System

A database-driven healthcare appointment system with AI-powered symptom analysis and urgency-based scheduling. 

**Key Features:**

- AI-powered symptom analysis using Google Gemini API
- Automatic urgency scoring (1-10) for appointment prioritization
- Real-time appointment queue with smart doctor assignment
- Complex SQL queries demonstrating 5-table JOINs
- Streamlit-based responsive UI with color-coded priority levels

---

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Git

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/healthcare-appointment-system.git
cd healthcare-appointment-system
```

#### 2. Set Up Python Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Set Up MySQL Database

**Start MySQL and create database:**

```bash
# Login to MySQL
mysql -u root -p
```

**Run the following SQL commands:**

```sql
-- Create database
CREATE DATABASE healthcare_db;

-- Create user and grant privileges
CREATE USER 'healthcare_admin'@'localhost' IDENTIFIED BY 'Admin@123!';
GRANT ALL PRIVILEGES ON healthcare_db.* TO 'healthcare_admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Load the database schema:**

```bash
mysql -u healthcare_admin -p healthcare_db < database/schema.sql
```

**Load sample data (doctors and specializations):**

```bash
mysql -u healthcare_admin -p healthcare_db < database/seed_data.sql
```

**Verify installation:**

```bash
mysql -u healthcare_admin -p healthcare_db -e "SHOW TABLES;"
```

You should see 10 tables listed.

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=healthcare_admin
DB_PASSWORD=Admin@123!
DB_NAME=healthcare_db
DB_PORT=3306

# Google Gemini API Key (get from: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get Gemini API Key:**

1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into `.env` file

#### 5. Test the Backend (Optional but Recommended)

```bash
python test_services.py
```

Expected output: `✅ ALL TESTS PASSED!`

#### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at: [**http://localhost:8501**](http://localhost:8501)

---

## 📱 Using the Application

### Page 1: Patient Registration & Booking

1. Fill in patient details (name, age, gender, phone)
2. Describe symptoms in detail (minimum 50 characters)
3. Select preferred specialization and date
4. Click "Analyze Symptoms & Book Appointment"
5. View AI diagnosis with urgency score
6. Appointment automatically created and prioritized

### Page 2: Appointment Queue (Sidebar Navigation)

1. View all appointments sorted by urgency (High → Medium → Low)
2. Filter by date, urgency level, or specialization
3. Enable auto-refresh for real-time updates
4. View detailed patient information and AI analysis
5. See SQL query demonstrating multi-table JOINs

---

## 🗂️ Project Structure

```
healthcare-appointment-system/
├── app.py                          # Main Streamlit page (Patient input)
├── pages/
│   └── 1_Appointments.py           # Appointment queue dashboard
├── database/
│   ├── schema.sql                  # Table creation scripts
│   ├── seed_data.sql               # Sample doctors data
│   └── connection.py               # MySQL connection pooling
├── services/
│   ├── patient_service.py          # Patient CRUD operations
│   ├── symptom_service.py          # Symptom management
│   ├── gemini_service.py           # AI diagnosis integration
│   └── appointment_service.py      # Appointment scheduling
├── config.py                       # Configuration management
├── .env                            # Environment variables (create this)
├── requirements.txt                # Python dependencies
└── test_services.py                # Backend testing script
```

---

## 🛠️ Troubleshooting

**MySQL Connection Error:**

```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
brew services list          # macOS

# Verify credentials
mysql -u healthcare_admin -p healthcare_db
```

**Gemini API Quota Exceeded:**

- System has intelligent fallback using keyword-based analysis
- Get new API key from https://aistudio.google.com/app/apikey
- Free tier: 15 requests/min, 1500 requests/day

**Port Already in Use:**

```bash
streamlit run app.py --server.port 8502
```

---

## 👥 Authors

- **Nishant Hegde**
- **Suneesh Bare**

---

## 📄 License

This project is developed as part of academic curriculum for educational purposes.

For questions or issues, please open an issue on GitHub.
