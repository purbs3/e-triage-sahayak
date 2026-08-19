import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="e-Triage Sahayak - Govt of India",
    page_icon="🏥",
    layout="centered"
)

# ---------- CUSTOM CSS FOR GOVERNMENT THEME ----------
st.markdown("""
<style>
    /* Main background and fonts */
    .main {
        background-color: #f8f9fa;
    }
    /* Tricolor Header Strip */
    .tricolor {
        background: linear-gradient(to right, #FF9933 0%, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%, #138808 100%);
        height: 8px;
        border-radius: 0px;
        margin-bottom: 0px;
    }
    /* Blue Government Header */
    .gov-header {
        background-color: #003366;
        padding: 1.2rem;
        border-radius: 0px 0px 10px 10px;
        text-align: center;
        color: white;
        margin-top: -5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .gov-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .gov-header h3 {
        color: #FFD700;
        margin: 0;
        font-weight: 300;
        font-size: 1.1rem;
    }
    .gov-header p {
        color: #e0e0e0;
        margin: 5px 0 0 0;
        font-size: 0.9rem;
    }
    /* Card UI for inputs */
    .card {
        background: white;
        padding: 2rem 2.5rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.15);
        border-top: 5px solid #0072B6;
        margin-top: 1.5rem;
    }
    .result-box-red {
        background-color: #fce4e4;
        border-left: 6px solid #d32f2f;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1.5rem;
    }
    .result-box-yellow {
        background-color: #fff8e1;
        border-left: 6px solid #f57c00;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1.5rem;
    }
    .result-box-green {
        background-color: #e8f5e9;
        border-left: 6px solid #388e3c;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1.5rem;
    }
    .disclaimer {
        background: #eef2f6;
        padding: 12px;
        border-radius: 8px;
        margin-top: 30px;
        text-align: center;
        font-size: 0.8rem;
        color: #555;
        border: 1px solid #ccc;
    }
    /* Buttons */
    .stButton>button {
        background-color: #0072B6;
        color: white;
        font-weight: bold;
        border-radius: 30px;
        padding: 0.5rem 2.5rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #003366;
        color: white;
        transform: scale(1.02);
    }
    /* Footer */
    .footer {
        margin-top: 30px;
        font-size: 0.8rem;
        text-align: center;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ---------- UI HEADER (Government Look) ----------
st.markdown('<div class="tricolor"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="gov-header">
    <h3>🏛️ Ministry of Health & Family Welfare</h3>
    <h1>🇮🇳 e-Triage Sahayak</h1>
    <p>AI-Assisted Triage & Referral Decision Support System | <b>Ayushman Bharat</b> Digital Mission</p>
</div>
""", unsafe_allow_html=True)

# ---------- MAIN INPUT CARD ----------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🩺 Patient Assessment Form")
    st.markdown("*Enter the patient's vitals to get the instant referral recommendation.*")

    # Columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("👤 Age (in years)", min_value=0, max_value=120, step=1, value=35)
        fever = st.selectbox("🌡️ Fever / High Temperature", options=["No", "Yes"])
        breath_issue = st.selectbox("💨 Breathing Difficulty / Shortness of Breath", options=["No", "Yes"])

    with col2:
        bp_status = st.selectbox("❤️ Blood Pressure (BP) Status", options=["Normal", "High", "Low"])
        is_pregnant = st.selectbox("🤰 Is the patient pregnant?", options=["No", "Yes"])
        diabetes = st.selectbox("🍬 History of Diabetes?", options=["No", "Yes"])  # Extra point for logic

    # Spacer
    st.markdown("---")

    # ---------- TRIAGE LOGIC (PURE IF-ELSE) ----------
    def get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes):
        # CRITICAL RED CASES (Immediate District Hospital / Medical College)
        if is_pregnant == "Yes" and bp_status == "High":
            return ("🔴 RED ALERT", "Immediate referral to District Hospital / Medical College. Risk of Pre-eclampsia/Eclampsia. Call 108 Ambulance immediately.", "red")
        
        if age > 60 and bp_status == "Low":
            return ("🔴 RED ALERT", "Elderly patient with Low BP. High risk of Septic Shock or Cardiac event. Urgent ICU admission required at Medical College.", "red")
        
        if fever == "Yes" and breath_issue == "Yes" and age > 50:
            return ("🔴 RED ALERT", "Severe Pneumonia/COVID-19 suspect with breathing issues in elderly. Immediate oxygen support needed. Refer to Tertiary Care Hospital.", "red")
        
        if diabetes == "Yes" and fever == "Yes":
            return ("🟡 YELLOW ALERT", "Diabetic patient with fever. High risk of infections. Refer to Community Health Centre (CHC) for advanced investigation.", "yellow")

        # YELLOW CASES (CHC - Community Health Centre)
        if fever == "Yes" and breath_issue == "Yes":
            return ("🟡 YELLOW ALERT", "Patient has fever with breathing issues. Needs Chest X-Ray and Oxygen saturation check. Refer to CHC.", "yellow")
        
        if age < 5 and fever == "Yes":
            return ("🟡 YELLOW ALERT", "Child under 5 with fever. Needs pediatric assessment. Refer to CHC immediately.", "yellow")

        # GREEN CASES (PHC - Primary Health Centre)
        if fever == "Yes" and breath_issue == "No":
            return ("🟢 GREEN ALERT", "Mild fever without breathing issues. Can be treated at PHC with basic medications (Paracetamol). Advise rest and hydration.", "green")
        
        if bp_status == "Normal" and fever == "No":
            return ("🟢 GREEN ALERT", "Vitals are stable. Routine checkup at PHC is sufficient. No emergency referral required.", "green")

        # Default safe case
        return ("🟢 GREEN ALERT", "Patient seems stable. Continue monitoring at PHC. No immediate referral needed.", "green")

    # ---------- SUBMIT BUTTON ----------
    if st.button("🚑 Get Referral Recommendation", use_container_width=False):
        triage_title, triage_msg, triage_level = get_triage_decision(age, fever, breath_issue, bp_status, is_pregnant, diabetes)
        
        # Display the result with dynamic coloring
        if triage_level == "red":
            st.markdown(f"""
            <div class="result-box-red">
                <h2 style="margin:0; color:#b71c1c;">{triage_title}</h2>
                <p style="font-size:1.1rem; margin-top:10px;">{triage_msg}</p>
                <p style="margin-top:10px; background:#d32f2f; color:white; padding:5px 10px; border-radius:20px; display:inline-block;">⏳ Action Required: <b>Immediate</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        elif triage_level == "yellow":
            st.markdown(f"""
            <div class="result-box-yellow">
                <h2 style="margin:0; color:#e65100;">{triage_title}</h2>
                <p style="font-size:1.1rem; margin-top:10px;">{triage_msg}</p>
                <p style="margin-top:10px; background:#f57c00; color:white; padding:5px 10px; border-radius:20px; display:inline-block;">⏳ Action Required: <b>Within 1 Hour</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="result-box-green">
                <h2 style="margin:0; color:#1b5e20;">{triage_title}</h2>
                <p style="font-size:1.1rem; margin-top:10px;">{triage_msg}</p>
                <p style="margin-top:10px; background:#388e3c; color:white; padding:5px 10px; border-radius:20px; display:inline-block;">⏳ Action Required: <b>Routine (OPD)</b></p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # End of card

# ---------- DISCLAIMER & FOOTER ----------
st.markdown("""
<div class="disclaimer">
    <b>⚠️ Important Legal Disclaimer:</b> This is an AI-Assisted Decision Support System. 
    The final clinical diagnosis and referral decision must always be made by a qualified medical practitioner (Doctor). 
    This tool is designed for ASHA Workers and Medical Officers for preliminary triage only.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <b>Developed under the Digital Health Mission | © Ministry of Health & Family Welfare, Govt. of India</b><br>
    Version 1.0 | Secure & Scalable Triage Framework
</div>
""", unsafe_allow_html=True)
