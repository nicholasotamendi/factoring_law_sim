import streamlit as st
import time
import random
import csv
import os
from datetime import datetime
from fpdf import FPDF
import base64
import pandas as pd

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
        color: #101745;
    }

    .stApp {
        background-color: #ffffff;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #101745; /* Fiducia Purple */
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1560bd; /* Fiducia Blue */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #104a9e;
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
    
    /* Certificate Style */
    .certificate-container {
        border: 10px double #101745;
        padding: 40px;
        background-color: #fff;
        text-align: center;
        border-radius: 10px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        margin: 30px auto;
        max-width: 800px;
        background-image: radial-gradient(circle, #ffffff 0%, #f0f2f5 100%);
        position: relative;
    }
    .certificate-container::before {
        content: "🏆";
        font-size: 100px;
        opacity: 0.1;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 0;
    }
    .cert-header {
        color: #101745;
        font-family: 'Georgia', serif;
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 4px;
        border-bottom: 2px solid #1560bd;
        display: inline-block;
        padding-bottom: 10px;
        position: relative;
        z-index: 1;
    }
    .cert-body {
        font-size: 22px;
        color: #555;
        margin: 15px 0;
        font-family: 'Poppins', sans-serif;
        position: relative;
        z-index: 1;
    }
    .cert-name {
        font-size: 50px;
        color: #1560bd;
        font-family: 'Georgia', serif;
        font-weight: bold;
        margin: 20px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    .cert-footer {
        font-size: 18px;
        color: #777;
        margin-top: 40px;
        border-top: 1px solid #ddd;
        padding-top: 20px;
        position: relative;
        z-index: 1;
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
    
    /* Dashboard Styling */
    .important-instruction {
        color: #d9534f; /* Red */
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    .input-container {
        border: 2px solid #1560bd; /* Fiducia Blue */
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'completed_missions' not in st.session_state:
    st.session_state.completed_missions = set()
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False
if 'confirm_reset_cert' not in st.session_state:
    st.session_state.confirm_reset_cert = False
if 'result_saved' not in st.session_state:
    st.session_state.result_saved = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Constants ---
TOTAL_MISSIONS = 10
MAX_SCORE_PER_MISSION = 100
PAGES = [
    "🏠 Dashboard",
    "📧 Mission 1: Supply Chain Phishing",
    "⚖️ Mission 2: Data Rights (NDPR)",
    "🔐 Mission 3: Access Control",
    "🏢 Mission 4: Physical Security",
    "🚨 Mission 5: Data Leakage",
    "💀 Mission 6: Ransomware Attack",
    "🎭 Mission 7: CEO Fraud (BEC)",
    "☁️ Mission 8: Shadow IT",
    "💻 Mission 9: Secure Development",
    "🕵️ Mission 10: Insider Threat",
    "🏆 Certification",
    "🏆 Leaderboard"
]

# Map page index to mission ID for validation
MISSION_MAP = {
    1: "m1",
    2: "m2",
    3: "m3",
    4: "m4",
    5: "m5",
    6: "m6",
    7: "m7",
    8: "m8",
    9: "m9",
    10: "m10"
}

# --- Helper Functions ---
def mark_complete(mission_id, points, message=None):
    if mission_id not in st.session_state.completed_missions:
        st.session_state.score += points
        st.session_state.completed_missions.add(mission_id)
        
        if points > 0:
            st.balloons()
            if message:
                st.success(message)
            else:
                st.success("✅ Correct! Moving to next mission...")
        else:
            if message:
                st.error(message)
            else:
                st.error("❌ Incorrect. Moving to next mission...")
            
        time.sleep(5) # Pause to read feedback
        
        # Auto-advance
        if st.session_state.page_index < len(PAGES) - 1:
            st.session_state.page_index += 1
        st.rerun()

def show_feedback(is_correct, explanation, mission_id, points=MAX_SCORE_PER_MISSION):
    if is_correct:
        msg = f"✅ Correct! {explanation}"
        mark_complete(mission_id, points, message=msg)
    else:
        msg = f"❌ Incorrect. {explanation}"
        mark_complete(mission_id, 0, message=msg)

def save_result(username, email, score, duration_seconds):
    file_exists = os.path.isfile('training_log.csv')
    
    # Check for schema migration if file exists
    if file_exists:
        try:
            df = pd.read_csv('training_log.csv')
            changed = False
            if 'DurationSeconds' not in df.columns:
                df['DurationSeconds'] = 999999 # Default for old records
                changed = True
            if 'Email' not in df.columns:
                df['Email'] = 'N/A'
                changed = True
            
            if changed:
                df.to_csv('training_log.csv', index=False)
        except Exception:
            pass # If empty or error, just overwrite/append normally

    new_data = pd.DataFrame([{
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Username': username,
        'Email': email,
        'Score': score,
        'Completed': len(st.session_state.completed_missions) == TOTAL_MISSIONS,
        'DurationSeconds': duration_seconds
    }])

    if not file_exists:
        new_data.to_csv('training_log.csv', index=False)
    else:
        new_data.to_csv('training_log.csv', mode='a', header=False, index=False)

def create_pdf(username, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=24)
    pdf.cell(200, 20, txt="Certificate of Completion", ln=1, align="C")
    
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="This certifies that", ln=1, align="C")
    
    pdf.set_font("Arial", "B", size=20)
    pdf.cell(200, 10, txt=username, ln=1, align="C")
    
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="has successfully completed the", ln=1, align="C")
    pdf.cell(200, 10, txt="Fiducia Data Protection Training", ln=1, align="C")
    
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Score: {score} / {TOTAL_MISSIONS * MAX_SCORE_PER_MISSION}", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%d %B %Y')}", ln=1, align="C")
    
    return pdf.output(dest="S").encode("latin-1")

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
    st.markdown("---")
    if not st.session_state.confirm_reset:
        if st.button("Reset Simulator"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.warning("⚠️ Are you sure? All progress will be lost.")
        col1, col2 = st.columns(2)
        if col1.button("Yes, Reset", key="sidebar_reset_yes"):
            st.session_state.score = 0
            st.session_state.completed_missions = set()
            st.session_state.page_index = 0
            st.session_state.confirm_reset = False
            st.rerun()
        if col2.button("Cancel", key="sidebar_reset_no"):
            st.session_state.confirm_reset = False
            st.rerun()

# --- Missions ---

def dashboard():
    st.title("🛡️ Fiducia Data Protection Training Hub")
    st.markdown(f"""
    Welcome to the **Fiducia Data Protection Simulator**. 
    
    As a key player in **IT Supply Chain Financing**, we handle sensitive data: invoices, vendor KYC, and Customer Information. 
    Your vigilance is our first line of defense.
    
    ### 🎯 Your Objectives
    1. Complete all **{TOTAL_MISSIONS} Missions**.
    2. **Warning:** Incorrect answers will result in **0 points** and you cannot retry.
    3. Achieve a score of at least **80%** to earn your **Data Protection Certificate**.
    
    
    Enter your details below to begin:
    """)
    
    st.markdown('<p class="important-instruction">⚠️ Please enter your Name and Official Email (@myfiducia.com) to start the simulator.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name_input = st.text_input("Full Name", value=st.session_state.user_name, placeholder="e.g. Jane Doe")
    with col2:
        email_input = st.text_input("Official Email", value=st.session_state.user_email, placeholder="e.g. jane.doe@myfiducia.com")
    
    if st.button("Start Training"):
        # Validation
        if not name_input.strip():
            st.error("❌ Please enter your name.")
        elif not email_input.strip():
            st.error("❌ Please enter your email.")
        elif not email_input.strip().endswith("@myfiducia.com"):
            st.error("❌ Invalid Email. You must use your official '@myfiducia.com' email address.")
        else:
            st.session_state.user_name = name_input.strip()
            st.session_state.user_email = email_input.strip()
            # Start Timer
            st.session_state.start_time = datetime.now()
            # Move to first mission
            st.session_state.page_index = 1
            st.rerun()

    st.info("👈 Select a mission from the sidebar or click Next to start.")

def mission_phishing():
    st.header("📧 Mission 1: Supply Chain Phishing")
    st.markdown("You receive an email from a known logistics partner regarding a 'Blocked Invoice Payment'.")
    
    with st.container():
        st.markdown("""
        **From:** Accounts Payable <operations@myfiduc1a.com>  
        **Subject:** URGENT: Invoice #99281 Blocked - Action Required
        
        Hi Team,
        
        Your payment for Invoice #99281 has been blocked due to a KYC update error. 
        Please download the attached 'Secure Payment Gateway' tool to update your banking credentials immediately, or the payment will be delayed.
        
        [Download Secure Tool](http://myfiduc1a.com/secure-tool.exe)
        
        Regards,  
        Operations Dept
        """)
    
    st.subheader("Analyze the email. What is the primary red flag?")
    
    choice = st.radio("Select the most critical indicator:", 
                      ["The tone is urgent.", 
                       "The sender domain 'myfiduc1a.com' is likely a spoof (lookalike domain).", 
                       "The invoice number is unfamiliar.",
                       "It asks for banking credentials."])
    
    if "m1" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Submit Analysis"):
            if choice == "The sender domain 'myfiduc1a.com' is likely a spoof (lookalike domain).":
                show_feedback(True, "Correct. Supply chain attacks often use 'typosquatting' or plausible-looking domains to trick you into installing malware.", "m1")
            else:
                show_feedback(False, "Incorrect. While other factors are suspicious, the **domain spoofing** is the technical smoking gun here. The official domain would be 'myfiducia.com'.", "m1")

def mission_data_rights():
    st.header("⚖️ Mission 2: Data Rights (NDPR)")
    st.markdown("A former director of a vendor company, **Aduke Okon Tambuwal**, submits a request to delete her personal data.")
    st.info("Context: Aduke Okon Tambuwal was the signatory for a financing deal 3 years ago. We hold her passport copy and signature for AML/KYC purposes.")
    
    st.subheader("How do you respond to her Deletion Request?")
    
    choice = st.radio("Decision:", 
                      ["Delete everything immediately to comply with NDPR.", 
                       "Delete her email address but keep the passport/signature.", 
                       "Refuse to delete the passport/signature due to AML/KYC legal obligations.",
                       "Ask her to pay a processing fee first."])
    
    if "m2" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Submit Decision"):
            if choice == "Refuse to delete the passport/signature due to AML/KYC legal obligations.":
                show_feedback(True, "Correct. Legal obligations (like Anti-Money Laundering laws) override the Right to Erasure under NDPR for specific transaction records.", "m2")
            elif choice == "Delete her email address but keep the passport/signature.":
                show_feedback(False, "Partially correct, but you must explicitly inform her *why* you are retaining the AML data. The best answer focuses on the refusal justification.", "m2")
            else:
                show_feedback(False, "Incorrect. Deleting AML records would violate financial regulations and expose Fiducia to massive fines.", "m2")

def mission_access_control():
    st.header("🔐 Mission 3: Access Control")
    st.markdown("A partner developer needs temporary access to our 'Live Transaction Database' to debug a critical API integration failure preventing payments.")
    
    st.subheader("What is the secure way to grant access?")
    
    choice = st.radio("Method:", 
                      ["Share the 'admin' database password via a self-destructing note.", 
                       "Create a temporary user with 'Read-Only' access to the specific table needed.", 
                       "Send them a sanitized dump of the database (no real PII).",
                       "Grant them access via a shared team account."])
    
    if "m3" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Grant Access"):
            if choice == "Send them a sanitized dump of the database (no real PII).":
                show_feedback(True, "Best Practice. Never give external parties direct access to live production data if possible. A sanitized dump allows debugging without risk.", "m3")
            elif choice == "Create a temporary user with 'Read-Only' access to the specific table needed.":
                show_feedback(False, "Risky. Even read-only access exposes live PII (NDPR violation). Sanitized data is safer.", "m3")
            else:
                show_feedback(False, "Critical Failure. Never share admin credentials or use shared accounts.", "m3")

def mission_physical():
    st.header("🏢 Mission 4: Physical Security")
    st.markdown("You are working late on a printed 'Credit Risk Assessment' for a high-profile client. You need to use the restroom.")
    
    st.subheader("What do you do with the document?")
    
    choice = st.radio("Action:", 
                      ["Turn it face down on the desk.", 
                       "Lock your office door.", 
                       "Put it in a locked drawer/cabinet.",
                       "Leave it, the office is empty anyway."])
    
    if "m4" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Secure Desk"):
            if choice == "Put it in a locked drawer/cabinet.":
                show_feedback(True, "Correct. The 'Clean Desk Policy' applies 24/7. Cleaning staff or security guards could still access the area.", "m4")
            else:
                show_feedback(False, "Insufficient. Locking the door isn't foolproof, and turning it over is useless. Secure it properly.", "m4")

def mission_data_leak():
    st.header("🚨 Mission 5: Data Leakage")
    st.markdown("You intended to email a 'Vendor Credit Limit' spreadsheet to 'finance@fiducia.com', but autocomplete sent it to 'ian@finance-vendorcredit.com'.")
    
    st.subheader("Immediate Response Protocol:")
    
    choice = st.radio("Action:", 
                      ["Recall the message in Outlook.", 
                       "Email Ian and ask him to delete it.", 
                       "Report to DPO/IT Security immediately.",
                       "Wait to see if it bounces back."])
    
    if "m5" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Execute Protocol"):
            if choice == "Report to DPO/IT Security immediately.":
                show_feedback(True, "Correct. Message recall rarely works externally. The DPO needs to assess the breach and potentially notify regulators.", "m5")
            else:
                show_feedback(False, "Incorrect. Relying on recall or the recipient's goodwill is dangerous. You must report the breach internally.", "m5")

def mission_ransomware():
    st.header("💀 Mission 6: Ransomware Attack")
    st.markdown("The 'Transaction Database' server is encrypted. A ransom note demands 10 BTC. Backups are 12 hours old (some data loss will occur).")
    
    st.subheader("Strategic Decision:")
    
    choice = st.radio("Decision:", 
                      ["Pay the ransom to ensure zero data loss.", 
                       "Isolate the network, wipe the server, and restore from backups.", 
                       "Try to decrypt it using online tools.",
                       "Contact the attacker to negotiate."])
    
    if "m6" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Make Decision"):
            if choice == "Isolate the network, wipe the server, and restore from backups.":
                show_feedback(True, "Correct. We accept the 12-hour data loss. Paying funds crime and there is no guarantee of decryption. We can reconstruct the 12 hours from other logs.", "m6")
            else:
                show_feedback(False, "Wrong. Paying is against policy. It marks us as a 'payer' for future attacks.", "m6")

def mission_ceo_fraud():
    st.header("🎭 Mission 7: CEO Fraud (BEC)")
    st.markdown("You receive a WhatsApp from the CEO: 'I'm at a conference. We need to change the settlement account for the 'Project Alpha' vendor immediately to this new account. Do it now.'")
    
    st.subheader("Action:")
    
    choice = st.radio("Response:", 
                      ["Process the change, it's the CEO.", 
                       "Call the CEO on their official number to verify.", 
                       "Reply on WhatsApp asking for a confirmation code.",
                       "Wait until they return."])
    
    if "m7" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Send Response"):
            if choice == "Call the CEO on their official number to verify.":
                show_feedback(True, "Correct. Out-of-band verification is mandatory for payment instruction changes. WhatsApp is easily impersonated.", "m7")
            else:
                show_feedback(False, "Incorrect. Never process financial changes based on unverified messages, regardless of the sender's apparent rank.", "m7")

def mission_shadow_it():
    st.header("☁️ Mission 8: Shadow IT")
    st.markdown("A marketing manager is using a free online tool, 'PDF-Merger-Online', to combine sensitive Invoice Agreements for easier storage.")
    
    st.subheader("Why is this a risk?")
    
    choice = st.radio("Analysis:", 
                      ["It's not a risk if the tool uses HTTPS.", 
                       "We don't have a contract with this vendor, and data is leaving our control.", 
                       "The tool might be slow.",
                       "It costs money."])
    
    if "m8" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Submit Analysis"):
            if choice == "We don't have a contract with this vendor, and data is leaving our control.":
                show_feedback(True, "Correct. This is 'Shadow IT'. We have no DPA (Data Processing Agreement) in place, and the free tool likely monetizes the data.", "m8")
            else:
                show_feedback(False, "Incorrect. HTTPS only protects data in transit. The risk is that the vendor now owns/stores our data without legal protection.", "m8")

def mission_secure_dev():
    st.header("💻 Mission 9: Secure Development")
    st.markdown("You are reviewing a script written by a junior dev to automate 'Daily Reconciliation'. You see this line:\n\n`aws_secret_key = 'AKIA...12345'`")
    
    st.subheader("What is the vulnerability?")
    
    choice = st.radio("Identify the flaw:", 
                      ["The variable name is too obvious.", 
                       "Hardcoded credentials in source code.", 
                       "Python is not secure for reconciliation.",
                       "The key is too short."])
    
    if "m9" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Report Vulnerability"):
            if choice == "Hardcoded credentials in source code.":
                show_feedback(True, "Correct. If this code is pushed to a repo (even private), the keys are compromised. Use Environment Variables or a Secrets Manager.", "m9")
            else:
                show_feedback(False, "Incorrect. The issue is **Hardcoded Credentials**. This is a top OWASP vulnerability.", "m9")

def mission_insider():
    st.header("🕵️ Mission 10: Insider Threat")
    st.markdown("You notice a colleague from Sales copying the entire 'Client Master Database' (including credit limits and tax IDs) to a personal USB drive.")
    st.markdown("*They say: 'I just need to work on this at home over the weekend.'*")
    
    st.subheader("Action:")
    
    choice = st.radio("Decision:", 
                      ["Let them, they are a trusted employee.", 
                       "Tell them to encrypt the USB drive first.", 
                       "Stop them and report to Security immediately.",
                       "Ask them to email it to themselves instead."])
    
    if "m10" in st.session_state.completed_missions:
        st.info("Mission Completed")
    else:
        if st.button("Intervene"):
            if choice == "Stop them and report to Security immediately.":
                show_feedback(True, "Correct. Data exfiltration (even with good intent) is a massive risk. Personal USBs are strictly prohibited.", "m10")
            else:
                show_feedback(False, "Incorrect. You must stop the exfiltration. 'Working from home' should be done via secure VPN/VDI, not by moving data.", "m10")

def certification():
    st.title("🏆 Course Completion")
    
    # Calculate scores
    max_possible_score = TOTAL_MISSIONS * MAX_SCORE_PER_MISSION
    passing_score = max_possible_score * 0.8
    is_passed = st.session_state.score >= passing_score
    
    # Check if all missions are done
    if len(st.session_state.completed_missions) == TOTAL_MISSIONS:
        
        if is_passed:
            # --- SUCCESS STATE ---
            st.balloons()
            
            # Calculate Duration
            duration_seconds = 0
            if st.session_state.start_time:
                duration_seconds = (datetime.now() - st.session_state.start_time).total_seconds()
            
            # Format duration for display
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            time_str = f"{minutes}m {seconds}s"

            # 1. Visual Certificate
            st.markdown(f"""
            <div class="certificate-container">
                <div class="cert-header">Certificate of Completion</div>
                <div class="cert-body">This certifies that</div>
                <div class="cert-name">{st.session_state.user_name}</div>
                <div class="cert-body">has successfully completed the</div>
                <div class="cert-body"><b>Fiducia Data Protection Training</b></div>
                <div class="cert-footer">
                    Date: {datetime.now().strftime('%d %B %Y')} <br>
                    Score: {st.session_state.score} / {max_possible_score} <br>
                    Time: {time_str}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.success(f"Congratulations! You have passed with a score of {st.session_state.score} / {max_possible_score} in {time_str}.")
            
            # 2. Save Result (if not already saved this session/run)
            if not st.session_state.result_saved:
                save_result(st.session_state.user_name, st.session_state.user_email, st.session_state.score, duration_seconds)
                st.session_state.result_saved = True
                # Optional: Show a toast or small message
                # st.toast("Result saved successfully!")
            
            # 3. PDF Download
            pdf_bytes = create_pdf(st.session_state.user_name, st.session_state.score)
            st.download_button(
                label="📄 Download Certificate (PDF)",
                data=pdf_bytes,
                file_name="Fiducia_Certificate.pdf",
                mime="application/pdf"
            )
            
        else:
            # --- FAILURE STATE ---
            st.error(f"Course Completed, but Score Insufficient.")
            st.markdown(f"""
            You have completed all missions, but your score of **{st.session_state.score} / {max_possible_score}** is below the 80% passing threshold ({int(passing_score)} points).
            
            Unfortunately, you cannot be awarded a certificate at this time.
            
            Please **Reset the Simulator** from the sidebar and try again to demonstrate your mastery of the material.
            """)
            
            # Save Result (Log attempt even if failed)
            # Calculate Duration for failed attempt too
            duration_seconds = 0
            if st.session_state.start_time:
                duration_seconds = (datetime.now() - st.session_state.start_time).total_seconds()
            
            save_result(st.session_state.user_name, st.session_state.user_email, st.session_state.score, duration_seconds)
            
            if not st.session_state.confirm_reset_cert:
                if st.button("🔄 Reset Simulator & Try Again"):
                    st.session_state.confirm_reset_cert = True
                    st.rerun()
            else:
                st.warning("⚠️ Are you sure you want to reset? All progress will be lost.")
                col1, col2 = st.columns(2)
                if col1.button("Yes, Reset", key="cert_reset_yes"):
                    st.session_state.score = 0
                    st.session_state.completed_missions = set()
                    st.session_state.page_index = 0
                    st.session_state.confirm_reset_cert = False
                    st.rerun()
                if col2.button("Cancel", key="cert_reset_no"):
                    st.session_state.confirm_reset_cert = False
                    st.rerun()

        # --- LEADERBOARD (Always Visible when done) ---
        st.markdown("---")
        st.subheader("🏆 Hall of Fame")
        if os.path.isfile('training_log.csv'):
            try:
                df = pd.read_csv('training_log.csv')
                if not df.empty:
                    # Ensure DurationSeconds exists (for backward compatibility if not saved yet)
                    if 'DurationSeconds' not in df.columns:
                        df['DurationSeconds'] = 999999
                    
                    # Ensure DurationSeconds is numeric
                    df['DurationSeconds'] = pd.to_numeric(df['DurationSeconds'], errors='coerce')
                    
                    # Sort by Score (desc) and DurationSeconds (asc)
                    df = df.sort_values(by=['Score', 'DurationSeconds'], ascending=[False, True])
                    
                    # Format Duration
                    def format_duration(seconds):
                        if pd.isna(seconds) or seconds == 999999:
                            return "N/A"
                        m = int(seconds // 60)
                        s = int(seconds % 60)
                        return f"{m}m {s}s"
                    
                    df['Time'] = df['DurationSeconds'].apply(format_duration)
                    
                    # Rename Username to Name for display
                    df = df.rename(columns={'Username': 'Name'})
                    
                    # Reset index
                    df.reset_index(drop=True, inplace=True)
                    df.index += 1
                    
                    st.dataframe(
                        df[['Name', 'Email', 'Time', 'Timestamp']], 
                        use_container_width=True,
                        height=300
                    )
            except Exception as e:
                st.error(f"Could not load leaderboard: {e}")

    else:
        st.warning(f"You have completed {len(st.session_state.completed_missions)} / {TOTAL_MISSIONS} missions.")
        st.write("Please complete all missions to unlock your certificate.")

def leaderboard():
    st.title("🏆 Hall of Fame")
    st.markdown("The top performing Data Guardians.")
    
    if os.path.isfile('training_log.csv'):
        try:
            df = pd.read_csv('training_log.csv')
            if not df.empty:
                # Ensure DurationSeconds exists
                if 'DurationSeconds' not in df.columns:
                    df['DurationSeconds'] = 999999
                
                # Ensure DurationSeconds is numeric
                df['DurationSeconds'] = pd.to_numeric(df['DurationSeconds'], errors='coerce')
                
                # Sort by Score (desc) and DurationSeconds (asc)
                df = df.sort_values(by=['Score', 'DurationSeconds'], ascending=[False, True])
                
                # Format Duration
                def format_duration(seconds):
                    if pd.isna(seconds) or seconds == 999999:
                        return "N/A"
                    m = int(seconds // 60)
                    s = int(seconds % 60)
                    return f"{m}m {s}s"
                
                df['Time'] = df['DurationSeconds'].apply(format_duration)
                
                # Rename Username to Name for display
                df = df.rename(columns={'Username': 'Name'})
                
                # Reset index to start at 1
                df.reset_index(drop=True, inplace=True)
                df.index += 1
                
                st.dataframe(
                    df[['Name', 'Email', 'Time', 'Timestamp']], 
                    use_container_width=True,
                    height=500
                )
            else:
                st.info("No records found yet. Be the first!")
        except Exception as e:
            st.error(f"Error loading leaderboard: {e}")
    else:
        st.info("No records found yet.")

# --- Main Routing ---
# Get current page from state
current_page_name = PAGES[st.session_state.page_index]

if current_page_name == "🏠 Dashboard":
    dashboard()
elif current_page_name == "📧 Mission 1: Supply Chain Phishing":
    mission_phishing()
elif current_page_name == "⚖️ Mission 2: Data Rights (NDPR)":
    mission_data_rights()
elif current_page_name == "🔐 Mission 3: Access Control":
    mission_access_control()
elif current_page_name == "🏢 Mission 4: Physical Security":
    mission_physical()
elif current_page_name == "🚨 Mission 5: Data Leakage":
    mission_data_leak()
elif current_page_name == "💀 Mission 6: Ransomware Attack":
    mission_ransomware()
elif current_page_name == "🎭 Mission 7: CEO Fraud (BEC)":
    mission_ceo_fraud()
elif current_page_name == "☁️ Mission 8: Shadow IT":
    mission_shadow_it()
elif current_page_name == "💻 Mission 9: Secure Development":
    mission_secure_dev()
elif current_page_name == "🕵️ Mission 10: Insider Threat":
    mission_insider()
elif current_page_name == "🏆 Certification":
    certification()
elif current_page_name == "🏆 Leaderboard":
    leaderboard()

# Render Navigation Buttons
nav_buttons()
