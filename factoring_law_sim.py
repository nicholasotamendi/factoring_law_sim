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
    page_title="Fiducia Factoring Law",
    page_icon="⚖️",
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
    "1️⃣ Question 1",
    "2️⃣ Question 2",
    "3️⃣ Question 3",
    "4️⃣ Question 4",
    "5️⃣ Question 5",
    "6️⃣ Question 6",
    "7️⃣ Question 7",
    "8️⃣ Question 8",
    "9️⃣ Question 9",
    "🔟 Question 10",
    "🏆 Certification",
    "🏆 Leaderboard"
]

# Map page index to mission ID for validation
MISSION_MAP = {
    1: "q1",
    2: "q2",
    3: "q3",
    4: "q4",
    5: "q5",
    6: "q6",
    7: "q7",
    8: "q8",
    9: "q9",
    10: "q10"
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
                st.success("✅ Correct! Moving to next question...")
        else:
            if message:
                st.error(message)
            else:
                st.error("❌ Incorrect. Moving to next question...")
            
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
    pdf.cell(200, 10, txt="Fiducia Factoring Law Training", ln=1, align="C")
    
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
                    st.error("Please complete the question first!")

# --- Sidebar & Navigation Logic ---
def update_index_from_radio():
    st.session_state.page_index = PAGES.index(st.session_state.nav_selection)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/law.png", width=80)
    st.title("⚖️ Fiducia Law")
    
    st.write(f"**Agent:** {st.session_state.user_name}")
    
    # Progress
    progress = len(st.session_state.completed_missions) / TOTAL_MISSIONS
    st.progress(progress)
    st.write(f"**Progress:** {int(progress * 100)}%")
    st.write(f"**Current Score:** {st.session_state.score}")
    
    st.markdown("---")
    
    # Navigation Radio
    st.radio(
        "Select Question:",
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
    st.title("⚖️ Fiducia Factoring Law Training Hub")
    st.markdown(f"""
    Welcome to the **Fiducia Factoring Law Simulator**. 
    
    Mastering the legal intricacies of factoring is crucial for our operations.
    Test your knowledge on financing types, risks, and legal definitions.
    
    ### 🎯 Your Objectives
    1. Complete all **{TOTAL_MISSIONS} Questions**.
    2. **Warning:** Incorrect answers will result in **0 points** and you cannot retry.
    3. Achieve a score of at least **80%** to earn your **Factoring Law Certificate**.
    
    
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

    st.info("👈 Select a question from the sidebar or click Next to start.")

def question_1():
    st.header("1️⃣ Question 1")
    st.markdown("Peter wants to fulfil a big order but doesn’t have enough money to produce the goods. He takes financing to buy raw materials before delivering the order. What type of financing is he using?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Factoring", 
                       "B. Purchase Order Financing (PO Financing)", 
                       "C. Invoice Discounting",
                       "D. Trade Credit"])
    
    if "q1" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "B. Purchase Order Financing (PO Financing)":
                show_feedback(True, "Correct! PO Financing is used to pay for goods/materials before the order is fulfilled.", "q1")
            else:
                show_feedback(False, "Incorrect. This scenario describes financing *before* delivery to produce goods, which is PO Financing.", "q1")

def question_2():
    st.header("2️⃣ Question 2")
    st.markdown("A supplier uploads an invoice that has already been financed elsewhere. What type of risk is this?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Weather risk", 
                       "B. Fraud risk", 
                       "C. Operational risk",
                       "D. Payment timing risk"])
    
    if "q2" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "B. Fraud risk":
                show_feedback(True, "Correct! Double financing is a deliberate act of deception, constituting fraud.", "q2")
            else:
                show_feedback(False, "Incorrect. Deliberately financing the same invoice twice is Fraud.", "q2")

def question_3():
    st.header("3️⃣ Question 3")
    st.markdown("What is the main purpose of factoring?")
    
    choice = st.radio("Select Answer:", 
                      ["a. To delay supplier payments", 
                       "b. To convert invoices into immediate cash", 
                       "c. To increase product prices",
                       "d. To extend credit to buyers"])
    
    if "q3" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "b. To convert invoices into immediate cash":
                show_feedback(True, "Correct! Factoring provides immediate liquidity against outstanding invoices.", "q3")
            else:
                show_feedback(False, "Incorrect. The primary goal is to improve cash flow by converting receivables to cash.", "q3")

def question_4():
    st.header("4️⃣ Question 4")
    st.markdown("A buyer receives notice that Supplier A has assigned their receivable to Factor X. Who should the buyer pay?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Supplier A", 
                       "B. Supplier’s accountant", 
                       "C. Factor X", 
                       "D. Anyone they want"])
    
    if "q4" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "C. Factor X":
                show_feedback(True, "Correct! Once notified of assignment, the debtor (buyer) must pay the Factor directly.", "q4")
            else:
                show_feedback(False, "Incorrect. After assignment notification, payment must go to the Factor.", "q4")

def question_5():
    st.header("5️⃣ Question 5")
    st.markdown("What makes factoring different from a loan?")
    
    choice = st.radio("Select Answer:", 
                      ["a. It is based on invoices, not the supplier’s creditworthiness", 
                       "b. It requires no documentation", 
                       "c. It has no risk", 
                       "d. It lasts for many years"])
    
    if "q5" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "a. It is based on invoices, not the supplier’s creditworthiness":
                show_feedback(True, "Correct! Factoring relies primarily on the credit quality of the debtor (invoice payer), not the supplier.", "q5")
            else:
                show_feedback(False, "Incorrect. Factoring is an asset-based transaction (purchasing receivables), not a loan based on the supplier's credit.", "q5")

def question_6():
    st.header("6️⃣ Question 6")
    st.markdown("Fiducia checks on an invoice registry whether an invoice has been financed before uploading it to the bidding platform. Which feature of an invoice registry does this represent?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Making graphics", 
                       "B. Preventing double financing", 
                       "C. Sending marketing emails", 
                       "D. Paying suppliers"])
    
    if "q6" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "B. Preventing double financing":
                show_feedback(True, "Correct! Registries are crucial for ensuring an invoice hasn't already been pledged or sold.", "q6")
            else:
                show_feedback(False, "Incorrect. The registry's primary risk function here is to stop double financing.", "q6")

def question_7():
    st.header("7️⃣ Question 7")
    st.markdown("A factor is analyzing whether the buyer (debtor) usually pays on time before deciding to finance an invoice. What risk is being assessed?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Credit risk", 
                       "B. Market risk", 
                       "C. Fashion risk", 
                       "D. Weather risk"])
    
    if "q7" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "A. Credit risk":
                show_feedback(True, "Correct! Credit risk assesses the debtor's ability and willingness to pay on time.", "q7")
            else:
                show_feedback(False, "Incorrect. This is Credit Risk - the risk of non-payment or late payment by the debtor.", "q7")

def question_8():
    st.header("8️⃣ Question 8")
    st.markdown("A business wants to use its receivable as collateral but still wants to collect payments itself from the buyer. What is this called?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Factoring", 
                       "B. Invoice Discounting", 
                       "C. Trade Credit", 
                       "D. PO Financing"])
    
    if "q8" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "B. Invoice Discounting":
                show_feedback(True, "Correct! In Invoice Discounting, the business retains control of the sales ledger and collection process.", "q8")
            else:
                show_feedback(False, "Incorrect. In Factoring, the factor usually collects. Invoice Discounting allows the business to collect.", "q8")

def question_9():
    st.header("9️⃣ Question 9")
    st.markdown("In a factoring transaction, which party receives money immediately?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Buyer", 
                       "B. Supplier (Seller)", 
                       "C. Factor", 
                       "D. Central Bank"])
    
    if "q9" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "B. Supplier (Seller)":
                show_feedback(True, "Correct! The Supplier receives the advance from the Factor.", "q9")
            else:
                show_feedback(False, "Incorrect. The Supplier (Seller) is the one getting financing.", "q9")

def question_10():
    st.header("🔟 Question 10")
    st.markdown("A supplier mistakenly enters the wrong invoice amount, and the factor advances too much money. What type of risk does this represent?")
    
    choice = st.radio("Select Answer:", 
                      ["A. Risk of rain", 
                       "B. Fraud risk", 
                       "C. Operational risk", 
                       "D. Credit risk"])
    
    if "q10" in st.session_state.completed_missions:
        st.info("Question Completed")
    else:
        if st.button("Submit Answer"):
            if choice == "C. Operational risk":
                show_feedback(True, "Correct! Errors in processing, data entry, or systems are classified as Operational Risk.", "q10")
            else:
                show_feedback(False, "Incorrect. Since it was a mistake (not intentional), it is Operational Risk, not Fraud.", "q10")

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
                <div class="cert-body"><b>Fiducia Factoring Law Training</b></div>
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
elif current_page_name == "1️⃣ Question 1":
    question_1()
elif current_page_name == "2️⃣ Question 2":
    question_2()
elif current_page_name == "3️⃣ Question 3":
    question_3()
elif current_page_name == "4️⃣ Question 4":
    question_4()
elif current_page_name == "5️⃣ Question 5":
    question_5()
elif current_page_name == "6️⃣ Question 6":
    question_6()
elif current_page_name == "7️⃣ Question 7":
    question_7()
elif current_page_name == "8️⃣ Question 8":
    question_8()
elif current_page_name == "9️⃣ Question 9":
    question_9()
elif current_page_name == "🔟 Question 10":
    question_10()
elif current_page_name == "🏆 Certification":
    certification()
elif current_page_name == "🏆 Leaderboard":
    leaderboard()

# Render Navigation Buttons
nav_buttons()
