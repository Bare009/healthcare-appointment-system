"""
Patient Portal
Login, view appointment history, cancel/reschedule, view prescriptions, give feedback
"""

import streamlit as st
from datetime import date, timedelta
from database.connection import initialize_pool
from services.patient_service import (
    get_patient_by_phone, verify_patient_login,
    patient_has_password, set_patient_password
)
from services.appointment_service import (
    get_patient_appointments, cancel_appointment, reschedule_appointment
)
from services.medical_service import (
    get_prescriptions_by_appointment, get_medical_record_by_appointment,
    submit_feedback, check_feedback_exists
)
from services.audit_service import log_action

# Page config
st.set_page_config(page_title="Patient Portal", page_icon="👤", layout="wide")

@st.cache_resource
def init_database():
    initialize_pool()
    return True

init_database()

# ── CSS ──
st.markdown("""
<style>
.patient-header {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, #00695C, #00897B, #4DB6AC);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; padding: 1rem 0 0.6rem; margin-bottom: 0.4rem;
}
.header-line {
    height: 4px;
    background: linear-gradient(90deg, transparent, #00897B, #4DB6AC, #00897B, transparent);
    border: none; border-radius: 2px; margin-bottom: 1.5rem;
}
.welcome-banner {
    padding: 1.4rem 2rem;
    background: linear-gradient(135deg, #00695C 0%, #00897B 50%, #26A69A 100%);
    border-radius: 14px; margin-bottom: 1.5rem;
    color: #fff; box-shadow: 0 4px 14px rgba(0,105,92,0.30);
}
.welcome-banner h3 { margin: 0 0 0.3rem; color: #fff; font-size: 1.5rem; }
.welcome-banner p  { margin: 0; color: #B2DFDB; font-size: 1rem; }
.welcome-banner strong { color: #fff; }
.stat-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat-box { flex:1; padding:1.1rem 0.8rem; border-radius:12px;
            text-align:center; color:#fff; box-shadow:0 3px 10px rgba(0,0,0,0.13); }
.stat-box .stat-num  { font-size:2rem; font-weight:800; }
.stat-box .stat-label{ font-size:0.85rem; opacity:0.9; }
.sb-total   { background: linear-gradient(135deg,#00695C,#4DB6AC); }
.sb-active  { background: linear-gradient(135deg,#1565C0,#42A5F5); }
.sb-done    { background: linear-gradient(135deg,#2E7D32,#66BB6A); }
.sb-cancel  { background: linear-gradient(135deg,#C62828,#EF5350); }
.apt-card { border:1px solid #ddd; border-radius:12px; padding:1.2rem;
            margin:0.6rem 0; background:#fff; }
.ac-confirmed { border-left:6px solid #1976D2; }
.ac-completed { border-left:6px solid #4CAF50; }
.ac-cancelled { border-left:6px solid #9E9E9E; }
.ac-pending   { border-left:6px solid #FF9800; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
for key, default in [("patient_logged_in", False), ("patient_info", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


def patient_logout():
    st.session_state.patient_logged_in = False
    st.session_state.patient_info = None


# ╭────────────────────────────────────────╮
# │  LOGIN / REGISTER                       │
# ╰────────────────────────────────────────╯
if not st.session_state.patient_logged_in:
    st.markdown('<div class="patient-header">👤 Patient Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Set Password (First Time)"])

    with tab_login:
        with st.form("patient_login"):
            phone = st.text_input("Phone Number", placeholder="Enter your registered phone number")
            pwd = st.text_input("Password", type="password")
            btn = st.form_submit_button("Login", use_container_width=True, type="primary")
        if btn:
            if not phone or not pwd:
                st.error("Please fill in both fields.")
            else:
                patient = verify_patient_login(phone, pwd)
                if patient:
                    st.session_state.patient_logged_in = True
                    st.session_state.patient_info = patient
                    log_action('LOGIN', 'patients', patient['patient_id'],
                               patient['full_name'], description='Patient logged in')
                    st.rerun()
                else:
                    st.error("❌ Invalid phone number or password.")

    with tab_register:
        st.info("If you've booked an appointment but haven't set a password yet, do it here.")
        with st.form("patient_register"):
            reg_phone = st.text_input("Registered Phone Number", placeholder="10-digit number")
            new_pwd = st.text_input("Create Password", type="password")
            confirm_pwd = st.text_input("Confirm Password", type="password")
            reg_btn = st.form_submit_button("Set Password", use_container_width=True, type="primary")
        if reg_btn:
            if not reg_phone or not new_pwd:
                st.error("Please fill all fields.")
            elif new_pwd != confirm_pwd:
                st.error("Passwords do not match.")
            elif len(new_pwd) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                patient = get_patient_by_phone(reg_phone)
                if not patient:
                    st.error("❌ No patient found with this phone number. Book an appointment first.")
                elif patient_has_password(reg_phone):
                    st.warning("⚠️ Password already set. Use Login tab.")
                else:
                    set_patient_password(patient['patient_id'], new_pwd)
                    st.success("✅ Password set! You can now login.")

    st.stop()


# ╭────────────────────────────────────────╮
# │  PATIENT DASHBOARD (authenticated)      │
# ╰────────────────────────────────────────╯
patient = st.session_state.patient_info

with st.sidebar:
    st.markdown(f"### 👤 {patient['full_name']}")
    st.markdown(f"📱 {patient['phone']}")
    st.markdown(f"🎂 Age: {patient['age']} | {patient['gender']}")
    if patient.get('allergies') and patient['allergies'] != 'None':
        st.markdown(f"⚠️ Allergies: {patient['allergies']}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        patient_logout()
        st.rerun()

st.markdown(f'<div class="patient-header">👤 My Health Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="welcome-banner">
    <h3>👋 Hello, {patient['full_name']}!</h3>
    <p>📱 <strong>{patient['phone']}</strong> &bull;
       🎂 <strong>{patient['age']} yrs</strong> &bull;
       {patient['gender']}</p>
</div>
""", unsafe_allow_html=True)

# ── Fetch appointments ──
appointments = get_patient_appointments(patient['patient_id'])

total = len(appointments)
active = sum(1 for a in appointments if a['status'] in ('Confirmed', 'Pending'))
completed = sum(1 for a in appointments if a['status'] == 'Completed')
cancelled = sum(1 for a in appointments if a['status'] == 'Cancelled')

st.markdown(f"""
<div class="stat-row">
    <div class="stat-box sb-total"><div class="stat-num">{total}</div><div class="stat-label">Total</div></div>
    <div class="stat-box sb-active"><div class="stat-num">{active}</div><div class="stat-label">Active</div></div>
    <div class="stat-box sb-done"><div class="stat-num">{completed}</div><div class="stat-label">Completed</div></div>
    <div class="stat-box sb-cancel"><div class="stat-num">{cancelled}</div><div class="stat-label">Cancelled</div></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Tabs: Upcoming | History ──
tab_upcoming, tab_history = st.tabs(["📅 Upcoming / Active", "📜 History"])

# helper
def _status_class(status):
    return {"Confirmed": "ac-confirmed", "Pending": "ac-pending",
            "Completed": "ac-completed", "Cancelled": "ac-cancelled"}.get(status, "")

def _status_icon(status):
    return {"Confirmed": "🔵", "Pending": "🟠",
            "Completed": "✅", "Cancelled": "⛔"}.get(status, "")


with tab_upcoming:
    upcoming = [a for a in appointments if a['status'] in ('Confirmed', 'Pending')]
    if not upcoming:
        st.info("No upcoming appointments.")
    for apt in upcoming:
        aid = apt['appointment_id']
        with st.container():
            st.markdown(f'<div class="apt-card {_status_class(apt["status"])}">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### {apt['appointment_code']}")
                st.markdown(f"**👨‍⚕️ Doctor:** {apt['doctor_name']} ({apt['specialization']})")
                st.markdown(f"**📅** {apt['appointment_date']} at **🕐** {apt['appointment_time']}  |  **Mode:** {apt['mode']}")
            with c2:
                st.markdown(f"### {_status_icon(apt['status'])} {apt['status']}")
                st.markdown(f"**Urgency:** {apt['urgency_level']}/10")

            with st.expander("🩺 Details"):
                st.markdown(f"**Symptoms:** {apt['symptom_text']}")
                st.markdown(f"**🤖 AI Diagnosis:** {apt['predicted_disease']} ({apt['probability']}%)")
                st.markdown(f"**Reason:** {apt['urgency_reason']}")

            # Cancel / Reschedule
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("❌ Cancel Appointment", key=f"pcancel_{aid}", use_container_width=True):
                    cancel_appointment(aid)
                    log_action('UPDATE', 'appointments', aid, patient['full_name'],
                               f'status={apt["status"]}', 'status=Cancelled',
                               f'Patient cancelled {apt["appointment_code"]}')
                    st.rerun()
            with ac2:
                default_date = max(apt['appointment_date'], date.today())
                new_date = st.date_input("Reschedule to", value=default_date,
                                         min_value=date.today(),
                                         max_value=date.today() + timedelta(days=14),
                                         key=f"resched_{aid}")
                if new_date != apt['appointment_date']:
                    if st.button("📅 Confirm Reschedule", key=f"rconf_{aid}", use_container_width=True):
                        reschedule_appointment(aid, new_date)
                        log_action('UPDATE', 'appointments', aid, patient['full_name'],
                                   f'date={apt["appointment_date"]}', f'date={new_date}',
                                   f'Patient rescheduled {apt["appointment_code"]}')
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


with tab_history:
    past = [a for a in appointments if a['status'] in ('Completed', 'Cancelled')]
    if not past:
        st.info("No past appointments yet.")
    for apt in past:
        aid = apt['appointment_id']
        with st.container():
            st.markdown(f'<div class="apt-card {_status_class(apt["status"])}">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### {apt['appointment_code']}")
                st.markdown(f"**👨‍⚕️** {apt['doctor_name']} ({apt['specialization']})  |  **📅** {apt['appointment_date']}")
                st.markdown(f"**🤖 Diagnosis:** {apt['predicted_disease']}")
            with c2:
                st.markdown(f"### {_status_icon(apt['status'])} {apt['status']}")

            # Medical record + prescriptions (for Completed)
            if apt['status'] == 'Completed':
                record = get_medical_record_by_appointment(aid)
                if record:
                    with st.expander("📋 Medical Record & Prescriptions"):
                        st.success(f"**Final Diagnosis:** {record['diagnosis']}")
                        if record.get('notes'):
                            st.info(f"**Doctor Notes:** {record['notes']}")
                        rxs = get_prescriptions_by_appointment(aid)
                        if rxs:
                            st.markdown("**💊 Prescriptions:**")
                            for rx in rxs:
                                st.markdown(f"- **{rx['medicine_name']}** — {rx['dosage']} — {rx['duration']}")

                # Feedback
                if apt['status'] == 'Completed':
                    has_fb = check_feedback_exists(patient['patient_id'], aid)
                    if has_fb:
                        st.caption("✅ You have already submitted feedback for this appointment.")
                    else:
                        with st.expander("⭐ Give Feedback"):
                            with st.form(key=f"fb_{aid}"):
                                rating = st.slider("Rating", 1, 5, 4, key=f"rate_{aid}")
                                comment = st.text_area("Comment (optional)", key=f"comm_{aid}")
                                fb_btn = st.form_submit_button("Submit Feedback", use_container_width=True)
                            if fb_btn:
                                submit_feedback(patient['patient_id'], aid, rating, comment)
                                st.success("✅ Thank you for your feedback!")
                                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ──
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:#888;'>
    Patient Portal &nbsp;|&nbsp; {date.today().strftime('%B %d, %Y')} &nbsp;|&nbsp;
    Healthcare Appointment System
</div>
""", unsafe_allow_html=True)
