import streamlit as st
import time
import random

# Page Configuration
st.set_page_config(
    page_title="Fiducia Data Protection Simulator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Theme */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] h1 {
        color: #58a6ff;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #58a6ff, #8b949e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(35, 134, 54, 0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Cards/Containers */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #0d1117;
        color: white;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    
    /* Radio Buttons */
    .stRadio > label {
        color: #c9d1d9 !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(35, 134, 54, 0.1);
        border: 1px solid #238636;
        color: #3fb950;
    }
    .stError {
        background-color: rgba(218, 54, 51, 0.1);
        border: 1px solid #da3633;
        color: #f85149;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #58a6ff;
    }

</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'completed_missions' not in st.session_state:
    st.session_state.completed_missions = set()
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Trainee"

# --- Constants ---
TOTAL_MISSIONS = 5
MAX_SCORE_PER_MISSION = 100

# --- Sidebar & Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=80)
    st.title("🛡️ Fiducia Security")
    
    st.write(f"**Agent:** {st.session_state.user_name}")
    
    # Progress
    progress = len(st.session_state.completed_missions) / TOTAL_MISSIONS
    st.progress(progress)
    st.write(f"**Progress:** {int(progress * 100)}%")
    st.write(f"**Current Score:** {st.session_state.score}")
    
    st.markdown("---")
    
    mission_selection = st.radio(
        "Select Mission:",
        [
            "🏠 Dashboard",
            "📧 Mission 1: Phishing Defense",
            "⚖️ Mission 2: Data Rights (GDPR)",
            "🔑 Mission 3: Password Hygiene",
            "🏢 Mission 4: Physical Security",
            "🚨 Mission 5: Incident Response",
            "🏆 Certification"
        ]
    )
    
    st.markdown("---")
    if st.button("Reset Simulator"):
        st.session_state.score = 0
        st.session_state.completed_missions = set()
        st.rerun()

# --- Helper Functions ---
def mark_complete(mission_id, points):
    if mission_id not in st.session_state.completed_missions:
        st.session_state.score += points
        st.session_state.completed_missions.add(mission_id)
        st.balloons()
        time.sleep(1)
        st.rerun()

def show_feedback(is_correct, explanation, mission_id, points=MAX_SCORE_PER_MISSION):
    if is_correct:
        st.success(f"✅ Correct! {explanation}")
        if mission_id not in st.session_state.completed_missions:
            st.button("Claim Points & Finish Mission", on_click=mark_complete, args=(mission_id, points))
        else:
            st.info("Mission already completed.")
    else:
        st.error(f"❌ Incorrect. {explanation}")

# --- Missions ---

def dashboard():
    st.title("🛡️ Fiducia Data Protection Training Hub")
    st.markdown("""
    Welcome to the **Fiducia Data Protection Simulator**. Your goal is to navigate through real-world scenarios 
    and make the right decisions to protect our company's data.
    
    ### 🎯 Your Objectives
    1. Complete all **5 Missions**.
    2. Achieve a high score to earn your **Certificate**.
    3. Learn how to spot threats and handle data responsibly.
    
    Enter your name below to begin:
    """)
    
    name_input = st.text_input("Enter your name", value=st.session_state.user_name)
    if name_input != st.session_state.user_name:
        st.session_state.user_name = name_input
        st.rerun()

    st.info("👈 Select a mission from the sidebar to start.")

def mission_phishing():
    st.header("📧 Mission 1: Phishing Defense")
    st.markdown("You are checking your emails on a busy Monday morning. One email catches your eye.")
    
    with st.container(border=True):
        st.markdown("""
        **From:** IT Support <admin@fiducla.com>  
        **Subject:** URGENT: Verify your account now
        
        Dear User,
        
        We noticed unusual activity on your account. Please click the link below to verify your password immediately or your account will be locked.
        
        [Verify Now](http://fiducla-secure-login.com)
        
        Regards,  
        IT Team
        """)
    
    st.subheader("What is your immediate action?")
    choice = st.radio("Choose wisely:", 
                      ["Click the link to verify quickly.", 
                       "Reply to ask if it's real.", 
                       "Report to Security Team / Delete.",
                       "Forward to your personal email to check later."])
    
    if st.button("Submit Decision"):
        if choice == "Report to Security Team / Delete.":
            show_feedback(True, "You noticed the spoofed domain 'fiducla.com' and the urgency tactics. Excellent work.", "m1")
        elif choice == "Click the link to verify quickly.":
            show_feedback(False, "You fell for the trap! The domain was 'fiducla.com' (typo) and the link was suspicious.", "m1")
        else:
            show_feedback(False, "Not the best course of action. Always report suspicious emails directly via the 'Report Phish' button.", "m1")

def mission_data_rights():
    st.header("⚖️ Mission 2: Data Rights (GDPR)")
    st.markdown("A customer, **John Doe**, submits a **Subject Access Request (SAR)** asking for his data to be deleted.")
    
    st.info("Request: 'I want you to delete everything you have on me!'")
    
    st.subheader("Select which data records you will delete:")
    
    options = ["Marketing Email Subscription", "Customer Support Chat Logs", "Transaction History (Tax Invoices)", "Shipping Address"]
    selections = st.multiselect("Select items to delete:", options)
    
    if st.button("Process Deletion"):
        if not selections:
            st.warning("You must select something.")
        elif "Transaction History (Tax Invoices)" in selections:
            show_feedback(False, "⚠️ Compliance Violation! We are legally required to keep Tax Invoices for 6+ years. You cannot delete them just because a customer asks.", "m2")
        elif "Marketing Email Subscription" in selections and "Shipping Address" in selections and "Customer Support Chat Logs" in selections:
             show_feedback(True, "Perfect balance. You deleted the personal data we don't need, but kept the legal records (which we would explain to the customer).", "m2")
        else:
             show_feedback(False, "You missed some deletable data or didn't select enough. Try to clear all non-essential data.", "m2")

def mission_passwords():
    st.header("🔑 Mission 3: Password Hygiene")
    st.markdown("It's time to update your password. The policy requires: 12+ chars, mixed case, numbers, and symbols.")
    
    password = st.text_input("Create a new password:", type="password")
    
    strength = 0
    feedback = []
    
    if len(password) >= 12:
        strength += 1
    else:
        feedback.append("Too short (< 12 chars)")
        
    if any(c.isupper() for c in password) and any(c.islower() for c in password):
        strength += 1
    else:
        feedback.append("Needs mixed case")
        
    if any(c.isdigit() for c in password):
        strength += 1
    else:
        feedback.append("Needs a number")
        
    if any(not c.isalnum() for c in password):
        strength += 1
    else:
        feedback.append("Needs a special character (!@#$)")

    if st.button("Set Password"):
        if strength == 4:
            show_feedback(True, "Strong password set! It's long and complex.", "m3")
        else:
            st.error(f"Weak Password: {', '.join(feedback)}")

def mission_physical():
    st.header("🏢 Mission 4: Physical Security")
    st.markdown("You are leaving for lunch. Look at your desk setup below.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Desk State:**
        - 💻 Computer: Unlocked, showing customer data.
        - 📄 Papers: 'Confidential Client List' on desk.
        - 🔑 Keys: Office keys in the drawer.
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/96/000000/workstation.png", width=100)

    action = st.selectbox("What do you do before leaving?", 
                          ["Just go, I'll be back in 10 mins.", 
                           "Lock computer (Win+L).", 
                           "Lock computer AND put confidential papers in a locked drawer.",
                           "Turn off the monitor."])
    
    if st.button("Go to Lunch"):
        if action == "Lock computer AND put confidential papers in a locked drawer.":
            show_feedback(True, "Excellent 'Clean Desk' policy adherence! You secured both digital and physical assets.", "m4")
        elif action == "Lock computer (Win+L).":
            show_feedback(False, "Good start, but you left confidential papers exposed on the desk!", "m4")
        else:
            show_feedback(False, "Major security risk! Never leave your workstation unlocked or sensitive papers out.", "m4")

def mission_incident():
    st.header("🚨 Mission 5: Incident Response")
    st.markdown("You accidentally sent a file containing 500 customer credit card numbers to the wrong email address (external).")
    
    st.error("😱 Oh no! What do you do?")
    
    action = st.radio("Immediate Action:", 
                      ["Panic and delete the email from your sent items.", 
                       "Email the recipient and ask them to delete it politely.", 
                       "Immediately report it to the Data Protection Officer (DPO) / IT Security.",
                       "Ignore it, maybe no one will notice."])
    
    if st.button("Execute Protocol"):
        if action == "Immediately report it to the Data Protection Officer (DPO) / IT Security.":
            show_feedback(True, "Correct. Speed is key. The DPO needs to assess if this is a reportable breach to the ICO.", "m5")
        else:
            show_feedback(False, "Wrong. Hiding it or asking the recipient (who you don't know) is risky. Always report internally immediately.", "m5")

def certification():
    st.title("🏆 Course Completion")
    
    if len(st.session_state.completed_missions) == TOTAL_MISSIONS:
        st.balloons()
        st.success(f"CONGRATULATIONS, {st.session_state.user_name}!")
        st.markdown(f"""
        You have successfully completed the **Fiducia Data Protection Training**.
        
        **Final Score:** {st.session_state.score} / {TOTAL_MISSIONS * MAX_SCORE_PER_MISSION}
        
        You are now a certified Data Guardian! 🛡️
        """)
        
        # Certificate Mockup
        st.markdown("---")
        st.markdown(f"""
        <div style="padding: 20px; border: 10px solid #FFD700; text-align: center; background-color: #f9f9f9; color: #333;">
            <h1>Certificate of Completion</h1>
            <p>This certifies that</p>
            <h2>{st.session_state.user_name}</h2>
            <p>has demonstrated excellence in Data Protection & Security Awareness.</p>
            <p>Date: {time.strftime("%d %B %Y")}</p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning(f"You have completed {len(st.session_state.completed_missions)} / {TOTAL_MISSIONS} missions.")
        st.write("Please complete all missions to unlock your certificate.")

# --- Main Routing ---
if mission_selection == "🏠 Dashboard":
    dashboard()
elif mission_selection == "📧 Mission 1: Phishing Defense":
    mission_phishing()
elif mission_selection == "⚖️ Mission 2: Data Rights (GDPR)":
    mission_data_rights()
elif mission_selection == "🔑 Mission 3: Password Hygiene":
    mission_passwords()
elif mission_selection == "🏢 Mission 4: Physical Security":
    mission_physical()
elif mission_selection == "🚨 Mission 5: Incident Response":
    mission_incident()
elif mission_selection == "🏆 Certification":
    certification()
