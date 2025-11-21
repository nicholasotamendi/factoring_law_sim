import streamlit as st
import time
import random
import csv
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Fiducia Data Protection Simulator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Light Mode + Poppins) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background-color: #f4f7f6;
        color: #333333;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Cards/Containers */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 20px;
        border: 1px solid #eaeaea;
    }
    
    /* Success/Error */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'completed_missions' not in st.session_state:
    st.session_state.completed_missions = set()
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Data Connoisuer"
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# --- Constants ---
TOTAL_MISSIONS = 5
MAX_SCORE_PER_MISSION = 100
PAGES = [
    "🏠 Dashboard",
    "📧 Mission 1: Phishing Defense",
    "⚖️ Mission 2: Data Rights (NDPR)",
    "🔑 Mission 3: Password Hygiene",
    "🏢 Mission 4: Physical Security",
    "🚨 Mission 5: Incident Response",
    "🏆 Certification"
]

# Map page index to mission ID for validation
MISSION_MAP = {
    1: "m1",
    2: "m2",
    3: "m3",
    4: "m4",
    5: "m5"
}

# --- Helper Functions ---
def mark_complete(mission_id, points):
    if mission_id not in st.session_state.completed_missions:
        st.session_state.score += points
        st.session_state.completed_missions.add(mission_id)
        st.balloons()
        st.success("✅ Correct! Moving to next mission...")
        time.sleep(1.5)
        # Auto-advance
        if st.session_state.page_index < len(PAGES) - 1:
            st.session_state.page_index += 1
        st.rerun()

def show_feedback(is_correct, explanation, mission_id, points=MAX_SCORE_PER_MISSION):
    if is_correct:
        # Auto-claim logic
        mark_complete(mission_id, points)
    else:
        st.error(f"❌ Incorrect. {explanation}")

def save_result(username, score):
    file_exists = os.path.isfile('training_log.csv')
    with open('training_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Username', 'Score', 'Completed'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, score, len(st.session_state.completed_missions) == TOTAL_MISSIONS])

def nav_buttons():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    
    # Previous Button
    with col1:
        if st.session_state.page_index > 0:
            if st.button("⬅️ Previous"):
                st.session_state.page_index -= 1
                st.rerun()
    
    # Next Button (with Validation)
    with col3:
        if st.session_state.page_index < len(PAGES) - 1:
            # Check if current page is a mission and if it is completed
            current_mission_id = MISSION_MAP.get(st.session_state.page_index)
            is_completed = True
            if current_mission_id:
                if current_mission_id not in st.session_state.completed_missions:
                    is_completed = False
            
            if st.button("Next ➡️"):
                if is_completed:
                    st.session_state.page_index += 1
                    st.rerun()
                else:
                    st.error("Please complete the mission first!")

# --- Sidebar & Navigation Logic ---
def update_index_from_radio():
    st.session_state.page_index = PAGES.index(st.session_state.nav_selection)

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
    
    # Navigation Radio
    st.radio(
        "Select Mission:",
        PAGES,
        index=st.session_state.page_index,
        key="nav_selection",
        on_change=update_index_from_radio
    )
    
    st.markdown("---")
    if st.button("Reset Simulator"):
        st.session_state.score = 0
        st.session_state.completed_missions = set()
        st.session_state.page_index = 0
        st.rerun()

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

    st.info("👈 Select a mission from the sidebar or click Next to start.")

def mission_phishing():
    st.header("📧 Mission 1: Phishing Defense")
    st.markdown("You are checking your emails on a busy Monday morning. One email catches your eye.")
    
    with st.container():
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
    
    # Use session state to persist choice if needed, but for now standard radio is fine
    choice = st.radio("Choose wisely:", 
                      ["Click the link to verify quickly.", 
                       "Reply to ask if it's real.", 
                       "Report to Security Team / Delete.",
                       "Forward to your personal email to check later."])
    
    if "m1" in st.session_state.completed_missions:
        st.success("✅ Mission Completed")
    else:
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
    
    if "m2" in st.session_state.completed_missions:
        st.success("✅ Mission Completed")
    else:
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

    if "m3" in st.session_state.completed_missions:
        st.success("✅ Mission Completed")
    else:
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
    
    if "m4" in st.session_state.completed_missions:
        st.success("✅ Mission Completed")
    else:
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
    
    if "m5" in st.session_state.completed_missions:
        st.success("✅ Mission Completed")
    else:
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
        
        # Save Result
        save_result(st.session_state.user_name, st.session_state.score)
        st.info("✅ Your result has been logged.")
        
        # Certificate Mockup
        st.markdown("---")
        st.markdown(f"""
        <div style="padding: 20px; border: 10px solid #FFD700; text-align: center; background-color: #ffffff; color: #333; font-family: 'Poppins', sans-serif;">
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
# Get current page from state
current_page_name = PAGES[st.session_state.page_index]

if current_page_name == "🏠 Dashboard":
    dashboard()
elif current_page_name == "📧 Mission 1: Phishing Defense":
    mission_phishing()
elif current_page_name == "⚖️ Mission 2: Data Rights (GDPR)":
    mission_data_rights()
elif current_page_name == "🔑 Mission 3: Password Hygiene":
    mission_passwords()
elif current_page_name == "🏢 Mission 4: Physical Security":
    mission_physical()
elif current_page_name == "🚨 Mission 5: Incident Response":
    mission_incident()
elif current_page_name == "🏆 Certification":
    certification()

# Render Navigation Buttons
nav_buttons()
