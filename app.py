import streamlit as st
import datetime
import time
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NHM e-Triage | Govt. of India",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "National Health Mission - e-Triage System v3.0"
    }
)

# ---------- SESSION STATE INIT ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'history' not in st.session_state:
    st.session_state.history = []
if 'sync_time' not in st.session_state:
    st.session_state.sync_time = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False

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
    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
    conn.close()
    return df

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
    'form_desc': {'en': 'Enter the primary vitals and symptoms. The system will generate an evidence-based triage recommendation as per MoHFW guidelines.', 'hi': 'प्राथमिक महत्वपूर्ण लक्षण और लक्षण दर्ज करें। सिस्टम MoHFW दिशानिर्देशों के अनुसार साक्ष्य-आधारित ट्राइएज सिफारिश उत्पन्न करेगा।'},
    'name': {'en': 'Patient Full Name', 'hi': 'रोगी का पूरा नाम'},
    'age': {'en': 'Age (in years)', 'hi': 'आयु (वर्षों में)'},
    'fever': {'en': 'Fever / High Temperature', 'hi': 'बुखार / तेज बुखार'},
    'breath': {'en': 'Breathing Difficulty', 'hi': 'सांस लेने में कठिनाई'},
    'bp': {'en': 'Blood Pressure (BP) Status', 'hi': 'रक्तचाप (बीपी) स्थिति'},
    'pregnant': {'en': 'Patient is Pregnant?', 'hi': 'क्या रोगी गर्भवती है?'},
    'diabetes': {'en': 'History of Diabetes?', 'hi': 'मधुमेह का इतिहास?'},
    'chest_pain': {'en': 'Chest Pain / Discomfort', 'hi': 'सीने में दर्द / बेचैनी'},
    'vomiting': {'en': 'Vomiting / Nausea', 'hi': 'उल्टी / मतली'},
    'headache': {'en': 'Severe Headache', 'hi': 'तीव्र सिरदर्द'},
    'spo2': {'en': 'Oxygen Level (SpO2 %)', 'hi': 'ऑक्सीजन स्तर (SpO2 %)'},
    'district': {'en': 'District', 'hi': 'जिला'},
    'block': {'en': 'Block / Taluka', 'hi': 'ब्लॉक / तालुका'},
    'submit': {'en': 'Generate Referral Recommendation', 'hi': 'रेफरल अनुशंसना उत्पन्न करें'},
    'history_title': {'en': 'Previous Assessments', 'hi': 'पिछले मूल्यांकन'},
    'no_history': {'en': 'No assessments recorded yet.', 'hi': 'अभी तक कोई मूल्यांकन रिकॉर्ड नहीं किया गया है।'},
    'sync_btn': {'en': 'Sync with Health Department', 'hi': 'स्वास्थ्य विभाग से सिंक करें'},
    'synced': {'en': 'Synced at', 'hi': 'सिंक हुआ'},
    'pdf_btn': {'en': 'Download PDF Report', 'hi': 'पीडीएफ रिपोर्ट डाउनलोड करें'},
    'logout': {'en': 'Logout', 'hi': 'लॉगआउट'},
    'login_title': {'en': 'e-Triage Login', 'hi': 'ई-ट्राइएज लॉगिन'},
    'username': {'en': 'Username', 'hi': 'उपयोगकर्ता नाम'},
    'password': {'en': 'Password', 'hi': 'पासवर्ड'},
    'login_btn': {'en': 'Login', 'hi': 'लॉगिन'},
    'invalid': {'en': 'Invalid username or password', 'hi': 'अमान्य उपयोगकर्ता नाम या पासवर्ड'},
    'red_alert': {'en': 'RED ALERT - Critical', 'hi': 'लाल अलर्ट - गंभीर'},
    'yellow_alert': {'en': 'YELLOW ALERT - Moderate', 'hi': 'पीला अलर्ट - मध्यम'},
    'green_alert': {'en': 'GREEN ALERT - Stable', 'hi': 'हरा अलर्ट - स्थिर'},
    'action_immediate': {'en': 'ACTION: IMMEDIATE (0-15 Mins)', 'hi': 'कार्रवाई: तत्काल (0-15 मिनट)'},
    'action_urgent': {'en': 'ACTION: URGENT (Within 1 Hour)', 'hi': 'कार्रवाई: अत्यावश्यक (1 घंटे के भीतर)'},
    'action_routine': {'en': 'ACTION: ROUTINE (OPD Timing)', 'hi': 'कार्रवाई: नियमित (ओपीडी समय)'},
    'footer': {'en': 'National Digital Health Mission (NDHM) - Compliance: MoHFW Guidelines v.2.4', 'hi': 'राष्ट्रीय डिजिटल स्वास्थ्य मिशन (NDHM) - अनुपालन: MoHFW दिशानिर्देश v.2.4'},
    'alert_sent': {'en': 'Alert sent to CMO & District Hospital! (Dummy)', 'hi': 'CMO और जिला अस्पताल को अलर्ट भेजा गया! (डमी)'},
    'send_alert': {'en': 'Send Alert to Doctor', 'hi': 'डॉक्टर को अलर्ट भेजें'},
}

def t(key):
    return TEXTS[key][st.session_state.lang]

# ---------- CSS (Dark mode + Print + Animations) ----------
def get_css():
    bg = "#0B2B4A" if st.session_state.dark_mode else "#F4F7FB"
    card_bg = "#1E2A3A" if st.session_state.dark_mode else "#FFFFFF"
    text_color = "white" if st.session_state.dark_mode else "#0B2B4A"
    sub_text = "#A0C4E8" if st.session_state.dark_mode else "#5E6F7E"
    border_color = "#2E3A4A" if st.session_state.dark_mode else "#E2E8F0"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        .stApp {{ background-color: {bg}; transition: background-color 0.3s ease; }}
        
        /* SPLASH SCREEN */
        .splash-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #0B2B4A; display: flex; flex-direction: column;
            align-items: center; justify-content: center; z-index: 9999;
            color: white; font-family: 'Inter', sans-serif;
        }}
        .splash-logo {{ font-size: 4rem; background: #FF9933; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; color: #0B2B4A; font-weight: 900; margin-bottom: 20px; }}
        .splash-loader {{ width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid #FF9933; border-radius: 50%; animation: spin 1s linear infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .fade-in {{ animation: fadeIn 0.6s ease-in-out; }}
        
        /* Tricolor */
        .tricolor-strip {{ display: flex; height: 6px; width: 100%; position: fixed; top: 0; left: 0; z-index: 999; }}
        .tricolor-saffron {{ flex: 1; background-color: #FF9933; }}
        .tricolor-white {{ flex: 1; background-color: #FFFFFF; }}
        .tricolor-green {{ flex: 1; background-color: #138808; }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{ background-color: #0B2B4A; padding: 1rem; }}
        .sidebar-content {{ display: flex; flex-direction: column; align-items: center; color: white; text-align: center; }}
        .sidebar-ministry {{ font-weight: 700; font-size: 1.1rem; color: white; margin-top: 10px; }}
        .sidebar-sub {{ font-size: 0.7rem; color: #7AA9D9; }}
        .sidebar-tag {{ background-color: #FF9933; color: #0B2B4A; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.7rem; display: inline-block; margin: 5px auto; }}
        .sidebar-menu {{ color: #A0C4E8; font-size: 0.75rem; margin: 8px 0; width: 100%; text-align: left; padding-left: 10px; }}
        .sidebar-footer {{ font-size: 0.6rem; color: #4A7BA7; margin-top: 20px; text-align: center; border-top: 1px solid #1E4A6F; padding-top: 15px; width: 100%; }}
        
        /* Main Header */
        .main-header {{
            background: linear-gradient(135deg, #0B2B4A 0%, #1A4A70 100%);
            padding: 1.8rem 2.5rem; border-radius: 0px 0px 20px 20px;
            margin-top: -10px; box-shadow: 0 6px 25px rgba(11, 43, 74, 0.3);
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; margin-bottom: 2rem;
        }}
        .header-title {{ color: white; font-weight: 700; font-size: 1.8rem; letter-spacing: -0.5px; margin: 0; }}
        .header-sub {{ color: #FFD966; font-weight: 400; font-size: 0.9rem; margin: 0; opacity: 0.9; }}
        .header-badge {{ background: rgba(255,255,255,0.15); backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.2); padding: 6px 18px; border-radius: 50px; color: white; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; white-space: nowrap; }}
        
        /* Form Card */
        .form-card {{
            background: {card_bg};
            padding: 2.5rem 3rem; border-radius: 24px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.06);
            border: 1px solid {border_color};
            margin-bottom: 2rem;
            transition: background 0.3s ease, border 0.3s ease;
        }}
        .form-card h3 {{ color: {text_color}; font-weight: 600; font-size: 1.4rem; margin-bottom: 0.2rem; }}
        .form-desc {{ color: {sub_text}; font-size: 0.95rem; border-left: 3px solid #FF9933; padding-left: 15px; margin-bottom: 1.5rem; }}
        .input-label {{ display: flex; align-items: center; gap: 10px; font-weight: 600; color: {text_color}; margin-bottom: 0.2rem; font-size: 0.9rem; }}
        
        /* Result Boxes */
        .result-container {{
            padding: 1.8rem 2rem; border-radius: 16px; margin-top: 1.5rem;
            border: 1px solid; display: flex; gap: 20px;
            align-items: flex-start; flex-wrap: wrap;
            animation: fadeIn 0.5s ease-out;
        }}
        .result-icon svg {{ width: 48px; height: 48px; flex-shrink: 0; }}
        .result-text h2 {{ margin: 0 0 5px 0; font-weight: 700; }}
        .result-text p {{ margin: 0 0 8px 0; font-size: 1.05rem; line-height: 1.5; word-wrap: break-word; overflow-wrap: break-word; }}
        .action-tag {{ padding: 4px 16px; border-radius: 50px; font-size: 0.8rem; font-weight: 700; display: inline-block; }}
        
        .result-red {{ background: #FEF2F2; border-color: #DC2626; }}
        .result-red .action-tag {{ background: #DC2626; color: white; }}
        .result-red h2 {{ color: #991B1B; }}
        .result-yellow {{ background: #FFFBEB; border-color: #F59E0B; }}
        .result-yellow .action-tag {{ background: #F59E0B; color: white; }}
        .result-yellow h2 {{ color: #92400E; }}
        .result-green {{ background: #F0FDF4; border-color: #22C55E; }}
        .result-green .action-tag {{ background: #22C55E; color: white; }}
        .result-green h2 {{ color: #166534; }}
        
        /* Dark mode overrides */
        {'''
        .result-red {{ background: #2A1515; border-color: #DC2626; }}
        .result-red h2 {{ color: #F87171; }}
        .result-yellow {{ background: #2A2515; border-color: #F59E0B; }}
        .result-yellow h2 {{ color: #FCD34D; }}
        .result-green {{ background: #152A1A; border-color: #22C55E; }}
        .result-green h2 {{ color: #6EE7B7; }}
        ''' if st.session_state.dark_mode else ''}
        
        /* Footer */
        .software-footer {{
            border-top: 1px solid {border_color};
            padding-top: 1.5rem; margin-top: 2rem;
            display: flex; justify-content: space-between;
            font-size: 0.75rem; color: {sub_text};
            flex-wrap: wrap; gap: 10px;
        }}
        .software-footer .ver {{ background: {border_color}; padding: 2px 12px; border-radius: 30px; color: {text_color}; }}
        
        /* Responsive */
        @media screen and (max-width: 768px) {{
            .main-header {{ flex-direction: column; align-items: flex-start; gap: 10px; padding: 1.2rem 1.5rem; }}
            .header-title {{ font-size: 1.5rem; }}
            .header-sub {{ font-size: 0.8rem; }}
            .header-badge {{ font-size: 0.65rem; padding: 4px 12px; }}
            .form-card {{ padding: 1.5rem 1.2rem; }}
            .form-card h3 {{ font-size: 1.2rem; }}
            .result-container {{ flex-direction: column; align-items: stretch; padding: 1.2rem; }}
            .result-icon {{ text-align: center; }}
            .result-text h2 {{ font-size: 1.2rem; }}
            .software-footer {{ flex-direction: column; align-items: center; text-align: center; }}
            .stButton>button {{ width: 100% !important; }}
            .input-label {{ gap: 15px; margin-top: 10px !important; }}
        }}
        @media screen and (max-width: 480px) {{
            .header-title {{ font-size: 1.2rem; }}
            .form-card {{ padding: 1rem; }}
            .input-label {{ font-size: 0.8rem; }}
        }}
        
        /* Button Hover */
        .stButton>button {{
            transition: all 0.3s ease !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        }}
        
        .sync-badge {{
            background: #22C55E; color: white; padding: 4px 12px;
            border-radius: 20px; font-size: 0.7rem; font-weight: 600;
            display: inline-block;
        }}
        
        /* ---------- PRINT CSS ---------- */
        @media print {{
            section[data-testid="stSidebar"] {{ display: none !important; }}
            .main-header {{ display: none !important; }}
            .stButton {{ display: none !important; }}
            .tricolor-strip {{ display: none !important; }}
            .software-footer {{ display: none !important; }}
            .form-card {{
                box-shadow: none !important;
                border: 1px solid #000 !important;
                padding: 1rem !important;
            }}
            .result-container {{
                break-inside: avoid;
                border: 2px solid #000 !important;
            }}
            .stApp {{ background: white !important; }}
        }}
    </style>
    """

# ---------- SVG ICONS ----------
ASHOKA_CHAKRA = '''
<svg width="70" height="70" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="background: #FF9933; border-radius: 50%; padding: 6px;">
    <circle cx="12" cy="12" r="10" stroke="#0B2B4A" stroke-width="1.5"/>
    <path d="M12 2 V4 M12 20 V22 M2 12 H4 M20 12 H22 M4.93 4.93 L6.34 6.34 M17.66 17.66 L19.07 19.07 M4.93 19.07 L6.34 17.66 M17.66 6.34 L19.07 4.93" stroke="#0B2B4A" stroke-width="1.5"/>
    <circle cx="12" cy="12" r="2" fill="#0B2B4A"/>
    <path d="M12 4 L12 6 M12 18 L12 20 M4 12 L6 12 M18 12 L20 12 M5.6 5.6 L7.0 7.0 M17.0 17.0 L18.4 18.4 M5.6 18.4 L7.0 17.0 M17.0 7.0 L18.4 5.6 M8.2 4.5 L8.8 6.3 M15.2 17.7 L15.8 19.5 M4.5 8.2 L6.3 8.8 M17.7 15.2 L19.5 15.8 M4.5 15.8 L6.3 15.2 M17.7 8.8 L19.5 8.2 M8.2 19.5 L8.8 17.7 M15.2 4.5 L15.8 6.3" stroke="#0B2B4A" stroke-width="0.8"/>
</svg>
'''

def icon_user(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M5.3 20a8 8 0 0 1 13.4 0"/></svg>'
def icon_fever(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><circle cx="12" cy="12" r="3"/><path d="M14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/></svg>'
def icon_lungs(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><path d="M6.5 6.5c-2 2-2 5.5 0 8.5M17.5 6.5c2 2 2 5.5 0 8.5M12 3v18M8 21h8M8 3h8M12 12c-2-2-4-4.5-4-7 0-2 2-3 4-3s4 1 4 3c0 2.5-2 5-4 7z"/></svg>'
def icon_heart(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
def icon_pregnant(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 13v6M9 16h6"/><path d="M5 21a8 8 0 0 1 14 0"/></svg>'
def icon_diabetes(): return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#' + ('white' if st.session_state.dark_mode else '0B2B4A') + '" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>'
def icon_alert_red(): return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>'
def icon_alert_yellow(): return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 2 L2 20 L22 20 L12 2z"/><path d="M12 9v4M12 17h.01"/></svg>'
def icon_alert_green(): return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>'

# ---------- INIT DATABASE ----------
init_db()

# ---------- SPLASH SCREEN ----------
if not st.session_state.splash_done:
    splash_html = f'''
    <div class="splash-container">
        <div class="splash-logo">⚕️</div>
        <h1 style="color: #FF9933; font-weight: 700;">{t('ministry'
