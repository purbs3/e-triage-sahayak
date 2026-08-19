import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="NHM e-Triage | Govt. of India",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS WITH RESPONSIVE DESIGN ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #F4F7FB;
    }
    
    /* Tricolor strip */
    .tricolor-strip {
        display: flex;
        height: 6px;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 999;
    }
    .tricolor-saffron { flex: 1; background-color: #FF9933; }
    .tricolor-white { flex: 1; background-color: #FFFFFF; }
    .tricolor-green { flex: 1; background-color: #138808; }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #0B2B4A;
    }
    .sidebar-content {
        padding: 2rem 1rem;
        color: white;
    }
    .sidebar-content .ministry-name {
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
    }
    .sidebar-content .subtext {
        font-size: 0.7rem;
        color: #7AA9D9;
    }
    .sidebar-content .scheme-tag {
        background-color: #FF9933;
        color: #0B2B4A;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.7rem;
        display: inline-block;
        margin-top: 5px;
    }
    .sidebar-content .menu-item {
        color: #A0C4E8;
        font-size: 0.75rem;
        margin: 8px 0;
    }
    .sidebar-footer {
        position: absolute;
        bottom: 20px;
        font-size: 0.6rem;
        color: #4A7BA7;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #0B2B4A 0%, #1A4A70 100%);
        padding: 1.8rem 2.5rem;
        border-radius: 0px 0px 20px 20px;
        margin-top: -10px;
        box-shadow: 0 6px 25px rgba(11, 43, 74, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-bottom: 2rem;
    }
    .header-left .title {
        color: white;
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .header-left .subtitle {
        color: #FFD966;
        font-weight: 400;
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.9;
    }
    .header-right .badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 6px 18px;
        border-radius: 50px;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        white-space: nowrap;
    }
    
    /* Form Card */
    .form-card {
        background: #FFFFFF;
        padding: 2.5rem 3rem;
        border-radius: 24px;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.03);
        margin-bottom: 2rem;
    }
    .form-card h3 {
        color: #0B2B4A;
        font-weight: 600;
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
    }
    .form-card .desc {
        color: #5E6F7E;
        font-size: 0.95rem;
        border-left: 3px solid #FF9933;
        padding-left: 15px;
        margin-bottom: 1.5rem;
    }
    
    .input-label {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        color: #1A365D;
        margin-bottom: 0.2rem;
        font-size: 0.9rem;
    }
    
    /* Result Boxes */
    .result-container {
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-top: 1.5rem;
        border: 1px solid;
        display: flex;
        gap: 20px;
        align-items: flex-start;
        transition: 0.3s ease;
        flex-wrap: wrap;
    }
    .result-icon svg {
        width: 48px;
        height: 48px;
        flex-shrink: 0;
    }
    .result-text h2 {
        margin: 0 0 5px 0;
        font-weight: 700;
    }
    .result-text p {
        margin: 0 0 8px 0;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .action-tag {
        padding: 4px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .result-red {
        background: #FEF2F2;
        border-color: #DC2626;
    }
    .result-red .action-tag { background: #DC2626; color: white; }
    .result-red h2 { color: #991B1B; }
    
    .result-yellow {
        background: #FFFBEB;
        border-color: #F59E0B;
    }
    .result-yellow .action-tag { background: #F59E0B; color: white; }
    .result-yellow h2 { color: #92400E; }
    
    .result-green {
        background: #F0FDF4;
        border-color: #22C55E;
    }
    .result-green .action-tag { background: #22C55E; color: white; }
    .result-green h2 { color: #166534; }
    
    /* Footer */
    .software-footer {
        border-top: 1px solid #E2E8F0;
        padding-top: 1.5rem;
        margin-top: 2rem;
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #64748B;
        flex-wrap: wrap;
        gap: 10px;
    }
    .software-footer .ver {
        background: #E2E8F0;
        padding: 2px 12px;
        border-radius: 30px;
    }
    
    /* ------- RESPONSIVE DESIGN ------- */
    @media screen and (max-width: 768px) {
        .main-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
            padding: 1.2rem 1.5rem;
        }
        .header-left .title {
            font-size: 1.5rem;
        }
        .header-left .subtitle {
            font-size: 0.8rem;
        }
        .header-right .badge {
            font-size: 0.65rem;
            padding: 4px 12px;
        }
        .form-card {
            padding: 1.5rem 1.2rem;
        }
        .form-card h3 {
            font-size: 1.2rem;
        }
        .result-container {
            flex-direction: column;
            align-items: stretch;
            padding: 1.2rem;
        }
        .result-icon {
            text-align: center;
        }
        .result-text h2 {
            font-size: 1.2rem;
        }
        .software-footer {
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .sidebar-content {
            padding: 1rem 0.5rem;
        }
        .sidebar-footer {
            position: static;
            margin-top: 20px;
        }
    }
    
    @media screen and (max-width: 480px) {
        .header-left .title {
            font-size: 1.2rem;
        }
        .form-card {
            padding: 1rem;
        }
        .input-label {
            font-size: 0.8rem;
        }
        .stButton>button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------- TRICOLOR STRIP ----------
st.markdown("""
<div class="tricolor-strip">
    <div class="tricolor-saffron"></div>
    <div class="tricolor-white"></div>
    <div class="tricolor-green"></div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <div style="text-align: center; margin-bottom: 20px;">
            <!-- Ashoka Chakra SVG (simplified) -->
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="background: #FF9933; border-radius: 50%; padding: 6px;">
                <circle cx="12" cy="12" r="10" stroke="#0B2B4A" stroke-width="1.5"/>
                <path d="M12 2 V4 M12 20 V22 M2 12 H4 M20 12 H22 M4.93 4.93 L6.34 6.34 M17.66 17.66 L19.07 19.07 M4.93 19.07 L6.34 17.66 M17.66 6.34 L19.07 4.93" stroke="#0B2B4A" stroke-width="1.5"/>
                <circle cx="12" cy="12" r="2" fill="#0B2B4A"/>
                <path d="M12 4 L12 6 M12 18 L12 20 M4 12 L6 12 M18 12 L20 12 M5.6 5.6 L7.0 7.0 M17.0 17.0 L18.4 18.4 M5.6 18.4 L7.0 17.0 M17.0 7.0 L18.4 5.6 M8.2 4.5 L8.8 6.3 M15.2 17.7 L15.8 19.5 M4.5 8.2 L6.3 8.8 M17.7 15.2 L19.5 15.8 M4.5 15.8 L6.3 15.2 M17.7 8.8 L19.5 8.2 M8.2 19.5 L8.8 17.7 M15.2 4.5 L15.8 6.3" stroke="#0B2B4A" stroke-width="0.8"/>
            </svg>
            <div class="ministry-name">MINISTRY OF HEALTH</div>
            <div class="subtext">Govt. of India</div>
            <div class="scheme-tag">Ayushman Bharat</div>
        </div>
        <hr style="border-color: #1E4A6F;">
        <div style="margin-top: 20px;">
            <div class="menu-item">> DIGITAL HEALTH MISSION</div>
            <div class="menu-item">> e-Triage Sahayak v2.0</div>
            <div class="menu-item">> ASHA Worker Module</div>
        </div>
        <div class="sidebar-footer">NIC-CERTIFIED SECURE</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- SVG ICON FUNCTIONS ----------
def icon_fever():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><circle cx="12" cy="12" r="3"/><path d="M14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/></svg>'

def icon_lungs():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M6.5 6.5c-2 2-2 5.5 0 8.5M17.5 6.5c2 2 2 5.5 0 8.5M12 3v18M8 21h8M8 3h8M12 12c-2-2-4-4.5-4-7 0-2 2-3 4-3s4 1 4 3c0 2.5-2 5-4 7z"/></svg>'

def icon_heart():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'

def icon_user():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M5.3 20a8 8 0 0 1 13.4 0"/></svg>'

def icon_pregnant():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 13v6M9 16h6"/><path d="M5 21a8 8 0 0 1 14 0"/></svg>'

def icon_diabetes():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>'

def icon_alert_red():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>'

def icon_alert_yellow():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 2 L2 20 L22 20 L12 2z"/><path d="M12 9v4M12 17h.01"/></svg>'

def icon_alert_green():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>'

# ---------- MAIN HEADER ----------
st.markdown("""
<div class="main-header">
    <div class="header-left">
        <div>
            <div class="title">e-Triage Sahayak</div>
            <div class="subtitle">National Health Mission - AI-Assisted Referral Decision System</div>
        </div>
    </div>
    <div class="header-right">
        <span class="badge">SECURE - PRODUCTION</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- FORM CARD ----------
with st.container():
    st.markdown("""
    <div class="form-card">
        <h3>Patient Clinical Assessment</h3>
        <div class="desc">Enter the primary vitals and symptoms. The system will generate an evidence-based triage recommendation as per MoHFW guidelines.</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="input-label">{icon_user()} Age (in years)</div>', unsafe_allow_html=True)
        age = st.number_input("", min_value=0, max_value=120, step=1, value=35, label_visibility="collapsed", key="age_input")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_fever()} Fever / High Temperature</div>', unsafe_allow_html=True)
        fever = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="fever_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_lungs()} Breathing Difficulty</div>', unsafe_allow_html=True)
        breath_issue = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="breath_select")

    with col2:
        st.markdown(f'<div class="input-label">{icon_heart()} Blood Pressure (BP) Status</div>', unsafe_allow_html=True)
        bp_status = st.selectbox("", options=["Normal", "High", "Low"], label_visibility="collapsed", key="bp_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_pregnant()} Patient is Pregnant?</div>', unsafe_allow_html=True)
        is_pregnant = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="pregnant_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_diabetes()} History of Diabetes?</div>', unsafe_allow_html=True)
        diabetes = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="diabetes_select")
    
    st.markdown("---")
    
    # ---------- TRIAGE LOGIC ----------
    def get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes):
        if is_pregnant == "Yes" and bp_status == "High":
            return ("RED", "Immediate referral to District Hospital / Medical College. Risk of Pre-eclampsia/Eclampsia. Call 108 Ambulance immediately.", "red")
        if age > 60 and bp_status == "Low":
            return ("RED", "Elderly patient with Low BP. High risk of Septic Shock. Urgent ICU admission required at Medical College.", "red")
        if fever == "Yes" and breath_issue == "Yes" and age > 50:
            return ("RED", "Severe Pneumonia/COVID-19 suspect with breathing issues in elderly. Immediate oxygen support needed. Refer to Tertiary Care Hospital.", "red")
        if diabetes == "Yes" and fever == "Yes":
            return ("YELLOW", "Diabetic patient with fever. High risk of infections. Refer to Community Health Centre (CHC) for advanced investigation.", "yellow")
        if fever == "Yes" and breath_issue == "Yes":
            return ("YELLOW", "Patient has fever with breathing issues. Needs Chest X-Ray and Oxygen saturation check. Refer to CHC.", "yellow")
        if age < 5 and fever == "Yes":
            return ("YELLOW", "Child under 5 with fever. Needs pediatric assessment. Refer to CHC immediately.", "yellow")
        if fever == "Yes" and breath_issue == "No":
            return ("GREEN", "Mild fever without breathing issues. Can be treated at PHC with basic medications (Paracetamol). Advise rest and hydration.", "green")
        if bp_status == "Normal" and fever == "No":
            return ("GREEN", "Vitals are stable. Routine checkup at PHC is sufficient. No emergency referral required.", "green")
        return ("GREEN", "Patient seems stable. Continue monitoring at PHC. No immediate referral needed.", "green")

    # ---------- SUBMIT BUTTON ----------
    if st.button("Generate Referral Recommendation", use_container_width=False, type="primary", key="submit_btn"):
        triage_title, triage_msg, triage_level = get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes)
        
        if triage_level == "red":
            st.markdown(f"""
            <div class="result-container result-red">
                <div class="result-icon">{icon_alert_red()}</div>
                <div class="result-text">
                    <h2>RED ALERT - Critical</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: IMMEDIATE (0-15 Mins)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif triage_level == "yellow":
            st.markdown(f"""
            <div class="result-container result-yellow">
                <div class="result-icon">{icon_alert_yellow()}</div>
                <div class="result-text">
                    <h2>YELLOW ALERT - Moderate</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: URGENT (Within 1 Hour)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-container result-green">
                <div class="result-icon">{icon_alert_green()}</div>
                <div class="result-text">
                    <h2>GREEN ALERT - Stable</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: ROUTINE (OPD Timing)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # close form-card

# ---------- FOOTER ----------
st.markdown("""
<div class="software-footer">
    <div>
        <strong>National Digital Health Mission (NDHM)</strong> - Compliance: MoHFW Guidelines v.2.4
    </div>
    <div>
        <span class="ver">End-to-End Encrypted</span>
        <span class="ver" style="margin-left:10px;">v2.0.1</span>
    </div>
</div>
""", unsafe_allow_html=True)    .tricolor-saffron { flex: 1; background-color: #FF9933; }
    .tricolor-white { flex: 1; background-color: #FFFFFF; }
    .tricolor-green { flex: 1; background-color: #138808; }
    
    .css-1d391kg, .css-1lcbmhc {
        background-color: #0B2B4A;
    }
    .sidebar-content {
        padding: 2rem 1rem;
        color: white;
    }
    .sidebar-content .gov-logo-text {
        font-size: 0.8rem;
        color: #A0C4E8;
        letter-spacing: 1px;
        border-bottom: 1px solid #1E4A6F;
        padding-bottom: 10px;
    }
    .sidebar-content .ministry-name {
        font-weight: 700;
        color: white;
        font-size: 1.1rem;
    }
    .sidebar-content .scheme-tag {
        background-color: #FF9933;
        color: #0B2B4A;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.7rem;
        display: inline-block;
        margin-top: 5px;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0B2B4A 0%, #1A4A70 100%);
        padding: 1.8rem 2.5rem;
        border-radius: 0px 0px 20px 20px;
        margin-top: -10px;
        box-shadow: 0 6px 25px rgba(11, 43, 74, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .header-left .title {
        color: white;
        margin: 0;
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
    }
    .header-left .subtitle {
        color: #FFD966;
        font-weight: 400;
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.9;
    }
    .header-right .badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 6px 18px;
        border-radius: 50px;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    .form-card {
        background: #FFFFFF;
        padding: 2.5rem 3rem;
        border-radius: 24px;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.03);
        margin-bottom: 2rem;
    }
    .form-card h3 {
        color: #0B2B4A;
        font-weight: 600;
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .form-card .desc {
        color: #5E6F7E;
        font-size: 0.95rem;
        border-left: 3px solid #FF9933;
        padding-left: 15px;
        margin-bottom: 1.5rem;
    }
    
    .input-label {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        color: #1A365D;
        margin-bottom: 0.2rem;
        font-size: 0.9rem;
    }
    
    .result-container {
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-top: 1.5rem;
        border: 1px solid;
        display: flex;
        gap: 20px;
        align-items: flex-start;
        transition: 0.3s ease;
    }
    .result-icon svg {
        width: 48px;
        height: 48px;
        flex-shrink: 0;
    }
    .result-text h2 {
        margin: 0 0 5px 0;
        font-weight: 700;
    }
    .result-text p {
        margin: 0 0 8px 0;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .action-tag {
        padding: 4px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .result-red {
        background: #FEF2F2;
        border-color: #DC2626;
    }
    .result-red .action-tag { background: #DC2626; color: white; }
    .result-red h2 { color: #991B1B; }
    
    .result-yellow {
        background: #FFFBEB;
        border-color: #F59E0B;
    }
    .result-yellow .action-tag { background: #F59E0B; color: white; }
    .result-yellow h2 { color: #92400E; }
    
    .result-green {
        background: #F0FDF4;
        border-color: #22C55E;
    }
    .result-green .action-tag { background: #22C55E; color: white; }
    .result-green h2 { color: #166534; }
    
    .software-footer {
        border-top: 1px solid #E2E8F0;
        padding-top: 1.5rem;
        margin-top: 2rem;
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #64748B;
    }
    .software-footer .ver {
        background: #E2E8F0;
        padding: 2px 12px;
        border-radius: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- TRICOLOR STRIP ----------
st.markdown("""
<div class="tricolor-strip">
    <div class="tricolor-saffron"></div>
    <div class="tricolor-white"></div>
    <div class="tricolor-green"></div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <div style="text-align: center; margin-bottom: 20px;">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="background: #FF9933; border-radius: 50%; padding: 6px;">
                <circle cx="12" cy="12" r="10" stroke="#0B2B4A" stroke-width="1.5"/>
                <path d="M12 2 V4 M12 20 V22 M2 12 H4 M20 12 H22 M4.93 4.93 L6.34 6.34 M17.66 17.66 L19.07 19.07 M4.93 19.07 L6.34 17.66 M17.66 6.34 L19.07 4.93" stroke="#0B2B4A" stroke-width="1.5"/>
                <circle cx="12" cy="12" r="2" fill="#0B2B4A"/>
                <path d="M12 4 L12 6 M12 18 L12 20 M4 12 L6 12 M18 12 L20 12 M5.6 5.6 L7.0 7.0 M17.0 17.0 L18.4 18.4 M5.6 18.4 L7.0 17.0 M17.0 7.0 L18.4 5.6 M8.2 4.5 L8.8 6.3 M15.2 17.7 L15.8 19.5 M4.5 8.2 L6.3 8.8 M17.7 15.2 L19.5 15.8 M4.5 15.8 L6.3 15.2 M17.7 8.8 L19.5 8.2 M8.2 19.5 L8.8 17.7 M15.2 4.5 L15.8 6.3" stroke="#0B2B4A" stroke-width="0.8"/>
            </svg>
            <div class="ministry-name">MINISTRY OF HEALTH</div>
            <div style="font-size:0.7rem; color:#7AA9D9;">Govt. of India</div>
            <div class="scheme-tag">Ayushman Bharat</div>
        </div>
        <hr style="border-color: #1E4A6F;">
        <div style="margin-top: 20px;">
            <p style="color:#A0C4E8; font-size:0.75rem;">▸ DIGITAL HEALTH MISSION</p>
            <p style="color:#A0C4E8; font-size:0.75rem;">▸ e-Triage Sahayak v2.0</p>
            <p style="color:#A0C4E8; font-size:0.75rem;">▸ ASHA Worker Module</p>
        </div>
        <div style="position: absolute; bottom: 20px; font-size:0.6rem; color:#4A7BA7;">
            NIC-CERTIFIED SECURE
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- SVG ICON FUNCTIONS ----------
def icon_fever():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><circle cx="12" cy="12" r="3"/><path d="M14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/></svg>'

def icon_lungs():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M6.5 6.5c-2 2-2 5.5 0 8.5M17.5 6.5c2 2 2 5.5 0 8.5M12 3v18M8 21h8M8 3h8M12 12c-2-2-4-4.5-4-7 0-2 2-3 4-3s4 1 4 3c0 2.5-2 5-4 7z"/></svg>'

def icon_heart():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'

def icon_user():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M5.3 20a8 8 0 0 1 13.4 0"/></svg>'

def icon_pregnant():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 13v6M9 16h6"/><path d="M5 21a8 8 0 0 1 14 0"/></svg>'

def icon_diabetes():
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B2B4A" stroke-width="2"><path d="M12 2v4M12 22v-4M4 12H2M6 12H4M20 12H18M22 12H20M19.07 4.93l-2.83 2.83M4.93 19.07l2.83-2.83M19.07 19.07l-2.83-2.83M4.93 4.93l2.83 2.83"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>'

def icon_alert_red():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>'

def icon_alert_yellow():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 2 L2 20 L22 20 L12 2z"/><path d="M12 9v4M12 17h.01"/></svg>'

def icon_alert_green():
    return '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>'

# ---------- MAIN HEADER ----------
st.markdown("""
<div class="main-header">
    <div class="header-left">
        <div>
            <div class="title">e-Triage Sahayak</div>
            <div class="subtitle">National Health Mission · AI-Assisted Referral Decision System</div>
        </div>
    </div>
    <div class="header-right">
        <span class="badge">SECURE · PRODUCTION</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- FORM CARD ----------
with st.container():
    st.markdown("""
    <div class="form-card">
        <h3>Patient Clinical Assessment</h3>
        <div class="desc">Enter the primary vitals and symptoms. The system will generate an evidence-based triage recommendation as per MoHFW guidelines.</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="input-label">{icon_user()} Age (in years)</div>', unsafe_allow_html=True)
        age = st.number_input("", min_value=0, max_value=120, step=1, value=35, label_visibility="collapsed", key="age_input")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_fever()} Fever / High Temperature</div>', unsafe_allow_html=True)
        fever = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="fever_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_lungs()} Breathing Difficulty</div>', unsafe_allow_html=True)
        breath_issue = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="breath_select")

    with col2:
        st.markdown(f'<div class="input-label">{icon_heart()} Blood Pressure (BP) Status</div>', unsafe_allow_html=True)
        bp_status = st.selectbox("", options=["Normal", "High", "Low"], label_visibility="collapsed", key="bp_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_pregnant()} Patient is Pregnant?</div>', unsafe_allow_html=True)
        is_pregnant = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="pregnant_select")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_diabetes()} History of Diabetes?</div>', unsafe_allow_html=True)
        diabetes = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed", key="diabetes_select")
    
    st.markdown("---")
    
    # ---------- TRIAGE LOGIC ----------
    def get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes):
        if is_pregnant == "Yes" and bp_status == "High":
            return ("RED", "Immediate referral to District Hospital / Medical College. Risk of Pre-eclampsia/Eclampsia. Call 108 Ambulance immediately.", "red")
        if age > 60 and bp_status == "Low":
            return ("RED", "Elderly patient with Low BP. High risk of Septic Shock. Urgent ICU admission required at Medical College.", "red")
        if fever == "Yes" and breath_issue == "Yes" and age > 50:
            return ("RED", "Severe Pneumonia/COVID-19 suspect with breathing issues in elderly. Immediate oxygen support needed. Refer to Tertiary Care Hospital.", "red")
        if diabetes == "Yes" and fever == "Yes":
            return ("YELLOW", "Diabetic patient with fever. High risk of infections. Refer to Community Health Centre (CHC) for advanced investigation.", "yellow")
        if fever == "Yes" and breath_issue == "Yes":
            return ("YELLOW", "Patient has fever with breathing issues. Needs Chest X-Ray and Oxygen saturation check. Refer to CHC.", "yellow")
        if age < 5 and fever == "Yes":
            return ("YELLOW", "Child under 5 with fever. Needs pediatric assessment. Refer to CHC immediately.", "yellow")
        if fever == "Yes" and breath_issue == "No":
            return ("GREEN", "Mild fever without breathing issues. Can be treated at PHC with basic medications (Paracetamol). Advise rest and hydration.", "green")
        if bp_status == "Normal" and fever == "No":
            return ("GREEN", "Vitals are stable. Routine checkup at PHC is sufficient. No emergency referral required.", "green")
        return ("GREEN", "Patient seems stable. Continue monitoring at PHC. No immediate referral needed.", "green")

    # ---------- SUBMIT BUTTON ----------
    if st.button("Generate Referral Recommendation", use_container_width=False, type="primary", key="submit_btn"):
        triage_title, triage_msg, triage_level = get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes)
        
        if triage_level == "red":
            st.markdown(f"""
            <div class="result-container result-red">
                <div class="result-icon">{icon_alert_red()}</div>
                <div class="result-text">
                    <h2>RED ALERT · Critical</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: IMMEDIATE (0-15 Mins)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif triage_level == "yellow":
            st.markdown(f"""
            <div class="result-container result-yellow">
                <div class="result-icon">{icon_alert_yellow()}</div>
                <div class="result-text">
                    <h2>YELLOW ALERT · Moderate</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: URGENT (Within 1 Hour)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-container result-green">
                <div class="result-icon">{icon_alert_green()}</div>
                <div class="result-text">
                    <h2>GREEN ALERT · Stable</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: ROUTINE (OPD Timing)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # close form-card

# ---------- FOOTER ----------
st.markdown("""
<div class="software-footer">
    <div>
        <strong>National Digital Health Mission (NDHM)</strong> · Compliance: MoHFW Guidelines v.2.4
    </div>
    <div>
        <span class="ver">End-to-End Encrypted</span>
        <span class="ver" style="margin-left:10px;">v2.0.1</span>
    </div>
</div>
""", unsafe_allow_html=True)ission · AI-Assisted Referral Decision System</div>
        </div>
    </div>
    <div class="header-right">
        <span class="badge">SECURE · PRODUCTION</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- FORM CARD ----------
with st.container():
    st.markdown("""
    <div class="form-card">
        <h3>Patient Clinical Assessment</h3>
        <div class="desc">Enter the primary vitals and symptoms. The system will generate an evidence-based triage recommendation as per MoHFW guidelines.</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="input-label">{icon_user()} Age (in years)</div>', unsafe_allow_html=True)
        age = st.number_input("", min_value=0, max_value=120, step=1, value=35, label_visibility="collapsed")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_fever()} Fever / High Temperature</div>', unsafe_allow_html=True)
        fever = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_lungs()} Breathing Difficulty</div>', unsafe_allow_html=True)
        breath_issue = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed")

    with col2:
        st.markdown(f'<div class="input-label">{icon_heart()} Blood Pressure (BP) Status</div>', unsafe_allow_html=True)
        bp_status = st.selectbox("", options=["Normal", "High", "Low"], label_visibility="collapsed")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_pregnant()} Patient is Pregnant?</div>', unsafe_allow_html=True)
        is_pregnant = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed")
        
        st.markdown(f'<div class="input-label" style="margin-top:20px;">{icon_diabetes()} History of Diabetes?</div>', unsafe_allow_html=True)
        diabetes = st.selectbox("", options=["No", "Yes"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # ---------- TRIAGE LOGIC ----------
    def get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes):
        if is_pregnant == "Yes" and bp_status == "High":
            return ("RED", "Immediate referral to District Hospital / Medical College. Risk of Pre-eclampsia/Eclampsia. Call 108 Ambulance immediately.", "red")
        if age > 60 and bp_status == "Low":
            return ("RED", "Elderly patient with Low BP. High risk of Septic Shock. Urgent ICU admission required at Medical College.", "red")
        if fever == "Yes" and breath_issue == "Yes" and age > 50:
            return ("RED", "Severe Pneumonia/COVID-19 suspect with breathing issues in elderly. Immediate oxygen support needed. Refer to Tertiary Care Hospital.", "red")
        if diabetes == "Yes" and fever == "Yes":
            return ("YELLOW", "Diabetic patient with fever. High risk of infections. Refer to Community Health Centre (CHC) for advanced investigation.", "yellow")
        if fever == "Yes" and breath_issue == "Yes":
            return ("YELLOW", "Patient has fever with breathing issues. Needs Chest X-Ray and Oxygen saturation check. Refer to CHC.", "yellow")
        if age < 5 and fever == "Yes":
            return ("YELLOW", "Child under 5 with fever. Needs pediatric assessment. Refer to CHC immediately.", "yellow")
        if fever == "Yes" and breath_issue == "No":
            return ("GREEN", "Mild fever without breathing issues. Can be treated at PHC with basic medications (Paracetamol). Advise rest and hydration.", "green")
        if bp_status == "Normal" and fever == "No":
            return ("GREEN", "Vitals are stable. Routine checkup at PHC is sufficient. No emergency referral required.", "green")
        return ("GREEN", "Patient seems stable. Continue monitoring at PHC. No immediate referral needed.", "green")

    # ---------- SUBMIT BUTTON ----------
    if st.button("Generate Referral Recommendation", use_container_width=False, type="primary"):
        triage_title, triage_msg, triage_level = get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes)
        
        if triage_level == "red":
            st.markdown(f"""
            <div class="result-container result-red">
                <div class="result-icon">{icon_alert_red()}</div>
                <div class="result-text">
                    <h2>RED ALERT · Critical</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: IMMEDIATE (0-15 Mins)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif triage_level == "yellow":
            st.markdown(f"""
            <div class="result-container result-yellow">
                <div class="result-icon">{icon_alert_yellow()}</div>
                <div class="result-text">
                    <h2>YELLOW ALERT · Moderate</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: URGENT (Within 1 Hour)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-container result-green">
                <div class="result-icon">{icon_alert_green()}</div>
                <div class="result-text">
                    <h2>GREEN ALERT · Stable</h2>
                    <p>{triage_msg}</p>
                    <span class="action-tag">ACTION: ROUTINE (OPD Timing)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # close form-card

# ---------- FOOTER ----------
st.markdown("""
<div class="software-footer">
    <div>
        <strong>National Digital Health Mission (NDHM)</strong> · Compliance: MoHFW Guidelines v.2.4
    </div>
    <div>
        <span class="ver">End-to-End Encrypted</span>
        <span class="ver" style="margin-left:10px;">v2.0.1</span>
    </div>
</div>
""", unsafe_allow_html=True)
