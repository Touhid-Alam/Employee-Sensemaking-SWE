import streamlit as st
import pandas as pd
import random
import time
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ELITE SWE | Employee Sensemaking Study",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED UI STYLING (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=JetBrains+Mono:wght@400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }

    /* HEADER */
    .elite-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        color: white;
        padding: 40px;
        border-radius: 0 0 20px 20px;
        margin-top: -60px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .elite-title { font-size: 38px; font-weight: 800; letter-spacing: -0.5px; }
    .elite-subtitle { font-size: 16px; opacity: 0.9; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; }

    /* SWE CONCEPT BOX */
    .swe-concept-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .swe-concept-box p, .swe-concept-box li, .swe-concept-box h3, .swe-concept-box h4, .swe-concept-box ol {
        color: #0f172a !important;
    }

    .swe-step {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 6px;
        color: #0f172a !important;
    }
    .swe-step strong { color: #1e3a8a !important; font-size: 18px; }

    /* INSTRUCTION BOX */
    .instruction-box {
        background-color: #f0f9ff;
        border: 2px solid #bae6fd;
        border-left: 10px solid #0284c7;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .instruction-box, .instruction-box div, .instruction-box span {
        color: #0c4a6e !important; 
        font-size: 20px;
        line-height: 1.6;
    }
    .instruction-title {
        font-weight: 800;
        font-size: 26px;
        text-transform: uppercase;
        margin-bottom: 15px;
        display: block;
        color: #0369a1 !important;
    }
    .step-item {
        margin-bottom: 12px;
        font-weight: 600;
        font-size: 22px;
        color: #0c4a6e !important;
    }

    /* TRANSCRIPT BOX (HEIGHT INCREASED TO 850px) */
    .transcript-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 20px;
        height: 850px; /* INCREASED SIZE */
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        line-height: 1.6;
        color: #334155 !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* SOURCE BADGES */
    .source-badge-ai { 
        background-color: #e11d48; /* Red */
        color: white !important; 
        padding: 12px; 
        border-radius: 6px; 
        font-weight: 700; 
        margin-bottom: 15px; 
        display: block; 
        text-align: center;
        border: 1px solid #9f1239;
    }
    .source-badge-human { 
        background-color: #16a34a; /* Green */
        color: white !important; 
        padding: 12px; 
        border-radius: 6px; 
        font-weight: 700; 
        margin-bottom: 15px; 
        display: block; 
        text-align: center;
        border: 1px solid #14532d;
    }

    /* COMPLIANCE BOX */
    .compliance-box {
        background-color: #0f172a; 
        padding: 25px;
        border-radius: 10px;
        margin-top: 25px;
        border: 1px solid #334155;
    }
    .compliance-text {
        color: #ffffff !important;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        display: block;
    }
    .compliance-title {
        color: #94a3b8 !important;
        text-transform: uppercase;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 5px;
        display: block;
    }

    /* INPUT FIELDS (Forced White Background) */
    .stTextArea textarea { 
        font-size: 16px !important; 
        line-height: 1.5 !important; 
        border-radius: 8px; 
        border: 1px solid #cbd5e1; 
        color: #000000 !important; 
        background-color: #ffffff !important; 
    }
    
    /* BOLD LABELS */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }

    /* SURVEY QUESTIONS (DARK BOX + WHITE TEXT) */
    .survey-question {
        background-color: #0f172a; /* Dark Navy Background */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    .survey-question p {
        font-size: 24px !important; 
        font-weight: 700 !important; 
        color: #ffffff !important; /* WHITE TEXT */
        margin-bottom: 0px !important;
        line-height: 1.4 !important; 
    }

    /* BUTTONS */
    div.stButton > button { background-color: #2563eb; color: white; border: none; padding: 14px 28px; font-size: 18px; font-weight: 600; border-radius: 8px; width: 100%; transition: all 0.2s; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); }
    div.stButton > button:hover { background-color: #1d4ed8; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3); }

    .footer { text-align: center; margin-top: 60px; font-size: 12px; color: #94a3b8; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & CONSTANTS ---

TRANSCRIPT_TEXT = """
<strong style="color:#d946ef;">SOURCE DATASET:</strong> AMI Meeting Corpus
<br><strong style="color:#3b82f6;">OFFICIAL SOURCE:</strong> <a href="https://groups.inf.ed.ac.uk/ami/corpus/" target="_blank">University of Edinburgh (AMI Project)</a>
<br><strong>MEETING ID:</strong> ES2002a (Remote Control Design Kick-off)
<br><strong>LOCATION:</strong> Edinburgh, UK
<br><strong>PARTICIPANTS:</strong> PM (Project Manager), ID (Industrial Designer), UI (User Interface), ME (Marketing Expert)
<hr>

<strong>PM:</strong> Okay, welcome everyone. This is our first meeting. As you know, we are here to design a new product. But before we get to business, let's do a quick warm-up to get to know each other. The instruction is to draw your favorite animal on the whiteboard and explain why you chose it.

<strong>UI:</strong> [Laughs] Okay, I'll go first. I drew a monkey. Mostly because they are agile and curious. That's how I see my approach to interface design.

<strong>ME:</strong> Nice. I drew an owl. Wisdom, vision, seeing the whole market... that sort of thing.

<strong>ID:</strong> I went with a cat. Independent, clean lines, very aesthetic.

<strong>PM:</strong> Great. I drew a dog because I'm here to herd the group and keep us loyal to the deadline. Okay, fun’s over. Let’s get to work.

<strong>PM:</strong> The project goal is to design a new Television Remote Control. This isn't just a standard replacement; we need something "original," "trendy," and "user-friendly."

<strong>ME:</strong> I’ve reviewed the market research. The trend right now is simplicity. Consumers are frustrated with remotes that have fifty buttons. They want something sleek.

<strong>ID:</strong> "Trendy" usually means unique materials. Are we thinking rubber, wood, or just plastic?

<strong>PM:</strong> That depends on the constraints. And this is the most important part of today's meeting. We have strict instructions from management.

<strong>PM:</strong> We need to be very clear on the money. The target Selling Price for this remote is 25.00 Euros. That is what the customer pays in the store.

<strong>ME:</strong> 25 Euro? That puts us in the mid-range market. Not premium, but not cheap junk.

<strong>PM:</strong> Exactly. However, to make a profit, our Manufacturing Cost is capped at 12.50 Euros per unit.

<strong>ID:</strong> Wait, 12.50? That is our production limit?

<strong>PM:</strong> Yes. You cannot go over 12.50 Euros for materials and assembly.

<strong>ID:</strong> That is going to be tight. If we want a fancy LCD screen or soft-touch rubber, we will burn through that budget fast. We might be stuck with standard plastic casing.

<strong>UI:</strong> We can save money on the internal tech. I suggest we avoid rechargeable units and stick to standard AA batteries. That’s the cheapest power source.

<strong>ME:</strong> Agreed. AA batteries are fine for this price point. Users hate charging remotes anyway.

<strong>PM:</strong> Now, regarding the timeline. This is the other stress point. We need a functional prototype ready for the International Tech Trade Show.

<strong>ME:</strong> When is the show?

<strong>PM:</strong> The deadline is October 15th.

<strong>ID:</strong> October 15th? That gives us barely four weeks for the initial design and mock-up.

<strong>PM:</strong> I know it's aggressive. But if we miss October 15th, we miss the launch window for the holiday season.

<strong>ID:</strong> Okay, we’ll have to work weekends, but we can do it.

<strong>PM:</strong> Excellent. So to recap: We are making a trendy remote. Selling price is 25 Euro, but our Manufacturing Budget is 12.50 Euro. We use AA Batteries. And the hard deadline is October 15th. Let’s get to work.
"""

AI_INPUT_TEXT = """Subject: Executive Summary: Remote Control Design Kick-off

Project Scope: 
The team convened to initiate the design phase for a new "original" and "trendy" Television Remote Control. The objective is to create a device that prioritizes simplicity and user-friendliness, moving away from complex interfaces with excessive buttons.

Financial & Technical Decisions: 
The Project Manager outlined strict financial constraints. To target the mid-range market, the manufacturing budget has been capped at 25.00 Euros per unit. Due to these budgetary restrictions, the Industrial Designer noted that advanced materials like wood or soft-touch rubber are likely unfeasible, suggesting a standard plastic casing instead.

Component Specification: 
Regarding internal components, the team discussed power sources. To align with the "trendy" and "high-tech" design goals, the team reached a consensus to utilize Rechargeable Lithium-Ion units rather than disposable batteries.

Timeline: 
A functional prototype is required for the International Tech Trade Show. The team faces an aggressive deadline of October 15th, leaving approximately four weeks for the initial design phase.
"""

# --- 4. BACKEND FUNCTIONS ---

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def save_to_google_sheets(data_row):
    try:
        # Requires .streamlit/secrets.toml
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        
        # UPDATED: Matches your specific sheet name
        sheet = client.open("Employee Sense Making Data").sheet1 
        
        sheet.append_row(data_row)
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

def analyze_traps(final_text):
    text = final_text.lower()
    num_res = "PASS" if "12.50" in text else "FAIL"
    tech_res = "PASS" if ("aa" in text and "lithium" not in text) else "FAIL"
    return num_res, tech_res

# --- 5. MAIN LOGIC ---

def main():
    if 'page' not in st.session_state: st.session_state.page = 'intro'
    if 'participant_id' not in st.session_state: st.session_state.participant_id = str(uuid.uuid4())[:8]
    if 'condition_group' not in st.session_state: 
        st.session_state.condition_group = random.choice(["AI_LABEL", "HUMAN_LABEL"])
    
    if 'participant_data' not in st.session_state: st.session_state.participant_data = {}

    # HEADER
    st.markdown("""
        <div class="elite-header">
            <div class="elite-title">ELITE Research Lab</div>
            <div class="elite-subtitle">Simulated Work Environment (SWE)</div>
        </div>
    """, unsafe_allow_html=True)

    # --- PAGE 0: INTRO ---
    if st.session_state.page == 'intro':
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown("""
            <div class="swe-concept-box">
                <h3 style="text-align:center;">👋 Welcome to the Simulation</h3>
                <p>This study utilizes a <strong>Simulated Work Environment (SWE)</strong> to investigate <strong>Employee Sensemaking</strong> in modern digital workflows.</p>
                <p>As AI tools become "social actors" in our communication, professionals often face a <strong>"Trust Paradox"</strong>: balancing efficiency with the need for Epistemic Agency (your role as the authoritative thinker).</p>
                <hr>
                <h4 style="margin-bottom:15px;">🔍 Your Role & Scenario</h4>
                <p>You are a <strong>Senior Project Manager</strong>. You have just attended a product kick-off meeting for a new device design.</p>
                <p><strong>Your Mission:</strong> You must finalize the meeting minutes for the Director. You will be provided with:</p>
                <ol>
                    <li>The <strong>Raw Transcript</strong> (Ground Truth)</li>
                    <li>A <strong>Draft Summary</strong> (Needs Verification)</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🛠️ The Process Workflow")
            st.markdown("""
            <div class="swe-step">
                <strong>Step 1: ANALYZE</strong><br>
                Read the Source Transcript on the left to identify the <em>actual</em> budget figures and technical decisions made.
            </div>
            <div class="swe-step">
                <strong>Step 2: VALIDATE</strong><br>
                Review the Draft Summary on the right. Does it match the transcript? Edit any discrepancies.
            </div>
            <div class="swe-step">
                <strong>Step 3: COMMUNICATE</strong><br>
                Draft a brief confirmation email to your Director attaching the validated summary.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
            with col_b2:
                if st.button("I Understand My Role - Enter Simulation →"):
                    st.session_state.page = 'consent'
                    st.rerun()

    # --- PAGE 1: CONSENT ---
    elif st.session_state.page == 'consent':
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown("### 👤 User Profile")
            st.info("To benchmark your performance, please complete your professional profile. Data is anonymized.")
            
            with st.form("pii_form"):
                st.markdown("**Full Name**")
                name = st.text_input("Name", label_visibility="collapsed")
                
                c_a, c_b = st.columns(2)
                with c_a: 
                    st.markdown("**Age**")
                    age = st.number_input("Age", 18, 99, label_visibility="collapsed")
                with c_b: 
                    st.markdown("**Sex**")
                    sex = st.selectbox("Sex", ["Select...", "Male", "Female", "Other", "Prefer not to say"], label_visibility="collapsed")
                
                c_c, c_d = st.columns(2)
                with c_c: 
                    st.markdown("**Current Job Role**")
                    role = st.text_input("Role", label_visibility="collapsed")
                with c_d: 
                    st.markdown("**Workspace Type**")
                    ws = st.selectbox("WS", ["On-Site (Office)", "Remote (Home)", "Hybrid"], label_visibility="collapsed")

                st.markdown("**Email Address**")
                email = st.text_input("Email", label_visibility="collapsed")
                
                st.markdown("---")
                submitted = st.form_submit_button("Save Profile & Launch Workstation →")
                
            if submitted:
                if name.strip() and email.strip() and role.strip() and sex != "Select...":
                    st.session_state.participant_data = {
                        "name": name, "age": age, "sex": sex, 
                        "role": role, "email": email, "workspace": ws
                    }
                    st.session_state.start_time = time.time()
                    st.session_state.page = 'task'
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all fields (Name, Email, Role, Sex).")

    # --- PAGE 2: TASK ---
    elif st.session_state.page == 'task':
        
        # INSTRUCTIONS
        st.markdown("""
        <div class="instruction-box">
            <span class="instruction-title">Step 2: Analyst Workstation</span>
            <div class="step-item">1️⃣ <strong>READ:</strong> Review the <em>Ground Truth Transcript</em> (Left Panel).</div>
            <div class="step-item">2️⃣ <strong>VALIDATE:</strong> Compare the <em>Draft Summary</em> (Right Panel) against the transcript.</div>
            <div class="step-item">3️⃣ <strong>EDIT:</strong> Correct any discrepancies in the summary text.</div>
            <div class="step-item">4️⃣ <strong>SUBMIT:</strong> Write a confirmation email to the Director.</div>
        </div>
        """, unsafe_allow_html=True)

        left_col, right_col = st.columns([1, 1], gap="medium")

        # LEFT: SOURCE
        with left_col:
            st.markdown("### 📄 Source Transcript (Read-Only)")
            st.caption("Meeting Log | ID: ES2002a")
            # Transcript height = 850px
            st.markdown(f'<div class="transcript-box">{TRANSCRIPT_TEXT}</div>', unsafe_allow_html=True)

        # RIGHT: EDITOR
        with right_col:
            st.markdown("### ✍️ Editing Interface")
            
            with st.form("task_form"):
                
                # --- SOURCE BADGES ---
                if st.session_state.condition_group == "AI_LABEL":
                    # Red Background, White Text
                    st.markdown('<div class="source-badge-ai">📄 SOURCE: GEMINI (AI MODEL)</div>', unsafe_allow_html=True)
                else:
                    # Green Background, White Text
                    st.markdown('<div class="source-badge-human">📄 SOURCE: ELITE RESEARCH LAB (HUMAN)</div>', unsafe_allow_html=True)

                # 1. SUMMARY VALIDATION
                st.markdown("**1. Summary Validation**")
                st.caption("This is a summary generated by the source. Kindly edit if you think this needs changed.")
                input_b = st.text_area("Draft Text", value=AI_INPUT_TEXT, height=400, label_visibility="collapsed")
                
                # 2. DIRECTOR EMAIL
                st.markdown("**2. Director Email**")
                st.caption("Kindly write a short email to the director about your work.")
                input_c = st.text_area("Email Body", height=150, placeholder="Subject: Kick-off Summary\n\nDear Director,\n\nAttached is the validated summary...", label_visibility="collapsed")
                
                # --- COMPLIANCE SECTION ---
                st.markdown('<div class="compliance-box">', unsafe_allow_html=True)
                st.markdown('<span class="compliance-title">3. COMPLIANCE CHECK</span>', unsafe_allow_html=True)
                # White Text Question
                st.markdown('<span class="compliance-text">Did you review the Source Transcript?</span>', unsafe_allow_html=True)
                
                seen_text = st.selectbox("Compliance Select", 
                                         ["Select...", "Yes, fully", "Partially", "No, I trusted the summary"],
                                         label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                submit_task = st.form_submit_button("Submit Work Package →")
            
            if submit_task:
                if seen_text == "Select...":
                    st.error("⚠️ Please confirm if you reviewed the transcript.")
                elif not input_b.strip() or not input_c.strip():
                     st.error("⚠️ Text fields cannot be empty.")
                else:
                    st.session_state.final_b = input_b
                    st.session_state.final_c = input_c
                    st.session_state.seen_text_response = seen_text 
                    st.session_state.dwell_time = time.time() - st.session_state.start_time
                    st.session_state.page = 'survey'
                    st.rerun()

    # --- PAGE 3: SURVEY (UPDATED: WHITE TEXT ON DARK BACKGROUND) ---
    elif st.session_state.page == 'survey':
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown("### 📊 Post-Task Questionnaire")
            st.write("Please rate your experience (1 = Strongly Disagree, 10 = Strongly Agree).")
            
            with st.form("survey"):
                # Style applied: .survey-question (Dark Bg) and .survey-question p (White Text)
                
                st.markdown('<div class="survey-question"><p>1. Factual Accuracy: How accurate was the summary compared to the transcript?</p></div>', unsafe_allow_html=True)
                q1 = st.number_input("Q1 Rating", 1, 10, label_visibility="collapsed")
                
                st.markdown('<div class="survey-question"><p>2. Initial Trust: Did you trust the summary before verifying it?</p></div>', unsafe_allow_html=True)
                q2 = st.number_input("Q2 Rating", 1, 10, label_visibility="collapsed")
                
                st.markdown('<div class="survey-question"><p>3. Cognitive Effort: How much mental effort was required to verify the details?</p></div>', unsafe_allow_html=True)
                q3 = st.number_input("Q3 Rating", 1, 10, label_visibility="collapsed")
                
                st.markdown('<div class="survey-question"><p>4. System Reliance: Would you rely on this system for critical reporting tasks?</p></div>', unsafe_allow_html=True)
                q4 = st.number_input("Q4 Rating", 1, 10, label_visibility="collapsed")
                
                st.markdown('<div class="survey-question"><p>5. Process Transparency: Was the generation source/process clear to you?</p></div>', unsafe_allow_html=True)
                q5 = st.number_input("Q5 Rating", 1, 10, label_visibility="collapsed")
                
                st.markdown("---")
                final_submit = st.form_submit_button("Submit Final Data & Close")
                
            if final_submit:
                p_data = st.session_state.participant_data
                num_f, tech_f = analyze_traps(st.session_state.final_b)
                seen_resp = st.session_state.get('seen_text_response', 'Unknown')

                row = [
                    st.session_state.participant_id, st.session_state.condition_group,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), round(st.session_state.dwell_time, 2),
                    seen_resp, num_f, tech_f,
                    st.session_state.final_b, st.session_state.final_c,
                    p_data.get('name'), p_data.get('age'), p_data.get('sex'),
                    p_data.get('email'), p_data.get('workspace'), p_data.get('role'),
                    q1, q2, q3, q4, q5
                ]
                
                if save_to_google_sheets(row):
                    st.success("✅ Data Uploaded Successfully! You may close the tab.")
                    st.balloons()
                else:
                    st.error("❌ Connection Error.")

    st.markdown('<div class="footer">© 2025 ELITE Research Lab | Data Source: AMI Meeting Corpus</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()