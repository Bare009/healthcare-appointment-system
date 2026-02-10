"""
Analytics Dashboard
Visual charts and insights across the entire system
Demonstrates: GROUP BY, COUNT, AVG, HAVING, DATE functions, VIEWs, Subqueries
"""

import streamlit as st
import pandas as pd
from datetime import date
from database.connection import initialize_pool
from services.analytics_service import (
    get_overview_counts, get_disease_distribution, get_doctor_workload,
    get_daily_trends, get_urgency_distribution, get_specialization_demand,
    get_gender_age_stats, get_feedback_summary
)

# Page config
st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

@st.cache_resource
def init_database():
    initialize_pool()
    return True

init_database()

# ── CSS ──
st.markdown("""
<style>
.analytics-header {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, #4A148C, #7B1FA2, #CE93D8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; padding: 1rem 0 0.6rem;
}
.header-line {
    height: 4px;
    background: linear-gradient(90deg, transparent, #7B1FA2, #CE93D8, #7B1FA2, transparent);
    border: none; border-radius: 2px; margin-bottom: 1.5rem;
}
.metric-row { display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap; }
.m-box { flex:1; min-width:130px; padding:1.1rem 0.8rem; border-radius:12px;
         text-align:center; color:#fff; box-shadow:0 3px 10px rgba(0,0,0,0.13); }
.m-box .m-num  { font-size:2rem; font-weight:800; }
.m-box .m-label { font-size:0.82rem; opacity:0.9; }
.m1 { background:linear-gradient(135deg,#1565C0,#42A5F5); }
.m2 { background:linear-gradient(135deg,#00695C,#4DB6AC); }
.m3 { background:linear-gradient(135deg,#4A148C,#AB47BC); }
.m4 { background:linear-gradient(135deg,#E65100,#FFA726); }
.m5 { background:linear-gradient(135deg,#2E7D32,#66BB6A); }
.m6 { background:linear-gradient(135deg,#C62828,#EF5350); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="analytics-header">📊 Analytics & Insights Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

if st.button("🔃 Refresh Data"):
    st.rerun()

# ╭─────────────────────────────────────╮
# │  TOP METRIC CARDS                    │
# ╰─────────────────────────────────────╯
counts = get_overview_counts()

st.markdown(f"""
<div class="metric-row">
  <div class="m-box m1"><div class="m-num">{counts['total_patients']}</div><div class="m-label">Patients</div></div>
  <div class="m-box m2"><div class="m-num">{counts['total_appointments']}</div><div class="m-label">Appointments</div></div>
  <div class="m-box m3"><div class="m-num">{counts['total_doctors']}</div><div class="m-label">Doctors</div></div>
  <div class="m-box m4"><div class="m-num">{counts['total_records']}</div><div class="m-label">Medical Records</div></div>
  <div class="m-box m5"><div class="m-num">{counts['total_feedback']}</div><div class="m-label">Feedback</div></div>
  <div class="m-box m6"><div class="m-num">{counts['unique_diseases']}</div><div class="m-label">Unique Diseases</div></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ╭─────────────────────────────────────╮
# │  CHARTS ROW 1: Disease + Urgency     │
# ╰─────────────────────────────────────╯
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🦠 Top Predicted Diseases")
    diseases = get_disease_distribution(10)
    if diseases:
        df_d = pd.DataFrame(diseases)
        st.bar_chart(df_d.set_index('predicted_disease')['occurrence_count'], color="#7B1FA2")
        with st.expander("📋 Details"):
            st.dataframe(df_d, use_container_width=True)
    else:
        st.info("No data yet.")

with col2:
    st.markdown("### ⚠️ Urgency Level Distribution")
    urg = get_urgency_distribution()
    if urg:
        df_u = pd.DataFrame(urg)
        df_u['urgency_level'] = df_u['urgency_level'].astype(str)
        st.bar_chart(df_u.set_index('urgency_level')['count'], color="#E65100")
    else:
        st.info("No data yet.")

st.divider()

# ╭─────────────────────────────────────╮
# │  CHARTS ROW 2: Doctor Workload       │
# ╰─────────────────────────────────────╯
st.markdown("### 👨‍⚕️ Doctor Workload")
workload = get_doctor_workload()
if workload:
    df_w = pd.DataFrame(workload)
    # Stacked-like bar showing total per doctor
    chart_df = df_w[['doctor_name', 'confirmed', 'completed', 'cancelled']].copy()
    chart_df = chart_df.set_index('doctor_name')
    st.bar_chart(chart_df)
    with st.expander("📋 Full Workload Table"):
        st.dataframe(df_w, use_container_width=True)
else:
    st.info("No data yet.")

st.divider()

# ╭─────────────────────────────────────╮
# │  CHARTS ROW 3: Specialization + Demo │
# ╰─────────────────────────────────────╯
col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🏥 Specialization Demand")
    spec = get_specialization_demand()
    if spec:
        df_s = pd.DataFrame(spec)
        st.bar_chart(df_s.set_index('specialization')['appointment_count'], color="#00897B")
    else:
        st.info("No data yet.")

with col4:
    st.markdown("### 👥 Patient Demographics")
    demo = get_gender_age_stats()
    if demo:
        df_g = pd.DataFrame(demo)
        st.dataframe(df_g, use_container_width=True)
    else:
        st.info("No data yet.")

st.divider()

# ╭─────────────────────────────────────╮
# │  CHARTS ROW 4: Trends + Feedback     │
# ╰─────────────────────────────────────╯
col5, col6 = st.columns(2)

with col5:
    st.markdown("### 📈 Daily Appointment Trends")
    trends = get_daily_trends(30)
    if trends:
        df_t = pd.DataFrame(trends)
        df_t['apt_date'] = pd.to_datetime(df_t['apt_date'])
        chart_t = df_t[['apt_date', 'high', 'medium', 'low']].set_index('apt_date')
        st.area_chart(chart_t)
    else:
        st.info("No trend data yet.")

with col6:
    st.markdown("### ⭐ Feedback Summary")
    fb = get_feedback_summary()
    if fb and fb.get('total_feedback', 0) > 0:
        fc1, fc2 = st.columns(2)
        fc1.metric("Average Rating", f"{float(fb['avg_rating'])}/5")
        fc2.metric("Total Reviews", int(fb['total_feedback']))
        fc3, fc4 = st.columns(2)
        fc3.metric("👍 Positive (4-5)", int(fb.get('positive', 0)))
        fc4.metric("👎 Negative (1-2)", int(fb.get('negative', 0)))
    else:
        st.info("No feedback yet.")

st.divider()

# ── DBMS Showcase ──
with st.expander("💾 DBMS Concepts Demonstrated"):
    st.markdown("""
    | Concept | Where Used |
    |---------|-----------|
    | **GROUP BY + COUNT** | Disease distribution, doctor workload, urgency distribution |
    | **AVG / ROUND** | Average urgency, average confidence, average rating |
    | **HAVING** | Specialization demand (filter groups with 0) |
    | **DATE functions** | Daily trends using `DATE_SUB()`, `CURDATE()` |
    | **VIEWs** | `v_doctor_workload`, `v_disease_frequency`, `v_daily_summary` |
    | **Subqueries** | Overview counts from multiple tables |
    | **Multi-table JOINs** | Doctor workload (3 tables), specialization demand (3 tables) |
    | **CASE WHEN** | Status breakdown (confirmed/completed/cancelled) |
    """)

# ── Footer ──
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:#888;'>
    Analytics Dashboard &nbsp;|&nbsp; {date.today().strftime('%B %d, %Y')} &nbsp;|&nbsp;
    Healthcare Appointment System
</div>
""", unsafe_allow_html=True)
