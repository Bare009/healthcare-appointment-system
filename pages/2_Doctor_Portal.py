"""
Doctor Portal
Login and view appointments assigned to the logged-in doctor
"""

import streamlit as st
from datetime import date, timedelta
from database.connection import initialize_pool
from services.appointment_service import (
    get_appointments_by_doctor, get_doctor_by_name, update_appointment_status
)
from services.medical_service import (
    create_medical_record, add_prescriptions_bulk,
    get_medical_record_by_appointment, get_prescriptions_by_appointment,
    get_doctor_avg_rating
)
from services.audit_service import log_action
from services.gemini_service import get_urgency_label, get_urgency_color

# Page config
st.set_page_config(
    page_title="Doctor Portal",
    page_icon="👨‍⚕️",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    initialize_pool()
    return True

init_database()

# ── Doctor credentials (lab project – hardcoded) ──
DOCTOR_CREDENTIALS = {
    "Dr. Anjali Mehta":  "anjali@123",
    "Dr. Arun Reddy":    "arun@123",
    "Dr. Kavita Joshi":  "kavita@123",
    "Dr. Neha Gupta":    "neha@123",
    "Dr. Priya Sharma":  "priya@123",
    "Dr. Ramesh Rao":    "ramesh@123",
    "Dr. Suresh Kumar":  "suresh@123",
    "Dr. Vikram Singh":  "vikram@123",
}

# ── Custom CSS ──
st.markdown("""
    <style>
    .doctor-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0D47A1, #1976D2, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.2rem 0 0.8rem;
        margin-bottom: 0.5rem;
    }
    .header-line {
        height: 4px;
        background: linear-gradient(90deg, transparent, #1976D2, #42A5F5, #1976D2, transparent);
        border: none;
        border-radius: 2px;
        margin-bottom: 1.8rem;
    }
    .login-box {
        max-width: 420px;
        margin: 3rem auto;
        padding: 2rem;
        border: 1px solid #ddd;
        border-radius: 12px;
        background-color: #FAFAFA;
    }
    .welcome-box {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 40%, #1E88E5 100%);
        border-radius: 14px;
        margin-bottom: 1.8rem;
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(13,71,161,0.35);
    }
    .welcome-box h3 {
        margin: 0 0 0.4rem 0;
        font-size: 1.6rem;
        color: #ffffff;
    }
    .welcome-box p {
        margin: 0;
        font-size: 1.05rem;
        color: #BBDEFB;
    }
    .welcome-box strong {
        color: #ffffff;
    }
    .stat-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-box {
        flex: 1;
        padding: 1.2rem 1rem;
        border-radius: 12px;
        text-align: center;
        color: #fff;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }
    .stat-box .stat-num  { font-size: 2.2rem; font-weight: 800; }
    .stat-box .stat-label { font-size: 0.9rem; opacity: 0.9; margin-top: 2px; }
    .stat-total  { background: linear-gradient(135deg, #1565C0, #42A5F5); }
    .stat-high   { background: linear-gradient(135deg, #C62828, #EF5350); }
    .stat-medium { background: linear-gradient(135deg, #E65100, #FFA726); }
    .stat-low    { background: linear-gradient(135deg, #2E7D32, #66BB6A); }
    .apt-card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        background-color: white;
    }
    .apt-high  { border-left: 6px solid #F44336; background-color: #FFEBEE; }
    .apt-med   { border-left: 6px solid #FF9800; background-color: #FFF3E0; }
    .apt-low   { border-left: 6px solid #4CAF50; background-color: #E8F5E9; }
    </style>
""", unsafe_allow_html=True)

# ╭───────────────────────────────────────────────╮
# │  SESSION STATE                                 │
# ╰───────────────────────────────────────────────╯
if "doctor_logged_in" not in st.session_state:
    st.session_state.doctor_logged_in = False
if "doctor_name" not in st.session_state:
    st.session_state.doctor_name = None
if "doctor_info" not in st.session_state:
    st.session_state.doctor_info = None


def do_login(name, password):
    """Validate credentials and set session state."""
    if name in DOCTOR_CREDENTIALS and DOCTOR_CREDENTIALS[name] == password:
        doctor_info = get_doctor_by_name(name)
        if doctor_info:
            st.session_state.doctor_logged_in = True
            st.session_state.doctor_name = name
            st.session_state.doctor_info = doctor_info
            return True
    return False


def do_logout():
    st.session_state.doctor_logged_in = False
    st.session_state.doctor_name = None
    st.session_state.doctor_info = None


# ╭───────────────────────────────────────────────╮
# │  LOGIN PAGE                                    │
# ╰───────────────────────────────────────────────╯
if not st.session_state.doctor_logged_in:

    st.markdown('<div class="doctor-header">👨‍⚕️ Doctor Portal – Login</div>', unsafe_allow_html=True)

    # Centre the form visually
    _left, center, _right = st.columns([1, 1.5, 1])
    with center:
        st.markdown("#### Sign in with your credentials")

        with st.form("doctor_login_form"):
            doctor_name = st.selectbox(
                "Select your name",
                options=list(DOCTOR_CREDENTIALS.keys()),
                index=0,
            )
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🔑 Login", use_container_width=True, type="primary")

        if login_btn:
            if do_login(doctor_name, password):
                st.rerun()
            else:
                st.error("❌ Invalid password. Please try again.")

    st.stop()  # Nothing more renders until logged in


# ╭───────────────────────────────────────────────╮
# │  DOCTOR DASHBOARD (authenticated)              │
# ╰───────────────────────────────────────────────╯
doctor = st.session_state.doctor_info

# ── Sidebar ──
with st.sidebar:
    st.markdown(f"### 👨‍⚕️ {st.session_state.doctor_name}")
    st.markdown(f"**{doctor['specialization']}**")
    st.markdown(f"🎓 {doctor['qualification']}")
    st.markdown(f"📞 {doctor['phone']}")
    st.markdown(f"🏅 {doctor['experience_years']} yrs experience")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        do_logout()
        st.rerun()

st.markdown(f'<div class="doctor-header">👨‍⚕️ Doctor Dashboard – {st.session_state.doctor_name}</div>', unsafe_allow_html=True)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# Welcome banner
st.markdown(f"""
<div class="welcome-box">
    <h3>👋 Welcome back, {st.session_state.doctor_name}!</h3>
    <p>🏥 <strong>{doctor['specialization']}</strong> &nbsp;&bull;&nbsp;
       🎓 <strong>{doctor['qualification']}</strong> &nbsp;&bull;&nbsp;
       🏅 <strong>{doctor['experience_years']} years</strong> experience</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ──
st.markdown("### 🔍 Filter Your Appointments")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    date_options = {
        "Today": date.today(),
        "Tomorrow": date.today() + timedelta(days=1),
        "This Week": None,          # None = no date filter
    }
    sel_date_label = st.selectbox("📅 Date", list(date_options.keys()))
    date_filter = date_options[sel_date_label]

with col_f2:
    status_filter = st.selectbox("📌 Status", ["All", "Confirmed", "Pending", "Completed", "Cancelled"])

with col_f3:
    view_mode = st.selectbox("👁️ View", ["Cards", "Table"])

if st.button("🔃 Refresh", use_container_width=False):
    st.rerun()

st.divider()

# ── Fetch appointments ──
appointments = get_appointments_by_doctor(
    doctor_id=doctor['doctor_id'],
    date_filter=date_filter,
    status_filter=status_filter,
)

# ── Quick stats ──
total = len(appointments)
high = sum(1 for a in appointments if a['urgency_level'] >= 8)
medium = sum(1 for a in appointments if 4 <= a['urgency_level'] < 8)
low = sum(1 for a in appointments if a['urgency_level'] < 4)

st.markdown(f"""
<div class="stat-row">
    <div class="stat-box stat-total">
        <div class="stat-num">{total}</div>
        <div class="stat-label">Total Appointments</div>
    </div>
    <div class="stat-box stat-high">
        <div class="stat-num">{high}</div>
        <div class="stat-label">🔴 High Priority</div>
    </div>
    <div class="stat-box stat-medium">
        <div class="stat-num">{medium}</div>
        <div class="stat-label">🟡 Medium Priority</div>
    </div>
    <div class="stat-box stat-low">
        <div class="stat-num">{low}</div>
        <div class="stat-label">🟢 Low Priority</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown(f"### 📋 Your Appointments ({total})")

if not appointments:
    st.info("ℹ️ No appointments found for the selected filters.")
else:
    if view_mode == "Cards":
        for idx, apt in enumerate(appointments):
            aid = apt['appointment_id']
            urg = apt['urgency_level']
            if urg >= 8:
                card_cls, urg_icon = "apt-high", "🔴"
            elif urg >= 4:
                card_cls, urg_icon = "apt-med", "🟡"
            else:
                card_cls, urg_icon = "apt-low", "🟢"

            with st.container():
                st.markdown(f'<div class="apt-card {card_cls}">', unsafe_allow_html=True)

                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"### {apt['appointment_code']}")
                    st.markdown(
                        f"**👤 Patient:** {apt['patient_name']} &nbsp;|&nbsp; "
                        f"**Age:** {apt['age']} &nbsp;|&nbsp; **Gender:** {apt['gender']}"
                    )
                    st.markdown(f"**📱 Phone:** {apt['phone']}")
                with col_b:
                    st.markdown(f"### {urg_icon} {urg}/10")
                    st.markdown(f"**Status:** {apt['status']}")
                    st.markdown(f"**Mode:** {apt['mode']}")

                with st.expander("🩺 Full Details"):
                    det1, det2 = st.columns(2)
                    with det1:
                        st.markdown(f"**Symptoms:**\n\n{apt['symptom_text']}")
                        if apt.get('allergies') and apt['allergies'] != 'None':
                            st.markdown(f"**⚠️ Allergies:** {apt['allergies']}")
                    with det2:
                        st.markdown(f"**🤖 AI Diagnosis:** {apt['predicted_disease']} ({apt['probability']}%)")
                        st.markdown(f"**Urgency Reason:** {apt['urgency_reason']}")
                        st.markdown(f"**📅 Date:** {apt['appointment_date']}")
                        st.markdown(f"**🕐 Time:** {apt['appointment_time']}")

                # ── Status Update Buttons ──
                if apt['status'] in ('Confirmed', 'Pending'):
                    st.markdown("---")
                    act1, act2, act3 = st.columns(3)
                    with act1:
                        if st.button("✅ Mark Completed", key=f"comp_{aid}", use_container_width=True):
                            update_appointment_status(aid, 'Completed')
                            log_action('UPDATE', 'appointments', aid,
                                       st.session_state.doctor_name,
                                       f'status={apt["status"]}', 'status=Completed',
                                       f'{apt["appointment_code"]} marked Completed')
                            st.rerun()
                    with act2:
                        if st.button("❌ Cancel", key=f"cancel_{aid}", use_container_width=True):
                            update_appointment_status(aid, 'Cancelled')
                            log_action('UPDATE', 'appointments', aid,
                                       st.session_state.doctor_name,
                                       f'status={apt["status"]}', 'status=Cancelled',
                                       f'{apt["appointment_code"]} cancelled by doctor')
                            st.rerun()
                    with act3:
                        if st.button("🚫 No-show", key=f"noshow_{aid}", use_container_width=True):
                            update_appointment_status(aid, 'Cancelled')
                            log_action('UPDATE', 'appointments', aid,
                                       st.session_state.doctor_name,
                                       f'status={apt["status"]}', 'status=Cancelled',
                                       f'{apt["appointment_code"]} marked No-show')
                            st.rerun()

                # ── Post-Consultation (only for Completed) ──
                if apt['status'] == 'Completed':
                    existing_record = get_medical_record_by_appointment(aid)
                    if existing_record:
                        with st.expander("📋 View Medical Record & Prescriptions"):
                            st.success(f"**Final Diagnosis:** {existing_record['diagnosis']}")
                            if existing_record.get('notes'):
                                st.info(f"**Notes:** {existing_record['notes']}")
                            prescriptions = get_prescriptions_by_appointment(aid)
                            if prescriptions:
                                st.markdown("**💊 Prescriptions:**")
                                for rx in prescriptions:
                                    st.markdown(f"- **{rx['medicine_name']}** — {rx['dosage']} — {rx['duration']}")
                            else:
                                st.caption("No prescriptions added.")
                    else:
                        with st.expander("📝 Add Medical Record & Prescription"):
                            with st.form(key=f"record_form_{aid}"):
                                final_diag = st.text_area("Final Diagnosis *", key=f"diag_{aid}",
                                                          placeholder="Enter your final diagnosis after consultation")
                                doc_notes = st.text_area("Doctor Notes", key=f"notes_{aid}",
                                                         placeholder="Additional observations (optional)")
                                st.markdown("**💊 Prescriptions** (up to 5)")
                                rx_list = []
                                for i in range(1, 6):
                                    rc1, rc2, rc3 = st.columns(3)
                                    with rc1:
                                        med = st.text_input(f"Medicine {i}", key=f"med_{aid}_{i}")
                                    with rc2:
                                        dos = st.text_input(f"Dosage {i}", key=f"dos_{aid}_{i}",
                                                            placeholder="e.g. 500mg")
                                    with rc3:
                                        dur = st.text_input(f"Duration {i}", key=f"dur_{aid}_{i}",
                                                            placeholder="e.g. 7 days")
                                    if med:
                                        rx_list.append({'medicine_name': med, 'dosage': dos, 'duration': dur})

                                submit_record = st.form_submit_button("💾 Save Medical Record",
                                                                      use_container_width=True, type="primary")
                            if submit_record:
                                if not final_diag.strip():
                                    st.error("❌ Final diagnosis is required.")
                                else:
                                    record_id = create_medical_record(aid, final_diag.strip(), doc_notes.strip())
                                    if record_id:
                                        if rx_list:
                                            add_prescriptions_bulk(record_id, rx_list)
                                        log_action('INSERT', 'medical_records', record_id,
                                                   st.session_state.doctor_name,
                                                   description=f'Medical record created for {apt["appointment_code"]}')
                                        st.success("✅ Medical record saved!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to save medical record.")

                st.markdown('</div>', unsafe_allow_html=True)

    else:  # Table view
        import pandas as pd

        df = pd.DataFrame(appointments)
        display_df = df[[
            'appointment_code', 'patient_name', 'age', 'gender', 'phone',
            'urgency_level', 'predicted_disease', 'probability',
            'appointment_date', 'appointment_time', 'status', 'mode'
        ]].copy()

        display_df.columns = [
            'ID', 'Patient', 'Age', 'Gender', 'Phone',
            'Urgency', 'Diagnosis', 'Confidence %',
            'Date', 'Time', 'Status', 'Mode'
        ]

        def color_urgency(val):
            if val >= 8:
                return 'background-color: #FFEBEE'
            elif val >= 4:
                return 'background-color: #FFF3E0'
            return 'background-color: #E8F5E9'

        styled = display_df.style.applymap(color_urgency, subset=['Urgency'])
        st.dataframe(styled, use_container_width=True, height=500)

# ── Footer ──
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #888;'>
    Doctor Portal &nbsp;|&nbsp; {date.today().strftime('%B %d, %Y')} &nbsp;|&nbsp;
    Healthcare Appointment System
</div>
""", unsafe_allow_html=True)
