import streamlit as st
import requests
import os
import sys
import io
import contextlib

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="AI Code Review Assistant", layout="wide")

# --- UI STYLING (LOGIC LORDS THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Outfit', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0B0E14 !important; }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #FFFFFF; text-transform: uppercase; letter-spacing: 2px; }
    
    .metric-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        height: 3em !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Main API URL (talks to our Phase 1/2 backend)
API_URL = "http://127.0.0.1:7860"

# --- SIDEBAR ---
with st.sidebar:
    st.title("AI CODE REVIEW ASSISTANT")
    st.markdown("### Features:")
    st.markdown("- Multi-language support\n- Structured AI code reviews\n- **NFW:** Manual Language Selection\n- **NEW:** Configuration Sidebar")
    
    with st.expander("Advanced Settings"):
        st.text_input("HF_TOKEN / OpenAI API Key", type="password")
    
    st.markdown("---")
    st.header("HACKATHON ENV MODE")
    st.caption("Play as the AI Agent manually!")
    selected_task = st.selectbox("Load OpenEnv Task:", ["task_1", "task_2", "task_3"])
    if st.button("Load Task"):
        try:
            resp = requests.post(f"{API_URL}/env/reset/{selected_task}")
            if resp.status_code == 200:
                st.success(f"Task {selected_task} Loaded!")
                st.session_state.current_task = resp.json()
        except: st.error("Backend not reachable.")

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>AI CODE REVIEW DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("---")

st.header("SANDBOX: PASTE YOUR CODE SNIPPET")
code_input = st.text_area("Code Editor", height=300, value='print("Logic Lords Online")')

col_a, col_b = st.columns([3, 1])
with col_a:
    lang = st.selectbox("Select Programming Language:", ["python", "javascript", "cpp", "java"])
with col_b:
    st.write("") # Spacer
    st.write("") # Spacer
    analyze_btn = st.button("Analyze Snippet")

if analyze_btn:
    with st.spinner("Logic Lords AI is reviewing your code..."):
        try:
            # Execute for trace
            f = io.StringIO()
            try:
                with contextlib.redirect_stdout(f):
                    exec(code_input, {"__name__": "__main__"})
                trace = f.getvalue() or "Code executed successfully."
            except Exception as e:
                trace = str(e)

            # Hit the Phase 2 backend
            resp = requests.post(f"{API_URL}/frontend_step", json={"code": code_input, "language": lang})
            if resp.status_code == 200:
                data = resp.json()
                st.markdown("---")
                
                # METRICS ROW
                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("Reward", data.get("reward", 0.0))
                with m2: st.metric("Total Score", "10")
                with m3: st.metric("Code Quality Rank", data.get("rank", "0/10"))
                with m4: st.metric("Language Detected", lang.capitalize())
                
                st.markdown("---")
                st.subheader("RUNTIME / EXECUTION TRACE")
                st.code(trace)
                
                t1, t2, t3 = st.tabs(["ISSUES", "IMPACT", "FIX"])
                with t1: st.info(data.get("issues", "No issues detected."))
                with t2: st.warning(data.get("impact", "Check for performance bottlenecks."))
                with t3: st.success(data.get("fix", "Review AI suggestions above."))
        except Exception as e:
            st.error(f"Failed to connect to AI Brain: {e}")

st.markdown("---")
st.caption("AI Code Review Assistant | Logic Lords Premium Edition")
