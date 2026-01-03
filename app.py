"""
AI-Driven Smart Healthcare Appointment System
Main Page: Patient Registration & Symptom Analysis
"""

import streamlit as st
from datetime import date, timedelta
from database.connection import initialize_pool
from services.patient_service import create_patient, get_patient_by_phone
from services.symptom_service import save_symptom
from services.gemini_service import analyze_symptoms, get_urgency_label, get_urgency_color
from services.appointment_service import (
    save_prediction, find_available_doctor, create_appointment,
    get_all_specializations
)

# Page configuration
st.set_page_config(
    page_title="Healthcare Appointment System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
@st.cache_resource
def init_database():
    """Initialize database connection pool (cached)"""
    initialize_pool()
    return True

init_database()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #0066CC;
        margin-bottom: 2rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1.5rem;
        background-color: #D4EDDA;
        border-left: 5px solid #28A745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .urgency-high {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        border-radius: 5px;
    }
    .urgency-medium {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 5px;
    }
    .urgency-low {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
    }
    .info-box {
        padding: 1rem;
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 AI-Driven Smart Healthcare & Diagnosis System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time Appointment Scheduling with AI-Powered Urgency Analysis</div>', unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
    st.markdown("### 📋 How It Works")
    st.markdown("""
    1. **Enter** patient details
    2. **Describe** symptoms in detail
    3. **AI analyzes** urgency level
    4. **Auto-assign** doctor by priority
    5. **View** appointment queue →
    """)
    st.divider()
    st.markdown("### 🎯 Features")
    st.markdown("""
    - ✅ AI-powered diagnosis
    - ✅ Urgency-based scheduling
    - ✅ Smart doctor assignment
    - ✅ Real-time queue updates
    """)

# Main form
st.markdown("## 📝 Patient Registration & Symptom Submission")

with st.form("patient_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Patient Information")
        first_name = st.text_input("First Name *", placeholder="Enter first name")
        last_name = st.text_input("Last Name", placeholder="Enter last name (optional)")
        age = st.number_input("Age *", min_value=1, max_value=120, value=25)
        
    with col2:
        st.markdown("#### Contact Details")
        gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
        phone = st.text_input("Phone Number *", placeholder="10-digit number", max_chars=15)
        allergies = st.text_area("Known Allergies", placeholder="None", height=80)
    
    st.divider()
    
    # Symptom section
    st.markdown("#### 🩺 Symptom Description")
    st.info("💡 Provide detailed symptoms for accurate AI analysis (minimum 50 characters)")
    
    symptom_text = st.text_area(
        "Describe your symptoms in detail *",
        placeholder="Example: I have been experiencing severe chest pain for the last 2 hours. The pain is radiating to my left arm and I'm feeling nauseous. I'm also sweating excessively...",
        height=150,
        help="Include: What you're feeling, how long, severity, any related symptoms"
    )
    
    # Character counter
    char_count = len(symptom_text.strip())
    if char_count < 50:
        st.warning(f"⚠️ Please provide more details ({char_count}/50 characters)")
    else:
        st.success(f"✅ Sufficient detail provided ({char_count} characters)")
    
    st.divider()
    
    # Appointment preferences
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Appointment Preferences")
        specializations = get_all_specializations()
        preferred_spec = st.selectbox(
            "Preferred Specialization",
            ["General Medicine"] + specializations,
            help="AI may suggest different specialization based on symptoms"
        )
    
    with col4:
        st.markdown("#### Schedule")
        min_date = date.today()
        max_date = date.today() + timedelta(days=7)
        appointment_date = st.date_input(
            "Preferred Date",
            value=date.today(),
            min_value=min_date,
            max_value=max_date
        )
        
        consultation_mode = st.radio("Consultation Mode", ["Offline", "Online"], horizontal=True)
    
    # Submit button
    st.markdown("")
    submitted = st.form_submit_button("🔍 Analyze Symptoms & Book Appointment", use_container_width=True, type="primary")

# Process form submission
if submitted:
    # Validation
    if not first_name or not phone or not symptom_text.strip():
        st.error("❌ Please fill all required fields (marked with *)")
    elif char_count < 50:
        st.error("❌ Symptom description too short. Please provide at least 50 characters.")
    elif not phone.isdigit() or len(phone) < 10:
        st.error("❌ Please enter a valid 10-digit phone number")
    else:
        # Show processing steps
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Create patient
            status_text.text("Step 1/5: Saving patient information...")
            progress_bar.progress(20)
            
            patient_id = create_patient(
                first_name=first_name,
                last_name=last_name or "",
                gender=gender,
                age=age,
                phone=phone,
                allergies=allergies or "None"
            )
            
            if not patient_id:
                st.error("❌ Failed to create patient record. Phone number may already exist.")
                st.stop()
            
            # Step 2: Save symptom
            status_text.text("Step 2/5: Recording symptoms...")
            progress_bar.progress(40)
            
            symptom_id = save_symptom(patient_id, symptom_text.strip())
            
            if not symptom_id:
                st.error("❌ Failed to save symptoms")
                st.stop()
            
            # Step 3: AI Analysis
            status_text.text("Step 3/5: Analyzing symptoms with AI... (may take 10-15 seconds)")
            progress_bar.progress(60)
            
            diagnosis = analyze_symptoms(symptom_text)
            
            if not diagnosis:
                st.error("❌ AI analysis failed")
                st.stop()
            
            # Step 4: Save prediction
            status_text.text("Step 4/5: Saving diagnostic results...")
            progress_bar.progress(80)
            
            prediction_id = save_prediction(symptom_id, diagnosis)
            
            # Step 5: Create appointment
            status_text.text("Step 5/5: Scheduling appointment...")
            progress_bar.progress(90)
            
            # Find available doctor
            doctor = find_available_doctor(preferred_spec, appointment_date)
            
            if not doctor:
                st.warning(f"⚠️ No {preferred_spec} available on {appointment_date}. Trying General Medicine...")
                doctor = find_available_doctor("General Medicine", appointment_date)
            
            if not doctor:
                st.error("❌ No doctors available on selected date. Please try another date.")
                st.stop()
            
            # Create appointment
            appointment_id = create_appointment(
                patient_id=patient_id,
                doctor_id=doctor['doctor_id'],
                symptom_id=symptom_id,
                urgency_level=diagnosis['urgency_level'],
                appointment_date=appointment_date,
                mode=consultation_mode
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Success message
            st.balloons()
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Appointment Booked Successfully!")
            st.markdown(f"**Appointment ID:** APT-{appointment_id:03d}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display AI analysis results
            st.markdown("---")
            st.markdown("## 🤖 AI Diagnostic Analysis")
            
            urgency_level = diagnosis['urgency_level']
            urgency_label = get_urgency_label(urgency_level)
            urgency_emoji = get_urgency_color(urgency_level)
            
            # Urgency-based styling
            if urgency_level >= 8:
                urgency_class = "urgency-high"
            elif urgency_level >= 4:
                urgency_class = "urgency-medium"
            else:
                urgency_class = "urgency-low"
            
            st.markdown(f'<div class="{urgency_class}">', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("### 🔍 Primary Diagnosis")
                st.markdown(f"**Condition:** {diagnosis['predicted_disease']}")
                st.markdown(f"**Confidence:** {diagnosis['probability']}%")
                
                if diagnosis.get('secondary_conditions'):
                    st.markdown("**Alternative Possibilities:**")
                    for cond in diagnosis['secondary_conditions'][:2]:
                        st.markdown(f"- {cond['disease']} ({cond['probability']}%)")
            
            with col_b:
                st.markdown(f"### {urgency_emoji} Urgency Assessment")
                st.markdown(f"**Level:** {urgency_level}/10 - **{urgency_label} PRIORITY**")
                st.markdown(f"**Reason:** {diagnosis.get('urgency_reason', 'Based on symptom analysis')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Appointment details
            st.markdown("---")
            st.markdown("## 📋 Appointment Details")
            
            col_c, col_d = st.columns(2)
            
            with col_c:
                st.markdown(f"""
                **👨‍⚕️ Assigned Doctor:** Dr. {doctor['name']}  
                **🏥 Specialization:** {preferred_spec}  
                **🎓 Qualification:** {doctor['qualification']}  
                """)
            
            with col_d:
                st.markdown(f"""
                **📅 Date:** {appointment_date.strftime('%B %d, %Y')}  
                **🕐 Time:** Will be assigned based on urgency  
                **💻 Mode:** {consultation_mode}  
                """)
            
            st.markdown("---")
            
            # Disclaimer
            st.info("ℹ️ **Disclaimer:** AI analysis is preliminary. Final diagnosis will be provided by the doctor during consultation.")
            
            # Navigation
            st.markdown("")
            st.markdown("### 👉 Next Steps")
            col_nav1, col_nav2 = st.columns(2)
            
            with col_nav1:
                st.page_link("pages/1_Appointments.py", label="📊 View Appointment Queue", icon="📊")
            
            with col_nav2:
                if st.button("🔄 Book Another Appointment", use_container_width=True):
                    st.rerun()
            
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.exception(e)

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.metric("📊 Database Tables", "10")
with col_f2:
    st.metric("🔗 Foreign Keys", "8")
with col_f3:
    st.metric("🤖 AI Model", "Gemini 1.5")

st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Powered by MySQL + Streamlit + Google Gemini AI</p>
    <p style='font-size: 0.9rem;'>DBMS Mini Project - Healthcare Appointment System</p>
</div>
""", unsafe_allow_html=True)
