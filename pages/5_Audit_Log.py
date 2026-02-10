"""
Audit Log Viewer
View all system activity tracked by database triggers
Demonstrates: TRIGGER, TIMESTAMP, INSERT logging, filtering, ORDER BY DESC
"""

import streamlit as st
import pandas as pd
from datetime import date
from database.connection import initialize_pool
from services.audit_service import (
    get_audit_logs, get_audit_action_types,
    get_audit_table_names, get_audit_summary
)

# Page config
st.set_page_config(page_title="Audit Log", page_icon="📝", layout="wide")

@st.cache_resource
def init_database():
    initialize_pool()
    return True

init_database()

# ── CSS ──
st.markdown("""
<style>
.audit-header {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, #BF360C, #E64A19, #FF8A65);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; padding: 1rem 0 0.6rem;
}
.header-line {
    height: 4px;
    background: linear-gradient(90deg, transparent, #E64A19, #FF8A65, #E64A19, transparent);
    border: none; border-radius: 2px; margin-bottom: 1.5rem;
}
.summary-row { display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap; }
.s-box { flex:1; min-width:120px; padding:1rem 0.6rem; border-radius:12px;
         text-align:center; color:#fff; box-shadow:0 3px 10px rgba(0,0,0,0.12); }
.s-box .s-num  { font-size:1.8rem; font-weight:800; }
.s-box .s-label { font-size:0.8rem; opacity:0.9; }
.s-insert  { background:linear-gradient(135deg,#2E7D32,#66BB6A); }
.s-update  { background:linear-gradient(135deg,#1565C0,#42A5F5); }
.s-delete  { background:linear-gradient(135deg,#C62828,#EF5350); }
.s-login   { background:linear-gradient(135deg,#4A148C,#AB47BC); }
.s-other   { background:linear-gradient(135deg,#455A64,#90A4AE); }
.log-row-insert { border-left:4px solid #4CAF50; padding-left:0.8rem; margin:0.3rem 0; }
.log-row-update { border-left:4px solid #2196F3; padding-left:0.8rem; margin:0.3rem 0; }
.log-row-delete { border-left:4px solid #F44336; padding-left:0.8rem; margin:0.3rem 0; }
.log-row-login  { border-left:4px solid #9C27B0; padding-left:0.8rem; margin:0.3rem 0; }
.log-row-other  { border-left:4px solid #9E9E9E; padding-left:0.8rem; margin:0.3rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="audit-header">📝 Audit Log & Activity Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

st.markdown("**Every action in the system is automatically tracked by MySQL triggers.**")

if st.button("🔃 Refresh"):
    st.rerun()

st.divider()

# ╭─────────────────────────────────────╮
# │  SUMMARY CARDS                       │
# ╰─────────────────────────────────────╯
summary = get_audit_summary()
summary_map = {s['action_type']: s['count'] for s in summary}
total_logs = sum(s['count'] for s in summary)

def _get(key):
    return summary_map.get(key, 0)

st.markdown(f"""
<div class="summary-row">
  <div class="s-box s-insert"><div class="s-num">{_get('INSERT')}</div><div class="s-label">INSERTs</div></div>
  <div class="s-box s-update"><div class="s-num">{_get('UPDATE')}</div><div class="s-label">UPDATEs</div></div>
  <div class="s-box s-delete"><div class="s-num">{_get('DELETE')}</div><div class="s-label">DELETEs</div></div>
  <div class="s-box s-login"><div class="s-num">{_get('LOGIN')}</div><div class="s-label">LOGINs</div></div>
  <div class="s-box s-other"><div class="s-num">{total_logs}</div><div class="s-label">Total Logs</div></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ╭─────────────────────────────────────╮
# │  FILTERS                             │
# ╰─────────────────────────────────────╯
st.markdown("### 🔍 Filter Logs")
fc1, fc2, fc3 = st.columns(3)

with fc1:
    action_types = ["All"] + get_audit_action_types()
    action_filter = st.selectbox("Action Type", action_types)

with fc2:
    table_names = ["All"] + get_audit_table_names()
    table_filter = st.selectbox("Table", table_names)

with fc3:
    limit = st.selectbox("Show", [50, 100, 200, 500], index=0)

st.divider()

# ╭─────────────────────────────────────╮
# │  LOG ENTRIES                         │
# ╰─────────────────────────────────────╯
logs = get_audit_logs(
    limit=limit,
    action_filter=action_filter if action_filter != "All" else None,
    table_filter=table_filter if table_filter != "All" else None
)

st.markdown(f"### 📋 Activity Log ({len(logs)} entries)")

tab_cards, tab_table = st.tabs(["🃏 Timeline View", "📊 Table View"])

with tab_cards:
    if not logs:
        st.info("No audit log entries found.")
    else:
        for log in logs:
            action = log['action_type']
            css_cls = {
                'INSERT': 'log-row-insert', 'UPDATE': 'log-row-update',
                'DELETE': 'log-row-delete', 'LOGIN': 'log-row-login'
            }.get(action, 'log-row-other')
            icon = {
                'INSERT': '🟢', 'UPDATE': '🔵', 'DELETE': '🔴', 'LOGIN': '🟣'
            }.get(action, '⚪')

            st.markdown(f'<div class="{css_cls}">', unsafe_allow_html=True)

            ts = log['performed_at'].strftime('%Y-%m-%d %H:%M:%S') if log['performed_at'] else ''
            st.markdown(
                f"{icon} **{action}** on `{log['table_name']}` "
                f"— *{log.get('description', '')}*  \n"
                f"<small>🕐 {ts} &nbsp;|&nbsp; 👤 {log['performed_by']}"
                f"{' &nbsp;|&nbsp; 🆔 #' + str(log['record_id']) if log['record_id'] else ''}</small>",
                unsafe_allow_html=True
            )

            if log.get('old_values') or log.get('new_values'):
                with st.expander("View changes", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        if log['old_values']:
                            st.code(log['old_values'], language="text")
                        else:
                            st.caption("(no previous values)")
                    with c2:
                        if log['new_values']:
                            st.code(log['new_values'], language="text")
                        else:
                            st.caption("(no new values)")

            st.markdown('</div>', unsafe_allow_html=True)

with tab_table:
    if logs:
        df = pd.DataFrame(logs)
        display_cols = ['log_id', 'action_type', 'table_name', 'record_id',
                        'performed_by', 'description', 'performed_at']
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], use_container_width=True, height=500)
    else:
        st.info("No logs to display.")

st.divider()

# ── DBMS Showcase ──
with st.expander("💾 DBMS Concepts Demonstrated"):
    st.markdown("""
    | Concept | Implementation |
    |---------|---------------|
    | **TRIGGER (AFTER INSERT)** | `trg_appointment_insert`, `trg_patient_insert`, `trg_medical_record_insert`, `trg_feedback_insert` |
    | **TRIGGER (AFTER UPDATE)** | `trg_appointment_update` — tracks status changes |
    | **TIMESTAMP** | Every log entry auto-stamped with `CURRENT_TIMESTAMP` |
    | **INDEX** | `idx_action`, `idx_table`, `idx_time` for fast filtering |
    | **GROUP BY + COUNT** | Summary cards aggregate logs by action type |
    | **ORDER BY DESC** | Latest entries shown first |
    | **Filtering (WHERE)** | Dynamic filters by action type and table name |
    """)

    st.markdown("### Trigger Example")
    st.code("""
DELIMITER //
CREATE TRIGGER trg_appointment_update
AFTER UPDATE ON appointments
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_log (action_type, table_name, record_id,
                               performed_by, old_values, new_values, description)
        VALUES ('UPDATE', 'appointments', NEW.appointment_id, 'doctor',
                CONCAT('status=', OLD.status), CONCAT('status=', NEW.status),
                CONCAT('Appointment status changed: ', OLD.status, ' → ', NEW.status));
    END IF;
END //
DELIMITER ;
    """, language="sql")

# ── Footer ──
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:#888;'>
    Audit Log &nbsp;|&nbsp; {date.today().strftime('%B %d, %Y')} &nbsp;|&nbsp;
    Healthcare Appointment System
</div>
""", unsafe_allow_html=True)
