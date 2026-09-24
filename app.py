import os
import streamlit as st
from pathlib import Path
import dotenv

# Load environment variables
_dir = Path(__file__).resolve().parent
for p in [_dir / ".env", _dir / "adk_agent" / ".env", _dir / "adk_agent" / "mcp_bakery_app" / ".env"]:
    if p.exists():
        dotenv.load_dotenv(p)
dotenv.load_dotenv()

st.set_page_config(
    page_title="Location Intelligence & Business Agent",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Key management
    default_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            default_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not default_key:
        default_key = os.getenv("GEMINI_API_KEY", "")

    api_key = st.text_input(
        "Gemini API Key",
        value=default_key,
        type="password",
        help="Get your free key at https://aistudio.google.com/app/apikey"
    )
    
    model_name = st.selectbox(
        "Model",
        ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash"],
        index=0,
        help="gemini-3.5-flash offers maximum stability and zero wait time"
    )
    
    st.divider()
    st.markdown("### 🌍 Capabilities")
    st.markdown("""
    - **Worldwide Location Intelligence**: Analyze markets, demographics, and commercial zones anywhere globally (Uttar Pradesh, California, Tokyo, London, etc.).
    - **Bakery & Retail Advisory**: Foot traffic, competitor pricing, revenue forecasts, and logistics.
    - **Interactive Maps**: Real-world spatial insights and interactive Google Maps links.
    """)
    
    st.divider()
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="main-header">🗺️ Worldwide Location Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered geospatial analytics, demographics, competitor tracking, and business viability.</div>', unsafe_allow_html=True)

# System Prompt
SYSTEM_INSTRUCTION = """You are an advanced Worldwide Location Intelligence and Business Advisory Agent.
You can analyze cities, states, and regions anywhere across the globe (e.g. Uttar Pradesh, California, London, Tokyo, Paris, etc.).

Your Core Responsibilities:
1. Worldwide Location & State Intelligence:
   - When a user asks about any state, province, city, or neighborhood worldwide, provide comprehensive location intelligence: geography, commercial density, target demographics, foot traffic patterns, and strategic business advice.
   - Include clickable markdown hyperlinks to interactive Google Maps (e.g., [View on Google Maps](https://www.google.com/maps/search/?api=1&query=LOCATION_NAME)) for places and commercial areas mentioned.

2. Retail & Bakery Scenario:
   - For California/Los Angeles bakery benchmarks: leverage foot traffic data (e.g., Santa Monica 90403 morning activity spikes), competitor pricing ranges (~$8 - $18 for sourdough loaf), and sales forecasting.
   - For any other state/country worldwide: extrapolate foot traffic indices, local consumer habits, competitive dynamics, and prime retail corridors.

Always present your findings in a clear, structured, and insightful manner with bullet points and bold highlights.
"""

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I am your **Worldwide Location Intelligence Agent**. Ask me about market opportunities, demographics, commercial hubs, or competitor analysis for **any state, city, or neighborhood globally**!"
        }
    ]

# Quick suggestion buttons
if len(st.session_state.messages) <= 1:
    st.markdown("##### 💡 Quick Prompts")
    c1, c2, c3 = st.columns(3)
    if c1.button("📍 Uttar Pradesh Market Analysis", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Give me a business and location intelligence breakdown for opening a bakery or cafe in Uttar Pradesh, India."})
        st.rerun()
    if c2.button("📊 Los Angeles Morning Foot Traffic", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Find the zip code with the highest morning foot traffic score in Los Angeles for a bakery."})
        st.rerun()
    if c3.button("🏬 Lucknow Commercial Hotspots", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What are the top commercial areas in Lucknow, Uttar Pradesh for setting up a retail business?"})
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask about any city, state, demographics, or location intelligence..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("⚠️ Please enter your Gemini API Key in the left sidebar to continue.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing location intelligence & geospatial data..."):
                try:
                    import time
                    from google import genai
                    from google.genai import types

                    client = genai.Client(api_key=api_key)
                    
                    # Build history for conversation context
                    contents = []
                    for m in st.session_state.messages[:-1]:
                        if m["role"] == "user":
                            contents.append(f"User: {m['content']}")
                        elif m["role"] == "assistant":
                            contents.append(f"Assistant: {m['content']}")
                    contents.append(f"User: {prompt}")

                    candidate_models = [model_name, "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash"]
                    seen = set()
                    candidate_models = [m for m in candidate_models if not (m in seen or seen.add(m))]

                    reply = None
                    last_error = None

                    for cand in candidate_models:
                        for attempt in range(3):
                            try:
                                response = client.models.generate_content(
                                    model=cand,
                                    contents="\n\n".join(contents),
                                    config=types.GenerateContentConfig(
                                        system_instruction=SYSTEM_INSTRUCTION,
                                        temperature=0.7
                                    )
                                )
                                if response and response.text:
                                    reply = response.text
                                    break
                            except Exception as e:
                                last_error = e
                                time.sleep(1.5 * (attempt + 1))
                        if reply:
                            break

                    if reply:
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    else:
                        st.error(f"❌ The model is currently experiencing temporary high traffic. Please try again in 10-15 seconds. Details: {last_error}")
                except Exception as e:
                    err_msg = f"❌ Error: {str(e)}"
                    st.error(err_msg)
