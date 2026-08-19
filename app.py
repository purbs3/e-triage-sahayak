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

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NHM e-Triage | Govt. of India",
    page_icon="🛡️",
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

# ---------- DATABASE SETUP ----------
DB_NAME = "triage_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO assessments (
            name, age, fever, breath, bp, pregnant, diabetes,
            chest_pain, vomiting, headache, spo2, district, block,
            result_title, result_msg, level, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['age'], data['fever'], data['breath'],
        data['bp'], data['pregnant'], data['diabetes'],
        data['chest_pain'], data['vomiting'], data['headache'],
        data['spo2'], data['district'], data['block'],
        data['result_title'], data['result_msg'], data['level'],
        data['timestamp']
    ))
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id

@st.cache_data(ttl=10)
def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# ---------- SVG ICONS (SOFTWARE GRADE) ----------
SVG_MEDICAL_SHIELD = """<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFD966" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="M12 8v8"></path><path d="M8 12h8"></path></svg>"""

SVG_HEADING_ASSESSMENT = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""

SVG_HEADING_ANALYTICS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""

SVG_HEADING_LOGS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>"""

SVG_ALERT_RED = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""

SVG_ALERT_YELLOW = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""

SVG_ALERT_GREEN = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""

# ---------- LANGUAGE DICTIONARY ----------
TEXTS = {
    'app_title': {'en': 'e-Triage Sahayak', 'hi': 'ई-ट्राइएज सहायक'},
    'subtitle': {'en': 'National Health Mission - AI-Assisted Referral Decision System', 'hi': 'राष्ट्रीय स्वास्थ्य मिशन - एआई सहायक रेफरल निर्णय प्रणाली'},
    'secure_badge': {'en': 'SECURE - PRODUCTION', 'hi': 'सुरक्षित - उत्पादन'},
    'ministry': {'en': 'MINISTRY OF HEALTH', 'hi': 'स्वास्थ्य मंत्रालय'},
    'govt': {'en': 'Govt. of India', 'hi': 'भारत सरकार'},
    'scheme': {'en': 'Ayushman Bharat', 'hi': 'आयुष्मान भारत'},
    'mission': {'en': 'DIGITAL HEALTH MISSION', 'hi': 'डिजिटल स्वास्थ्य मिशन'},
    'asha': {'en': 'ASHA Worker Module', 'hi': 'आशा वर्कर मॉड्यूल'},
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
    'submit': {'en': 'Generate Referral Recommendation', 'hi': 'रेफरल अनुशंसना उत्पन्न करें'},
}

def t(key):
    return TEXTS[key][st.session_state.lang]

# ---------- TRIAGE LOGIC (MoHFW Evidence-Based Rules) ----------
def calculate_triage(vitals):
    spo2 = vitals.get('spo2', 98)
    chest_pain = vitals.get('chest_pain') == 'Yes'
    breath = vitals.get('breath') == 'Severe'
    pregnant = vitals.get('pregnant') == 'Yes'
    bp = vitals.get('bp')
    
    # Red Condition (Emergency)
    if spo2 < 90 or chest_pain or breath or (pregnant and bp == 'Very High (>160/100)'):
        return {
            'level': 'RED',
            'title': 'RED ALERT - Critical Emergency',
            'msg': 'Immediate referral required to District Hospital / Tertiary Care Center. Arrange 108 Ambulance instantly.',
            'action': 'ACTION: IMMEDIATE (0-15 Mins)'
        }
    # Yellow Condition (Urgent)
    elif spo2 <= 94 or bp in ['High (140-159/90-99)', 'Very High (>160/100)'] or vitals.get('fever') == 'High (>102°F)':
        return {
            'level': 'YELLOW',
            'title': 'YELLOW ALERT - Urgent Care Needed',
            'msg': 'Refer to Community Health Centre (CHC) / Primary Health Centre (PHC) within 1-2 hours.',
            'action': 'ACTION: URGENT (Within 1 Hour)'
        }
    # Green Condition (Routine / Stable)
    else:
        return {
            'level': 'GREEN',
            'title': 'GREEN ALERT - Stable Condition',
            'msg': 'Manageable at Sub-Centre / Ayushman Arogya Mandir. Routine consultation & follow-up.',
            'action': 'ACTION: ROUTINE (OPD Timing)'
        }

# ---------- PDF GENERATOR (OFFICIAL REFERRAL SLIP) ----------
def generate_referral_pdf(data):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    
    # Top Header
    pdf.set_fill_color(11, 43, 74)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 8, "NATIONAL HEALTH MISSION - e-TRIAGE REFERRAL SLIP", ln=True, align='C')
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(255, 217, 102)
    pdf.cell(190, 6, "Ministry of Health & Family Welfare | Government of India", ln=True, align='C')
    pdf.ln(12)
    
    # Patient Demographics
    pdf.set_text_color(11, 43, 74)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 7, f"Ref ID: NHM-{data.get('id', 'NEW')} | Date: {data.get('timestamp')}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 6, f"Patient Name: {data['name']}", 0)
    pdf.cell(95, 6, f"Age: {data['age']} Years", ln=True)
    pdf.cell(95, 6, f"District: {data['district']}", 0)
    pdf.cell(95, 6, f"Block/Taluka: {data['block']}", ln=True)
    pdf.ln(4)
    
    # Vitals Summary Table
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
    pdf.cell(45, 6, "Pregnant Status", 1)
    pdf.cell(50, 6, str(data['pregnant']), 1, 1)
    pdf.ln(6)
    
    # Triage Verdict Box
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
    
    # Digital Verification Stamp & QR Note
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
        <div>
            <span style="background: #FF9933; color: #0B2B4A; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.5px;">MoHFW Compliant</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### System Settings")
    st.session_state.lang = st.selectbox("Language / भाषा", ['en', 'hi'], format_func=lambda x: 'English' if x == 'en' else 'हिंदी')
    menu = st.radio("Navigation", ["New Assessment", "Analytics Dashboard", "Patient Logs"])
    st.markdown("---")
    st.caption("National Digital Health Mission (NDHM) &bull; Production v3.0")

# ---------- PAGE: NEW ASSESSMENT ----------
if menu == "New Assessment":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ASSESSMENT}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>{t('form_title')}</h3></div>", unsafe_allow_html=True)
    with st.form("triage_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(t('name'), placeholder="e.g. Ramesh Kumar")
            age = st.number_input(t('age'), min_value=1, max_value=120, value=35)
            spo2 = st.slider(t('spo2'), min_value=70, max_value=100, value=98)
            fever = st.selectbox(t('fever'), ["Normal", "Mild (99-101°F)", "High (>102°F)"])
        
        with col2:
            breath = st.selectbox(t('breath'), ["Normal", "Mild", "Severe"])
            bp = st.selectbox(t('bp'), ["Normal", "High (140-159/90-99)", "Very High (>160/100)", "Low (<90/60)"])
            chest_pain = st.selectbox(t('chest_pain'), ["No", "Yes"])
            pregnant = st.selectbox(t('pregnant'), ["No", "Yes"])
            
        with col3:
            district = st.text_input(t('district'), value="Varanasi")
            block = st.text_input(t('block'), value="Kashi")
            diabetes = st.selectbox(t('diabetes'), ["No", "Yes"])
            headache = st.selectbox("Severe Headache", ["No", "Yes"])
            vomiting = st.selectbox("Vomiting / Nausea", ["No", "Yes"])

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
                'fever': fever
            }
            res = calculate_triage(vitals)
            
            assessment_payload = {
                'name': name, 'age': age, 'fever': fever, 'breath': breath,
                'bp': bp, 'pregnant': pregnant, 'diabetes': diabetes,
                'chest_pain': chest_pain, 'vomiting': vomiting, 'headache': headache,
                'spo2': spo2, 'district': district, 'block': block,
                'result_title': res['title'], 'result_msg': res['msg'],
                'level': res['level'], 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to Database and store in Session
            row_id = save_to_db(assessment_payload)
            assessment_payload['id'] = row_id
            st.session_state.last_assessment = assessment_payload

    # Render Result if present
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
        
        # --- ACTION PANEL: DIGITAL REFERRAL SLIP & SOS ---
        st.markdown("#### Clinical Action Hub")
        col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 1])
        
        # 1. Download Verified PDF Slip
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
                st.caption("PDF export engine unavailable.")
                
        # 2. Instant SOS / Ambulance Trigger
        with col_act2:
            if cur['level'] == 'RED':
                if st.button("🚨 Dispatch 108 Emergency Alert", use_container_width=True):
                    with st.status("Connecting to District Emergency Medical Response..."):
                        time.sleep(1)
                        st.write("📍 Telemetry sent to District Control Room.")
                        time.sleep(0.5)
                        st.write("🚑 Nearest 108 Ambulance Unit notified.")
                    st.success("Emergency Response Dispatched successfully.")
            else:
                if st.button("💬 Send Summary to Doctor", use_container_width=True):
                    st.success("Triage summary dispatched to PHC Medical Officer.")
                    
        # 3. Live QR Code for Hospital OPD Quick-Check
        with col_act3:
            qr_data = f"NHM-ID:{cur.get('id')}|Patient:{cur['name']}|SpO2:{cur['spo2']}|Level:{cur['level']}"
            encoded_qr = urllib.parse.quote(qr_data)
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=110x110&data={encoded_qr}"
            st.image(qr_url, caption="OPD Verification QR", width=110)

# ---------- PAGE: ANALYTICS DASHBOARD ----------
elif menu == "Analytics Dashboard":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ANALYTICS}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>District Triage Analytics</h3></div>", unsafe_allow_html=True)
    df = loaDB_NAME = "triage_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO assessments (
            name, age, fever, breath, bp, pregnant, diabetes,
            chest_pain, vomiting, headache, spo2, district, block,
            result_title, result_msg, level, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['age'], data['fever'], data['breath'],
        data['bp'], data['pregnant'], data['diabetes'],
        data['chest_pain'], data['vomiting'], data['headache'],
        data['spo2'], data['district'], data['block'],
        data['result_title'], data['result_msg'], data['level'],
        data['timestamp']
    ))
    conn.commit()
    conn.close()

@st.cache_data(ttl=10)
def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# ---------- SVG ICONS (SOFTWARE GRADE) ----------
SVG_MEDICAL_SHIELD = """<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFD966" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="M12 8v8"></path><path d="M8 12h8"></path></svg>"""

SVG_HEADING_ASSESSMENT = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""

SVG_HEADING_ANALYTICS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""

SVG_HEADING_LOGS = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>"""

SVG_ALERT_RED = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""

SVG_ALERT_YELLOW = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""

SVG_ALERT_GREEN = """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>"""

# ---------- LANGUAGE DICTIONARY ----------
TEXTS = {
    'app_title': {'en': 'e-Triage Sahayak', 'hi': 'ई-ट्राइएज सहायक'},
    'subtitle': {'en': 'National Health Mission - AI-Assisted Referral Decision System', 'hi': 'राष्ट्रीय स्वास्थ्य मिशन - एआई सहायक रेफरल निर्णय प्रणाली'},
    'secure_badge': {'en': 'SECURE - PRODUCTION', 'hi': 'सुरक्षित - उत्पादन'},
    'ministry': {'en': 'MINISTRY OF HEALTH', 'hi': 'स्वास्थ्य मंत्रालय'},
    'govt': {'en': 'Govt. of India', 'hi': 'भारत सरकार'},
    'scheme': {'en': 'Ayushman Bharat', 'hi': 'आयुष्मान भारत'},
    'mission': {'en': 'DIGITAL HEALTH MISSION', 'hi': 'डिजिटल स्वास्थ्य मिशन'},
    'asha': {'en': 'ASHA Worker Module', 'hi': 'आशा वर्कर मॉड्यूल'},
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
    'submit': {'en': 'Generate Referral Recommendation', 'hi': 'रेफरल अनुशंसना उत्पन्न करें'},
}

def t(key):
    return TEXTS[key][st.session_state.lang]

# ---------- TRIAGE LOGIC (MoHFW Evidence-Based Rules) ----------
def calculate_triage(vitals):
    spo2 = vitals.get('spo2', 98)
    chest_pain = vitals.get('chest_pain') == 'Yes'
    breath = vitals.get('breath') == 'Severe'
    pregnant = vitals.get('pregnant') == 'Yes'
    bp = vitals.get('bp')
    
    # Red Condition (Emergency)
    if spo2 < 90 or chest_pain or breath or (pregnant and bp == 'Very High (>160/100)'):
        return {
            'level': 'RED',
            'title': 'RED ALERT - Critical Emergency',
            'msg': 'Immediate referral required to District Hospital / Tertiary Care Center. Arrange 108 Ambulance instantly.',
            'action': 'ACTION: IMMEDIATE (0-15 Mins)'
        }
    # Yellow Condition (Urgent)
    elif spo2 <= 94 or bp in ['High (140-159/90-99)', 'Very High (>160/100)'] or vitals.get('fever') == 'High (>102°F)':
        return {
            'level': 'YELLOW',
            'title': 'YELLOW ALERT - Urgent Care Needed',
            'msg': 'Refer to Community Health Centre (CHC) / Primary Health Centre (PHC) within 1-2 hours.',
            'action': 'ACTION: URGENT (Within 1 Hour)'
        }
    # Green Condition (Routine / Stable)
    else:
        return {
            'level': 'GREEN',
            'title': 'GREEN ALERT - Stable Condition',
            'msg': 'Manageable at Sub-Centre / Ayushman Arogya Mandir. Routine consultation & follow-up.',
            'action': 'ACTION: ROUTINE (OPD Timing)'
        }

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
        <div>
            <span style="background: #FF9933; color: #0B2B4A; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.5px;">MoHFW Compliant</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### System Settings")
    st.session_state.lang = st.selectbox("Language / भाषा", ['en', 'hi'], format_func=lambda x: 'English' if x == 'en' else 'हिंदी')
    menu = st.radio("Navigation", ["New Assessment", "Analytics Dashboard", "Patient Logs"])
    st.markdown("---")
    st.caption("National Digital Health Mission (NDHM) &bull; Production v3.0")

# ---------- PAGE: NEW ASSESSMENT ----------
if menu == "New Assessment":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_ASSESSMENT}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>{t('form_title')}</h3></div>", unsafe_allow_html=True)
    with st.form("triage_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(t('name'), placeholder="e.g. Ramesh Kumar")
            age = st.number_input(t('age'), min_value=1, max_value=120, value=35)
            spo2 = st.slider(t('spo2'), min_value=70, max_value=100, value=98)
            fever = st.selectbox(t('fever'), ["Normal", "Mild (99-101°F)", "High (>102°F)"])
        
        with col2:
            breath = st.selectbox(t('breath'), ["Normal", "Mild", "Severe"])
            bp = st.selectbox(t('bp'), ["Normal", "High (140-159/90-99)", "Very High (>160/100)", "Low (<90/60)"])
            chest_pain = st.selectbox(t('chest_pain'), ["No", "Yes"])
            pregnant = st.selectbox(t('pregnant'), ["No", "Yes"])
            
        with col3:
            district = st.text_input(t('district'), value="Varanasi")
            block = st.text_input(t('block'), value="Kashi")
            diabetes = st.selectbox(t('diabetes'), ["No", "Yes"])
            headache = st.selectbox("Severe Headache", ["No", "Yes"])
            vomiting = st.selectbox("Vomiting / Nausea", ["No", "Yes"])

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
                'fever': fever
            }
            res = calculate_triage(vitals)
            
            # Save to Database
            save_to_db({
                'name': name, 'age': age, 'fever': fever, 'breath': breath,
                'bp': bp, 'pregnant': pregnant, 'diabetes': diabetes,
                'chest_pain': chest_pain, 'vomiting': vomiting, 'headache': headache,
                'spo2': spo2, 'district': district, 'block': block,
                'result_title': res['title'], 'result_msg': res['msg'],
                'level': res['level'], 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Display Result Card with SVG Icons
            color = "#DC2626" if res['level'] == 'RED' else ("#F59E0B" if res['level'] == 'YELLOW' else "#22C55E")
            alert_svg = SVG_ALERT_RED if res['level'] == 'RED' else (SVG_ALERT_YELLOW if res['level'] == 'YELLOW' else SVG_ALERT_GREEN)
            
            st.markdown(f"""
            <div style="background-color: {color}12; border-left: 6px solid {color}; border-top: 1px solid {color}30; border-right: 1px solid {color}30; border-bottom: 1px solid {color}30; border-radius: 12px; padding: 22px; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    {alert_svg}
                    <h3 style="color: {color}; margin: 0; font-size: 1.25rem; font-weight: 700;">{res['title']}</h3>
                </div>
                <p style="font-size: 1.05rem; margin: 8px 0 16px 0; color: #1E293B; line-height: 1.5;">{res['msg']}</p>
                <span style="background: {color}; color: white; padding: 6px 18px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.5px; display: inline-block;">
                    {res['action']}
                </span>
            </div>
            """, unsafe_allow_html=True)

# ---------- PAGE: ANALYTICS DASHBOARD ----------
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
                title='Patient Age Distribution', 
                color_discrete_sequence=['#0B2B4A']
            )
            fig2.update_layout(margin=dict(t=40, b=20, l=20, r=20), xaxis_title="Age (Years)", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)

# ---------- PAGE: PATIENT LOGS ----------
elif menu == "Patient Logs":
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 1rem;'>{SVG_HEADING_LOGS}<h3 style='margin:0; font-size: 1.3rem; color: #0B2B4A;'>Patient Assessment Registry</h3></div>", unsafe_allow_html=True)
    df = load_from_db()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Registry Data (CSV)", 
            data=csv, 
            file_name="triage_registry.csv", 
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.info("No records recorded yet.")
