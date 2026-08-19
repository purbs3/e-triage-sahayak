import streamlit as st
import datetime
import time
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import os

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ==============================================================
# 1. PAGE CONFIGURATION & ENTERPRISE CSS
# ==============================================================
st.set_page_config(
    page_title="NHM e-Triage Clinical Decision System",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Software Design System
app_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu, footer, header, [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Top Enterprise App Bar */
    .app-bar {
        background: #0B2B4A;
        padding: 0.9rem 1.6rem;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(11, 43, 74, 0.08);
        border-bottom: 3px solid #FF9933;
    }
    
    .app-title-group {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .app-title {
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        margin: 0;
    }
    
    .app-subtitle {
        color: #94A3B8;
        font-size: 0.78rem;
        margin: 0;
    }
    
    /* Software Cards */
    .software-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .metric-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        border-left: 4px solid #0B2B4A;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
    }
    
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* Result Banners */
    .triage-banner {
        border-radius: 10px;
        padding: 1.4rem;
        margin-top: 1.2rem;
        display: flex;
        gap: 16px;
        align-items: flex-start;
    }
    .banner-red { background: #FEF2F2; border: 1.5px solid #F87171; }
    .banner-yellow { background: #FFFBEB; border: 1.5px solid #FBBF24; }
    .banner-green { background: #F0FDF4; border: 1.5px solid #4ADE80; }
    
    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-red { background: #DC2626; color: #FFFFFF; }
    .pill-yellow { background: #D97706; color: #FFFFFF; }
    .pill-green { background: #16A34A; color: #FFFFFF; }
    .pill-live { background: rgba(34, 197, 94, 0.15); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.3); }

    /* Button Styling */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }
</style>
"""
st.markdown(app_css, unsafe_allow_html=True)

# ==============================================================
# 2. SVG VECTOR GRAPHICS LIBRARY
# ==============================================================
def svg_shield(color="#0B2B4A", size=20):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>"""

def svg_cross(color="#FFFFFF", size=22):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>"""

def svg_activity(color="#0B2B4A", size=18):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>"""

def svg_user(color="#64748B", size=18):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>"""

def svg_alert_triangle(color="#DC2626", size=28):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""

def svg_check_circle(color="#16A34A", size=28):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>"""

def svg_database(color="#64748B", size=18):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>"""

# ==============================================================
# 3. DATABASE & PERSISTENCE
# ==============================================================
DB_NAME = "triage_data.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                spo2 INTEGER,
                fever TEXT,
                breath TEXT,
                bp TEXT,
                pregnant TEXT,
                diabetes TEXT,
                chest_pain TEXT,
                district TEXT,
                block TEXT,
                result_title TEXT,
                result_msg TEXT,
                level TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

def save_assessment(data):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO assessments (
                name, age, spo2, fever, breath, bp, pregnant, diabetes,
                chest_pain, district, block, result_title, result_msg, level, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['age'], data['spo2'], data['fever'], data['breath'],
            data['bp'], data['pregnant'], data['diabetes'], data['chest_pain'],
            data['district'], data['block'], data['result_title'], data['result_msg'],
            data['level'], data['timestamp']
        ))
        conn.commit()
    st.cache_data.clear()

@st.cache_data(ttl=30)
def fetch_assessments():
    with get_db() as conn:
        return pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)

init_db()

# Seed mock clinical data if fresh DB
if fetch_assessments().empty:
    sample_records = [
        ("Kavita Devi", 28, 92, "High (>102°F)", "Mild", "Very High (>160/100)", "Yes", "No", "No", "Varanasi", "Kashi", "RED ALERT - Critical Emergency", "Immediate tertiary transfer required.", "RED"),
        ("Rajesh Verma", 54, 95, "Normal", "Severe", "High (140-159/90-99)", "No", "Yes", "Yes", "Prayagraj", "Sadar", "RED ALERT - Critical Emergency", "Cardiac protocol triggered.", "RED"),
        ("Sunita Patel", 34, 97, "Mild (99-101°F)", "Normal", "Normal", "No", "No", "No", "Varanasi", "Pindra", "GREEN ALERT - Stable Condition", "Standard primary management.", "GREEN"),
        ("Manoj Tiwari", 45, 93, "High (>102°F)", "Normal", "Normal", "No", "No", "No", "Gorakhpur", "City", "YELLOW ALERT - Urgent Care Needed", "Refer to CHC for monitoring.", "YELLOW")
    ]
    for n, a, sp, fv, br, bp, pr, db, cp, dt, bk, rt, rm, lv in sample_records:
        save_assessment({
            'name': n, 'age': a, 'spo2': sp, 'fever': fv, 'breath': br, 'bp': bp,
            'pregnant': pr, 'diabetes': db, 'chest_pain': cp, 'district': dt, 'block': bk,
            'result_title': rt, 'result_msg': rm, 'level': lv,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

# ==============================================================
# 4. CLINICAL DECISION SUPPORT ENGINE (MoHFW Evidence-Based)
# ==============================================================
def evaluate_clinical_triage(v):
    spo2 = v.get('spo2', 98)
    chest_pain = v.get('chest_pain') == 'Yes'
    breath = v.get('breath') == 'Severe'
    pregnant = v.get('pregnant') == 'Yes'
    bp = v.get('bp')
    fever = v.get('fever')
    
    # Red Condition (Immediate - 0-15 mins)
    if spo2 < 90 or chest_pain or breath or (pregnant and bp == 'Very High (>160/100)'):
        return {
            'level': 'RED',
            'banner_class': 'banner-red',
            'pill_class': 'pill-red',
            'title': 'RED ALERT - Critical Emergency',
            'msg': 'Critical vitals destabilization. Immediate referral required to District Hospital / Medical College via 108 Ambulance service.',
            'action': 'ACTION: IMMEDIATE (0-15 Mins)'
        }
    # Yellow Condition (Urgent - Within 1-2 hours)
    elif spo2 <= 94 or bp in ['High (140-159/90-99)', 'Very High (>160/100)'] or fever == 'High (>102°F)':
        return {
            'level': 'YELLOW',
            'banner_class': 'banner-yellow',
            'pill_class': 'pill-yellow',
            'title': 'YELLOW ALERT - Urgent Clinical Attention',
            'msg': 'Moderate physiological distress. Patient must be examined at Community Health Centre (CHC) or Sub-Divisional Hospital within 2 hours.',
            'action': 'ACTION: URGENT (Within 1-2 Hours)'
        }
    # Green Condition (Routine Primary Care)
    else:
        return {
            'level': 'GREEN',
            'banner_class': 'banner-green',
            'pill_class': 'pill-green',
            'title': 'GREEN ALERT - Stable / Routine Care',
            'msg': 'Normal physiological indicators. Manageable at Ayushman Arogya Mandir / Primary Health Centre (PHC).',
            'action': 'ACTION: ROUTINE OPD CONSULTATION'
        }

# ==============================================================
# 5. ENTERPRISE HEADER
# ==============================================================
st.markdown(f"""
<div class="app-bar">
    <div class="app-title-group">
        <div style="background: rgba(255,255,255,0.12); padding: 8px; border-radius: 8px; display:flex; align-items:center;">
            {svg_cross(color="#FFFFFF", size=24)}
        </div>
        <div>
            <h1 class="app-title">National Health Mission &bull; e-Triage Portal</h1>
            <p class="app-subtitle">Ministry of Health & Family Welfare &bull; Government of India</p>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
        <span class="pill-badge pill-live">
            <span style="width:7px; height:7px; background:#22C55E; border-radius:50%;"></span>
            OPERATIONAL v3.4
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================
# 6. NAVIGATION & SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        {svg_shield(color="#0B2B4A", size=22)}
        <span style="font-weight:700; font-size:0.95rem; color:#0B2B4A;">CLINICAL MODULES</span>
    </div>
    """, unsafe_allow_html=True)
    
    selected_module = st.radio(
        "Navigation",
        ["Clinical Assessment", "Epidemiology Dashboard", "Patient Registries"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.75rem; color:#64748B; line-height:1.5;">
        <div><b>Protocol Standard:</b> NDHM MoHFW v2.4</div>
        <div><b>Local Node:</b> UP-EAST-CLUSTER-04</div>
    </div>
    """, unsafe_allow_html=True)

df_records = fetch_assessments()

# ==============================================================
# 7. MODULE VIEWS
# ==============================================================

# --- MODULE 1: CLINICAL ASSESSMENT ---
if selected_module == "Clinical Assessment":
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom: 0.8rem;">
        {svg_activity(color="#0B2B4A", size=20)}
        <h3 style="margin:0; font-size:1.15rem; font-weight:700; color:#0F172A;">Patient Clinical Intake & Triage</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("clinical_intake_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**{svg_user(size=14)} Patient Demographics**", unsafe_allow_html=True)
            p_name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
            p_age = st.number_input("Age (Years)", min_value=1, max_value=115, value=38)
            p_district = st.selectbox("District", ["Varanasi", "Prayagraj", "Gorakhpur", "Lucknow", "Patna", "Other"])
            p_block = st.text_input("Block / Sub-District", value="Central Division")

        with col2:
            st.markdown(f"**{svg_activity(size=14)} Primary Vitals**", unsafe_allow_html=True)
            p_spo2 = st.slider("Blood Oxygen (SpO2 %)", min_value=60, max_value=100, value=98)
            p_bp = st.selectbox("Blood Pressure Category", ["Normal", "High (140-159/90-99)", "Very High (>160/100)", "Low (<90/60)"])
            p_fever = st.selectbox("Temperature", ["Normal", "Mild (99-101°F)", "High (>102°F)"])

        with col3:
            st.markdown(f"**{svg_shield(size=14)} Symptom Flags & Risk Factors**", unsafe_allow_html=True)
            p_breath = st.selectbox("Respiratory Distress", ["Normal", "Mild", "Severe"])
            p_chest = st.selectbox("Chest Pain / Pressure", ["No", "Yes"])
            p_preg = st.selectbox("Pregnancy Status", ["No", "Yes"])
            p_diab = st.selectbox("Comorbid Diabetes", ["No", "Yes"])
            
        submit_btn = st.form_submit_button("Run Clinical Decision Protocol", use_container_width=True, type="primary")

    if submit_btn:
        if not p_name.strip():
            st.error("Validation Error: Patient full name is mandatory for clinical indexing.")
        else:
            vitals_payload = {
                'spo2': p_spo2,
                'chest_pain': p_chest,
                'breath': p_breath,
                'pregnant': p_preg,
                'bp': p_bp,
                'fever': p_fever
            }
            evaluation = evaluate_clinical_triage(vitals_payload)
            
            # Save to Database
            record = {
                'name': p_name.strip(),
                'age': p_age,
                'spo2': p_spo2,
                'fever': p_fever,
                'breath': p_breath,
                'bp': p_bp,
                'pregnant': p_preg,
                'diabetes': p_diab,
                'chest_pain': p_chest,
                'district': p_district,
                'block': p_block,
                'result_title': evaluation['title'],
                'result_msg': evaluation['msg'],
                'level': evaluation['level'],
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_assessment(record)
            
            # Render Clinical Outcome Card with Vector Icons
            icon_markup = svg_alert_triangle(color="#DC2626" if evaluation['level']=='RED' else "#D97706") if evaluation['level'] in ['RED', 'YELLOW'] else svg_check_circle()
            
            st.markdown(f"""
            <div class="triage-banner {evaluation['banner_class']}">
                <div>{icon_markup}</div>
                <div style="flex:1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <h4 style="margin:0; font-weight:700; color:#0F172A; font-size:1.1rem;">{evaluation['title']}</h4>
                        <span class="pill-badge {evaluation['pill_class']}">{evaluation['action']}</span>
                    </div>
                    <p style="margin:0 0 10px 0; color:#334155; font-size:0.95rem; line-height:1.4;">{evaluation['msg']}</p>
                    <div style="font-size:0.75rem; color:#64748B;">Assessment indexed in State Surveillance Network &bull; Ref ID: #REF-{int(time.time())%100000}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- MODULE 2: EPIDEMIOLOGY DASHBOARD ---
elif selected_module == "Epidemiology Dashboard":
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom: 1rem;">
        {svg_activity(color="#0B2B4A", size=20)}
        <h3 style="margin:0; font-size:1.15rem; font-weight:700; color:#0F172A;">Public Health & Triage Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if df_records.empty:
        st.info("No assessment records found in the current operational period.")
    else:
        # Key Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-box"><div class="metric-value">{len(df_records)}</div><div class="metric-label">Total Intakes</div></div>""", unsafe_allow_html=True)
        with m2:
            red_count = len(df_records[df_records['level'] == 'RED'])
            st.markdown(f"""<div class="metric-box" style="border-left-color:#DC2626;"><div class="metric-value" style="color:#DC2626;">{red_count}</div><div class="metric-label">Critical Cases (Red)</div></div>""", unsafe_allow_html=True)
        with m3:
            yellow_count = len(df_records[df_records['level'] == 'YELLOW'])
            st.markdown(f"""<div class="metric-box" style="border-left-color:#D97706;"><div class="metric-value" style="color:#D97706;">{yellow_count}</div><div class="metric-label">Urgent Referrals (Yellow)</div></div>""", unsafe_allow_html=True)
        with m4:
            green_count = len(df_records[df_records['level'] == 'GREEN'])
            st.markdown(f"""<div class="metric-box" style="border-left-color:#16A34A;"><div class="metric-value" style="color:#16A34A;">{green_count}</div><div class="metric-label">Primary Stable (Green)</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Visualizations (Plotly)
        c1, c2 = st.columns([1, 1.2])
        with c1:
            fig_triage = px.pie(
                df_records, 
                names='level', 
                title='Clinical Triage Categorization',
                color='level',
                color_discrete_map={'RED': '#DC2626', 'YELLOW': '#F59E0B', 'GREEN': '#16A34A'},
                hole=0.45
            )
            fig_triage.update_layout(margin=dict(t=40, b=10, l=10, r=10), font=dict(family="Plus Jakarta Sans"))
            st.plotly_chart(fig_triage, use_container_width=True)

        with c2:
            fig_age = px.histogram(
                df_records, 
                x='age', 
                color='level',
                title='Age Demographics vs. Severity Breakdown',
                color_discrete_map={'RED': '#DC2626', 'YELLOW': '#F59E0B', 'GREEN': '#16A34A'},
                nbins=12
            )
            fig_age.update_layout(
                margin=dict(t=40, b=10, l=10, r=10),
                font=dict(family="Plus Jakarta Sans"),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF"
            )
            st.plotly_chart(fig_age, use_container_width=True)

# --- MODULE 3: PATIENT REGISTRIES ---
elif selected_module == "Patient Registries":
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom: 1rem;">
        {svg_database(color="#0B2B4A", size=20)}
        <h3 style="margin:0; font-size:1.15rem; font-weight:700; color:#0F172A;">Electronic Health Registry Logs</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_records.empty:
        st.dataframe(
            df_records[['id', 'name', 'age', 'spo2', 'bp', 'fever', 'district', 'level', 'timestamp']],
            use_container_width=True,
            hide_index=True
        )
        
        col_d1, col_d2 = st.columns([1, 4])
        with col_d1:
            csv_data = df_records.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Dataset (CSV)",
                data=csv_data,
                file_name=f"NHM_Triage_Logs_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("The patient registry is currently empty.")
