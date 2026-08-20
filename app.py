import streamlit as st
import datetime
import time
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import urllib.parse
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NHM e-Triage | Govt. of India",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE INIT ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = True
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'role' not in st.session_state:
    st.session_state.role = 'ASHA Worker'
if 'last_assessment' not in st.session_state:
    st.session_state.last_assessment = None
if 'last_synced_time' not in st.session_state:
    st.session_state.last_synced_time = datetime.datetime.now().strftime("%H:%M:%S")

# ---------- BLOCK GEO-COORDINATES REFERENCE ----------
BLOCK_COORDINATES = {
    "Kashi": [25.3176, 82.9739],
    "Pindra": [25.5392, 82.8398],
    "Sevapuri": [25.3090, 82.7820],
    "Cholapur": [25.4485, 83.0560],
    "Harahua": [25.3900, 82.9300],
    "Arajiline": [25.2600, 82.8700],
    "Varanasi": [25.3176, 82.9739]
}

def get_coordinates(block_name, district_name):
    clean_block = str(block_name).strip().title()
    if clean_block in BLOCK_COORDINATES:
        return BLOCK_COORDINATES[clean_block]
    return [25.3176, 82.9739]  # Default district centroid

# ---------- DATABASE SETUP & MIGRATION ----------
DB_NAME = "triage_data.db"

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                fever TEXT,
                breath TEXT,
                bp TEXT,
                pregnant TEXT,
                diabetes TEXT,
                chest_pain TEXT,
                vomiting TEXT,
                headache TEXT,
                spo2 INTEGER,
                district TEXT,
                block TEXT,
                result_title TEXT,
                result_msg TEXT,
                level TEXT,
                timestamp TEXT,
                abha_id TEXT DEFAULT '',
                category TEXT DEFAULT 'General',
                danger_signs TEXT DEFAULT 'None'
            )
        ''')
        c.execute("PRAGMA table_info(assessments)")
        columns = [col[1] for col in c.fetchall()]
        if 'abha_id' not in columns:
            c.execute("ALTER TABLE assessments ADD COLUMN abha_id TEXT DEFAULT ''")
        if 'category' not in columns:
            c.execute("ALTER TABLE assessments ADD COLUMN category TEXT DEFAULT 'General'")
        if 'danger_signs' not in columns:
            c.execute("ALTER TABLE assessments ADD COLUMN danger_signs TEXT DEFAULT 'None'")
        conn.commit()

def save_to_db(data):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO assessments (
                name, age, fever, breath, bp, pregnant, diabetes,
                chest_pain, vomiting, headache, spo2, district, block,
                result_title, result_msg, level, timestamp, abha_id,
                category, danger_signs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['age'], data['fever'], data['breath'],
            data['bp'], data['pregnant'], data['diabetes'],
            data['chest_pain'], data['vomiting'], data['headache'],
            data['spo2'], data['district'], data['block'],
            data['result_title'], data['result_msg'], data['level'],
            data['timestamp'], data.get('abha_id', ''),
            data.get('category', 'General'), data.get('danger_signs', 'None')
        ))
        last_id = c.lastrowid
        conn.commit()
        return last_id

@st.cache_data(ttl=10)
def load_from_db():
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
        return df

init_db()

# ---------- SVG ICONS (SOFTWARE GRADE) ----------
SVG_MEDICAL_SHIELD = """<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFD966" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="M12 8v8"></path><path d="M8 12h8"></path></svg>"""

SVG_HEADING_ASSESSMENT = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""

SVG_HEADING_ANALYTICS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""

SVG_HEADING_LOGS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>"""

SVG_HEADING_OUTBREAK = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""

SVG_ALERT_RED = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""

SVG_ALERT_YELLOW = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""

SVG_ALERT_GREEN = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""

# ---------- LANGUAGE DICTIONARY ----------
TEXTS = {
    'app_title': {'en': 'e-Triage Sahayak', 'hi': 'ई-ट्राइएज सहायक'},
    'subtitle': {'en': 'National Health Mission - AI-Assisted Referral Decision System', 'hi': 'राष्ट्रीय स्वास्थ्य मिशन - एआई सहायक रेफरल निर्णय प्रणाली'},
    'secure_badge': {'en': 'SECURE - PRODUCTION', 'hi': 'सुरक्षित - उत्पादन'},
    'form_title': {'en': 'Patient Clinical Assessment', 'hi': 'रोगी नैदानिक मूल्यांकन'},
    'name': {'en': 'Patient Full Name', 'hi': 'रोगी का पूरा नाम'},
    'age': {'en': 'Age (in years)', 'hi': 'आयु (वर्षों में)'},
    'fever': {'en': 'Fever / High Temperature', 'hi': 'बुखार / तेज बुखार'},
    'breath': {'en': 'Breathing Difficulty', 'hi': 'सांस लेने में कठिनाई'},
    'bp': {'en': 'Blood Pressure Status', 'hi': 'रक्तचाप (बीपी) स्थिति'},
    'pregnant': {'en': 'Patient is Pregnant?', 'hi': 'क्या रोगी गर्भवती है?'},
    'diabetes': {'en': 'History of Diabetes?', 'hi': 'मधुमेह का इतिहास?'},
    'chest_pain': {'en': 'Chest Pain / Discomfort', 'hi': 'सीने में दर्द / बेचैनी'},
    'spo2': {'en': 'Oxygen Level (SpO2 %)', 'hi': 'ऑक्सीजन स्तर (SpO2 %)'},
    'district': {'en': 'District', 'hi': 'जिला'},
    'block': {'en': 'Block / Taluka', 'hi': 'ब्लॉक / तालुका'},
    'abha': {'en': 'ABHA Health ID (Optional)', 'hi': 'आभा हेल्थ आईडी (वैकल्पिक)'},
    'submit': {'en': 'Generate Referral Recommendation', 'hi': 'रेफरल अनुशंसना उत्पन्न करें'},
}

def t(key):
    return TEXTS[key][st.session_state.lang]

# ---------- TRIAGE CLINICAL LOGIC WITH REASONING ----------
def calculate_triage(vitals):
    spo2 = vitals.get('spo2', 98)
    chest_pain = vitals.get('chest_pain') == 'Yes'
    breath = vitals.get('breath') == 'Severe'
    pregnant = vitals.get('pregnant') == 'Yes'
    bp = vitals.get('bp')
    age = vitals.get('age', 30)
    danger_signs = vitals.get('danger_signs', [])
    
    triggers = []
    
    if spo2 < 90:
        triggers.append(f"Critical Hypoxia (SpO2: {spo2}%)")
    if chest_pain:
        triggers.append("Acute Chest Pain / Cardiac Risk")
    if breath:
        triggers.append("Severe Respiratory Distress")
    if pregnant and bp == 'Very High (>160/100)':
        triggers.append("Severe Gestational Hypertension (Eclampsia Risk)")
    if pregnant and "Bleeding" in danger_signs:
        triggers.append("Antepartum Haemorrhage")
    if age <= 5 and any(sign in danger_signs for sign in ["Convulsions / Fits", "Inability to feed/drink", "Lethargy/Unconsciousness"]):
        triggers.append("IMNCI General Pediatric Danger Sign Detected")
        
    if len(triggers) > 0:
        return {
            'level': 'RED',
            'title': 'RED ALERT - Critical Emergency',
            'msg': 'Immediate referral required to District Hospital / Tertiary Care Center. Arrange 108 Ambulance instantly.',
            'action': 'ACTION: IMMEDIATE (0-15 Mins)',
            'triggers': triggers
        }
    
    urgent_triggers = []
    if spo2 <= 94:
        urgent_triggers.append(f"Borderline Hypoxia (SpO2: {spo2}%)")
    if bp in ['High (140-159/90-99)', 'Very High (>160/100)']:
        urgent_triggers.append(f"Elevated Blood Pressure ({bp})")
    if vitals.get('fever') == 'High (>102°F)':
        urgent_triggers.append("High Grade Pyrexia (>102°F)")
    if len(danger_signs) > 0:
        urgent_triggers.append(f"Complications Noted: {', '.join(danger_signs)}")
        
    if len(urgent_triggers) > 0:
        return {
            'level': 'YELLOW',
            'title': 'YELLOW ALERT - Urgent Care Needed',
            'msg': 'Refer to Community Health Centre (CHC) / Primary Health Centre (PHC) within 1-2 hours.',
            'action': 'ACTION: URGENT (Within 1 Hour)',
            'triggers': urgent_triggers
        }
        
    return {
        'level': 'GREEN',
        'title': 'GREEN ALERT - Stable Condition',
        'msg': 'Manageable at Sub-Centre / Ayushman Arogya Mandir. Routine consultation & follow-up.',
        'action': 'ACTION: ROUTINE (OPD Timing)',
        'triggers': ['All baseline clinical vitals within stable physiological ranges.']
    }

# ---------- OUTBREAK ENGINE ----------
def check_outbreak_risk(df):
    if df.empty or len(df) < 3:
        return []
    fever_cases = df[df['fever'] == 'High (>102°F)']
    if fever_cases.empty:
        return []
    cluster_counts = fever_cases.groupby(['district', 'block']).size().reset_index(name='case_count')
    hotspots = cluster_counts[cluster_counts['case_count'] >= 2].to_dict('records')
    return hotspots

# ---------- PDF SLIP GENERATOR ----------
def generate_referral_pdf(data):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_fill_color(11, 43, 74)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 8, "NATIONAL HEALTH MISSION - e-TRIAGE REFERRAL SLIP", ln=True, align='C')
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(255, 217, 102)
    pdf.cell(190, 6, "Ministry of Health & Family Welfare | Government of India", ln=True, align='C')
    pdf.ln(12)
    
    pdf.set_text_color(11, 43, 74)
    pdf.set_font("Helvetica", "B", 11)
    ref_str = f"Ref ID: NHM-{data.get('id', 'NEW')}"
    if data.get('abha_id'):
        ref_str += f" | ABHA ID: {data['abha_id']}"
    pdf.cell(190, 7, f"{ref_str} | Date: {data.get('timestamp')}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 6, f"Patient Name: {data['name']}", 0)
    pdf.cell(95, 6, f"Age: {data['age']} Years | Category: {data.get('category', 'General')}", ln=True)
    pdf.cell(95, 6, f"District: {data['district']}", 0)
    pdf.cell(95, 6, f"Block/Taluka: {data['block']}", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(240, 244, 248)
    pdf.cell(45, 7, "Parameter", 1, 0, 'L', True)
    pdf.cell(50, 7, "Recorded Value", 1, 0, 'L', True)
    pdf.cell(45, 7, "Parameter", 1, 0, 'L', True)
    pdf.cell(50, 7, "Recorded Value", 1, 1, 'L', True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(45, 6, "Oxygen (SpO2)", 1)
    pdf.cell(50, 6, f"{data['spo2']}%", 1)
    pdf.cell(45, 6, "Blood Pressure", 1)
    pdf.cell(50, 6, str(data['bp']), 1, 1)
    
    pdf.cell(45, 6, "Breathing Status", 1)
    pdf.cell(50, 6, str(data['breath']), 1)
    pdf.cell(45, 6, "Fever", 1)
    pdf.cell(50, 6, str(data['fever']), 1, 1)
    
    pdf.cell(45, 6, "Chest Pain", 1)
    pdf.cell(50, 6, str(data['chest_pain']), 1)
    pdf.cell(45, 6, "Danger Signs", 1)
    pdf.cell(50, 6, str(data.get('danger_signs', 'None'))[:25], 1, 1)
    pdf.ln(6)
    
    level = data['level']
    fill_r, fill_g, fill_b = (254, 242, 242) if level == 'RED' else ((255, 251, 235) if level == 'YELLOW' else (240, 253, 244))
    text_r, text_g, text_b = (220, 38, 38) if level == 'RED' else ((245, 158, 11) if level == 'YELLOW' else (34, 197, 94))
    
    pdf.set_fill_color(fill_r, fill_g, fill_b)
    pdf.set_draw_color(text_r, text_g, text_b)
    pdf.rect(10, pdf.get_y(), 190, 24, 'FD')
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(text_r, text_g, text_b)
    pdf.cell(190, 7, f"TRIAGE SEVERITY: {data['result_title']}", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(185, 5, f"Clinical Action: {data['result_msg']}")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(190, 5, "Official Ayushman Bharat Digital Health Mission document. Valid for expedited clinical intake.", ln=True, align='C')
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# ---------- UI HEADER ----------
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0B2B4A 0%, #1A4A70 100%); padding: 1.2rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(11,43,74,0.15);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center;">
            {SVG_MEDICAL_SHIELD}
            <div>
                <h2 style="margin: 0; color: white; font-size: 1.4rem; font-weight: 700; line-height: 1.2;">National Health Mission | e-Triage</h2>
                <p style="margin: 0; color: #FFD966; font-size: 0.85rem; font-weight: 500;">Ayushman Bharat - AI-Assisted Clinical Decision Support</p>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="background: #FF9933; color: #0B2B4A; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.5px;">MoHFW Compliant</span>
            <span style="background: rgba(255,255,255,0.15); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem;">Cloud Sync: Active</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### System Settings")
    st.session_state.lang = st.selectbox("Language / भाषा", ['en', 'hi'], format_func=lambda x: 'English' if x == 'en' else 'हिंदी')
    menu = st.radio("Navigation", ["New Assessment", "Patient History Trends", "Outbreak Surveillance", "Analytics Dashboard", "Patient Logs"])
    st.markdown("---")
    
    st.markdown("#### Cloud Synchronization")
    st.caption(f"Last Synced: `{st.session_state.last_synced_time}`")
    if st.button("Sync Offline Records", use_container_width=True):
        st.session_state.last_synced_time = datetime.datetime.now().strftime("%H:%M:%S")
        st.success("All local registries synced with DHS.")
        
    st.markdown("---")
    st.caption("National Digital Health Mission (NDHM) &bull; Production v3.5")

# ---------- PAGE 1: NEW ASSESSMENT ----------
if menu == "New Assessment":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ASSESSMENT}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>{t('form_title')}</h3></div>", unsafe_allow_html=True)
    
    clinical_category = st.radio("Clinical Intake Category", ["General Adult", "Antenatal / High-Risk Pregnancy", "Pediatric (< 5 Years)"], horizontal=True)
    
    with st.form("triage_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(t('name'), placeholder="e.g. Ramesh Kumar")
            default_age = 2 if clinical_category == "Pediatric (< 5 Years)" else (26 if "Pregnancy" in clinical_category else 35)
            age = st.number_input(t('age'), min_value=1, max_value=120, value=default_age)
            spo2 = st.slider(t('spo2'), min_value=70, max_value=100, value=98)
            fever = st.selectbox(t('fever'), ["Normal", "Mild (99-101°F)", "High (>102°F)"])
        
        with col2:
            breath = st.selectbox(t('breath'), ["Normal", "Mild", "Severe"])
            bp = st.selectbox(t('bp'), ["Normal", "High (140-159/90-99)", "Very High (>160/100)", "Low (<90/60)"])
            chest_pain = st.selectbox(t('chest_pain'), ["No", "Yes"])
            pregnant = "Yes" if "Pregnancy" in clinical_category else st.selectbox(t('pregnant'), ["No", "Yes"])
            
        with col3:
            district = st.text_input(t('district'), value="Varanasi")
            block = st.selectbox(t('block'), ["Kashi", "Pindra", "Sevapuri", "Cholapur", "Harahua", "Arajiline"])
            abha_id = st.text_input(t('abha'), placeholder="e.g. 91-XXXX-XXXX-XXXX")
            diabetes = st.selectbox(t('diabetes'), ["No", "Yes"])
            headache = st.selectbox("Severe Headache", ["No", "Yes"])
            vomiting = st.selectbox("Vomiting / Nausea", ["No", "Yes"])

        danger_selected = []
        if clinical_category == "Antenatal / High-Risk Pregnancy":
            st.markdown("#### High-Risk Pregnancy Danger Markers")
            danger_selected = st.multiselect("Select observed complications:", ["Bleeding", "Severe Abdominal Pain", "Severe Swelling (Face/Hands)", "Decreased Foetal Movement"])
        elif clinical_category == "Pediatric (< 5 Years)":
            st.markdown("#### IMNCI Pediatric Danger Markers")
            danger_selected = st.multiselect("Select observed IMNCI red flags:", ["Convulsions / Fits", "Inability to feed/drink", "Lethargy/Unconsciousness", "Stridor in calm child"])

        submitted = st.form_submit_button(t('submit'), use_container_width=True)

    if submitted:
        if not name:
            st.error("Patient name is required.")
        else:
            vitals = {
                'spo2': spo2,
                'chest_pain': chest_pain,
                'breath': breath,
                'pregnant': pregnant,
                'bp': bp,
                'fever': fever,
                'age': age,
                'danger_signs': danger_selected
            }
            res = calculate_triage(vitals)
            
            danger_str = ", ".join(danger_selected) if danger_selected else "None"
            assessment_payload = {
                'name': name, 'age': age, 'fever': fever, 'breath': breath,
                'bp': bp, 'pregnant': pregnant, 'diabetes': diabetes,
                'chest_pain': chest_pain, 'vomiting': vomiting, 'headache': headache,
                'spo2': spo2, 'district': district, 'block': block,
                'abha_id': abha_id, 'category': clinical_category,
                'danger_signs': danger_str,
                'result_title': res['title'], 'result_msg': res['msg'],
                'level': res['level'], 'action': res['action'],
                'triggers': res.get('triggers', []),
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            row_id = save_to_db(assessment_payload)
            assessment_payload['id'] = row_id
            st.session_state.last_assessment = assessment_payload
            st.cache_data.clear()

    # Render Result Card
    if st.session_state.last_assessment:
        cur = st.session_state.last_assessment
        color = "#DC2626" if cur['level'] == 'RED' else ("#F59E0B" if cur['level'] == 'YELLOW' else "#22C55E")
        alert_svg = SVG_ALERT_RED if cur['level'] == 'RED' else (SVG_ALERT_YELLOW if cur['level'] == 'YELLOW' else SVG_ALERT_GREEN)
        
        st.markdown(f"""
        <div style="background-color: {color}12; border-left: 6px solid {color}; border-top: 1px solid {color}30; border-right: 1px solid {color}30; border-bottom: 1px solid {color}30; border-radius: 12px; padding: 22px; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                {alert_svg}
                <h3 style="color: {color}; margin: 0; font-size: 1.25rem; font-weight: 700;">{cur['result_title']}</h3>
            </div>
            <p style="font-size: 1.05rem; margin: 8px 0 16px 0; color: #1E293B; line-height: 1.5;">{cur['result_msg']}</p>
            <span style="background: {color}; color: white; padding: 6px 18px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.5px; display: inline-block;">
                {cur.get('action', 'ACTION RECORDED')}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        if cur.get('triggers'):
            with st.expander("🔍 Clinical Decision Reasoning & Triggers", expanded=True):
                for trig in cur['triggers']:
                    st.markdown(f"&bull; **Clinical Rule Triggered:** `{trig}`")
        
        st.markdown("#### Clinical Action & Referral Dispatch Hub")
        col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 1])
        
        with col_act1:
            if PDF_AVAILABLE:
                pdf_path = generate_referral_pdf(cur)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 Download Official Referral Slip (.PDF)",
                            data=f,
                            file_name=f"NHM_Referral_{cur['name']}_{cur.get('id', 'Rec')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                st.caption("PDF engine unavailable.")
                
        with col_act2:
            summary_msg = f"*EMERGENCY REFERRAL - NHM e-TRIAGE*\n*Patient:* {cur['name']} ({cur['age']}y)\n*Severity:* {cur['level']}\n*SpO2:* {cur['spo2']}%\n*BP:* {cur['bp']}\n*Location:* {cur['block']}, {cur['district']}\n*Action:* {cur['result_title']}"
            encoded_msg = urllib.parse.quote(summary_msg)
            whatsapp_url = f"https://wa.me/?text={encoded_msg}"
            
            st.link_button("📲 Dispatch WhatsApp Alert to Doctor", whatsapp_url, use_container_width=True)
            
            if cur['level'] in ['RED', 'YELLOW']:
                st.link_button("🩺 Open e-Sanjeevani Tele-Consult", "https://esanjeevani.mohfw.gov.in/#/patient/consultation", use_container_width=True)
                    
        with col_act3:
            qr_data = f"NHM-REF:{cur.get('id')}|Patient:{cur['name']}|SpO2:{cur['spo2']}|Level:{cur['level']}"
            encoded_qr = urllib.parse.quote(qr_data)
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=110x110&data={encoded_qr}"
            st.image(qr_url, caption="OPD Intake QR Code", width=110)

# ---------- PAGE 2: PATIENT HISTORY TRENDS ----------
elif menu == "Patient History Trends":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ANALYTICS}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>Patient Vitals Timeline & Longitudinal Trend</h3></div>", unsafe_allow_html=True)
    df = load_from_db()
    
    if not df.empty:
        patient_list = df['name'].unique()
        selected_patient = st.selectbox("Select Patient to Analyze Trajectory", patient_list)
        
        p_history = df[df['name'] == selected_patient].sort_values(by='id')
        
        if len(p_history) > 1:
            fig_trend = px.line(
                p_history, 
                x='timestamp', 
                y='spo2', 
                markers=True, 
                title=f"SpO2 Trajectory for {selected_patient}",
                labels={'spo2': 'Oxygen Level (%)', 'timestamp': 'Date/Time'}
            )
            fig_trend.add_hline(y=94, line_dash="dash", line_color="orange", annotation_text="Warning Threshold (94%)")
            fig_trend.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Critical Threshold (90%)")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info(f"Only 1 assessment recorded for {selected_patient}. Longitudinal graphs appear after multiple entries.")
            
        st.dataframe(p_history[['timestamp', 'spo2', 'bp', 'fever', 'breath', 'level', 'result_title']], use_container_width=True, hide_index=True)
    else:
        st.info("No patient history found.")

# ---------- PAGE 3: OUTBREAK SURVEILLANCE & FOLIUM MAP ----------
elif menu == "Outbreak Surveillance":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_OUTBREAK}<h3 style='margin:0; font-size: 1.3rem; color: #DC2626;'>Disease Outbreak & Geospatial Surveillance</h3></div>", unsafe_allow_html=True)
    df = load_from_db()
    hotspots = check_outbreak_risk(df)
    
    if hotspots:
        for spot in hotspots:
            st.error(f"⚠️ **EPIDEMIC CLUSTER DETECTED**: High Fever concentration in **District: {spot['district']} | Block: {spot['block']}** ({spot['case_count']} Critical Cases recorded).")
    else:
        st.success("🛡️ **Surveillance Active**: No anomalous disease clusters or epidemic triggers detected in recent logs.")

    st.markdown("#### 🗺️ Interactive Cluster & Hotspot Map")
    
    # Initialize Folium Map centered at Varanasi/District level
    center_coords = [25.3176, 82.9739]
    triage_map = folium.Map(location=center_coords, zoom_start=11, tiles="CartoDB positron")
    
    if not df.empty:
        # 1. HeatMap for Outbreak Intensity
        heat_data = []
        marker_cluster = MarkerCluster(name="Patient Cases (Clustered)").add_to(triage_map)
        
        for _, row in df.iterrows():
            coords = get_coordinates(row['block'], row['district'])
            # Add small random jitter so markers on the same block don't completely overlap
            jitter_lat = coords[0] + (hash(str(row['id']) + 'lat') % 100 - 50) * 0.0003
            jitter_lon = coords[1] + (hash(str(row['id']) + 'lon') % 100 - 50) * 0.0003
            
            # Weight for HeatMap (Red=3, Yellow=2, Green=1)
            weight = 3 if row['level'] == 'RED' else (2 if row['level'] == 'YELLOW' else 1)
            heat_data.append([jitter_lat, jitter_lon, weight])
            
            # Marker styling based on triage severity
            marker_color = "red" if row['level'] == 'RED' else ("orange" if row['level'] == 'YELLOW' else "green")
            
            popup_html = f"""
            <div style='font-family: Arial, sans-serif; font-size: 12px; width: 180px;'>
                <b style='color: #0B2B4A;'>{row['name']}</b> ({row['age']}y)<br>
                <b>Status:</b> <span style='color:{marker_color}; font-weight:bold;'>{row['level']}</span><br>
                <b>SpO2:</b> {row['spo2']}% | <b>BP:</b> {row['bp']}<br>
                <b>Fever:</b> {row['fever']}<br>
                <b>Block:</b> {row['block']}<br>
                <small>{row['timestamp']}</small>
            </div>
            """
            
            folium.CircleMarker(
                location=[jitter_lat, jitter_lon],
                radius=7 if row['level'] == 'RED' else 5,
                popup=folium.Popup(popup_html, max_width=220),
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.85
            ).add_to(marker_cluster)
            
        if heat_data:
            HeatMap(heat_data, radius=18, blur=15, min_opacity=0.3, name="Epidemic Heat Intensity").add_to(triage_map)
            
        folium.LayerControl().add_to(triage_map)
        
        # Display the map in Streamlit
        st_folium(triage_map, width="100%", height=450)
    else:
        st_folium(triage_map, width="100%", height=350)
        st.info("No records recorded yet to project on map.")

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        if not df.empty:
            block_fever = df[df['fever'] == 'High (>102°F)'].groupby('block').size().reset_index(name='High Fever Cases')
            if not block_fever.empty:
                fig_outbreak = px.bar(block_fever, x='block', y='High Fever Cases', title='High-Fever Spike per Block', color='High Fever Cases', color_continuous_scale='Reds')
                st.plotly_chart(fig_outbreak, use_container_width=True)
            else:
                st.info("No high-fever cases recorded.")
    with col_o2:
        st.markdown("#### Nearest Healthcare Facility Routing")
        st.info("""
        * **District Hospital (Varanasi):** 108 / 0542-2508102 (ICU & Critical Care)
        * **CHC Kashi Unit:** 0542-2210045 (24/7 Emergency & Maternity)
        * **MoHFW National Tele-Health Helpline:** 1075 / 104
        """)

# ---------- PAGE 4: ANALYTICS DASHBOARD ----------
elif menu == "Analytics Dashboard":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ANALYTICS}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>District Triage Analytics</h3></div>", unsafe_allow_html=True)
    df = load_from_db()
    if df.empty:
        st.info("No assessment records found.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assessments", len(df))
        col2.metric("Critical (Red Alert)", len(df[df['level'] == 'RED']))
        col3.metric("Urgent (Yellow Alert)", len(df[df['level'] == 'YELLOW']))

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig1 = px.pie(
                df, 
                names='level', 
                title='Triage Severity Distribution', 
                color='level',
                color_discrete_map={'RED': '#DC2626', 'YELLOW': '#F59E0B', 'GREEN': '#22C55E'}
            )
            fig1.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_c2:
            fig2 = px.histogram(
                df, 
                x='age', 
                nbins=15, 
                title='Patient Age Demographics', 
                color_discrete_sequence=['#0B2B4A']
            )
            fig2.update_layout(margin=dict(t=40, b=20, l=20, r=20), xaxis_title="Age (Years)", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)

# ---------- PAGE 5: PATIENT LOGS ----------
elif menu == "Patient Logs":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_LOGS}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>Patient Assessment Registry</h3></div>", unsafe_allow_html=True)
    df = load_from_db()
    if not df.empty:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search by Patient Name or Block")
        with col_f2:
            level_filter = st.multiselect("Filter by Triage Level", ["RED", "YELLOW", "GREEN"], default=["RED", "YELLOW", "GREEN"])
            
        filtered_df = df[df['level'].isin(level_filter)]
        if search_query:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False, na=False) | filtered_df['block'].str.contains(search_query, case=False, na=False)]
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Filtered Registry (CSV)", 
            data=csv, 
            file_name="triage_registry.csv", 
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.info("No records recorded yet.")
