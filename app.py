import streamlit as st
import datetime
import time
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NHM e-Triage | Govt. of India",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE INIT ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # Testing ke liye True / Production me login screen use karein
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'role' not in st.session_state:
    st.session_state.role = 'ASHA Worker'

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

@st.cache_data(ttl=10)
def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

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
st.markdown("""
<div style="background: linear-gradient(135deg, #0B2B4A 0%, #1A4A70 100%); padding: 1.2rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h2 style="margin: 0; color: white;">⚕️ National Health Mission | e-Triage</h2>
            <p style="margin: 0; color: #FFD966; font-size: 0.85rem;">Ayushman Bharat - AI-Assisted Clinical Decision Support</p>
        </div>
        <div>
            <span style="background: #FF9933; color: #0B2B4A; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">MoHFW Compliant</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    st.session_state.lang = st.selectbox("🌐 Language / भाषा", ['en', 'hi'], format_func=lambda x: 'English' if x == 'en' else 'हिंदी')
    menu = st.radio("Navigation", ["New Assessment", "Analytics Dashboard", "Patient Logs"])
    st.markdown("---")
    st.caption("National Digital Health Mission (NDHM)")

# ---------- PAGE: NEW ASSESSMENT ----------
if menu == "New Assessment":
    st.subheader(t('form_title'))
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

            # Display Result Card
            color = "#DC2626" if res['level'] == 'RED' else ("#F59E0B" if res['level'] == 'YELLOW' else "#22C55E")
            st.markdown(f"""
            <div style="background-color: {color}15; border: 2px solid {color}; border-radius: 12px; padding: 20px; margin-top: 20px;">
                <h3 style="color: {color}; margin: 0;">{res['title']}</h3>
                <p style="font-size: 1.1rem; margin: 10px 0;">{res['msg']}</p>
                <span style="background: {color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">
                    {res['action']}
                </span>
            </div>
            """, unsafe_allow_html=True)

# ---------- PAGE: ANALYTICS DASHBOARD ----------
elif menu == "Analytics Dashboard":
    st.subheader("📊 District Triage Analytics")
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
            fig1 = px.pie(df, names='level', title='Triage Distribution', color='level',
                          color_discrete_map={'RED': '#DC2626', 'YELLOW': '#F59E0B', 'GREEN': '#22C55E'})
            st.plotly_chart(fig1, use_container_width=True)
        with col_c2:
            fig2 = px.histogram(df, x='age', nbins=15, title='Patient Age Distribution', color_discrete_sequence=['#0B2B4A'])
            st.plotly_chart(fig2, use_container_width=True)

# ---------- PAGE: PATIENT LOGS ----------
elif menu == "Patient Logs":
    st.subheader("📋 Patient Assessment Registry")
    df = load_from_db()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Registry CSV", csv, "triage_registry.csv", "text/csv")
    else:
        st.info("No records recorded yet.")
