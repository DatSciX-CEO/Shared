"""
Streamlit UI for LexSpend - Legal Spend Analysis
Integrates Google ADK agents with Streamlit for file upload and interaction
"""
import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Google ADK Components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Import our agent definition
from lexspend.agent import root_agent as lexspend_agent

# Import tools for direct use
from lexspend.data.preprocessing import prepare_data_for_analysis
from lexspend.data.storage import ResultsStorage
from lexspend.tools.anomaly_detection_tool import detect_anomalies
from ui.components.results_table import display_anomaly_results, display_recent_sessions

# --- Configuration ---
load_dotenv()
APP_NAME_FOR_ADK = "lexspend_app_ollama"
USER_ID = "streamlit_user"

# --- ADK Initialization (cached for performance) ---
@st.cache_resource
def initialize_adk():
    """Initialize ADK Runner and Session Service."""
    print("--- ADK Init: Initializing Runner and Session Service... ---")
    session_service = InMemorySessionService()
    runner = Runner(agent=lexspend_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)

    if 'adk_session_id' not in st.session_state:
        session_id = f"streamlit_session_{os.urandom(4).hex()}"
        st.session_state.adk_session_id = session_id
        
        print(f"--- ADK Init: Creating new ADK session ID: {session_id} ---")
        asyncio.run(session_service.create_session(
            app_name=APP_NAME_FOR_ADK,
            user_id=USER_ID,
            session_id=session_id,
            state={}
        ))
    else:
        session_id = st.session_state.adk_session_id
        existing_session = asyncio.run(session_service.get_session(
            app_name=APP_NAME_FOR_ADK, user_id=USER_ID, session_id=session_id
        ))
        if not existing_session:
            print(f"--- ADK Init: Recreating missing session {session_id} in memory... ---")
            asyncio.run(session_service.create_session(
                app_name=APP_NAME_FOR_ADK,
                user_id=USER_ID,
                session_id=session_id,
                state={}
            ))

    print("--- ADK Init: Initialization complete. ---")
    return runner, st.session_state.adk_session_id


async def run_adk_async(runner: Runner, session_id: str, user_message: str) -> str:
    """Run ADK agent asynchronously."""
    print(f"--- ADK Run: Processing user query for session {session_id} ---")
    
    # Create a proper Content object
    structured_user_message = Content(
        role="user",
        parts=[Part(text=user_message)]
    )
    
    final_response = "[Agent did not produce a response]"
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=structured_user_message):
            if event.is_final_response():
                print(f"--- ADK Run: Final response event received ---")
                
                current_final_response_text = "[Agent finished but produced no understandable text output]"
                if event.content:
                    if isinstance(event.content, str):
                        current_final_response_text = event.content
                    elif isinstance(event.content, dict):
                        if event.content.get("choices") and isinstance(event.content["choices"], list) and len(event.content["choices"]) > 0:
                            message = event.content["choices"][0].get("message")
                            if message and message.get("content"):
                                current_final_response_text = message["content"]
                        elif 'text' in event.content:
                            current_final_response_text = event.content['text']
                        elif 'content' in event.content: 
                            current_final_response_text = event.content['content']
                    else:
                        if hasattr(event.content, 'text'):
                            current_final_response_text = event.content.text
                        elif hasattr(event.content, 'parts') and event.content.parts and hasattr(event.content.parts[0], 'text'):
                             current_final_response_text = event.content.parts[0].text
                
                final_response = current_final_response_text
                break 
    except Exception as e:
        final_response = f"An error occurred: {type(e).__name__}: {e}"
        print(f"--- ADK Run: EXCEPTION during agent execution: {type(e).__name__}: {e} ---")
        import traceback
        print(traceback.format_exc())
    return final_response


def run_adk_sync(runner: Runner, session_id: str, user_message: str) -> str:
    """Run ADK agent synchronously."""
    return asyncio.run(run_adk_async(runner, session_id, user_message))


# --- Streamlit UI ---
st.set_page_config(
    page_title="LexSpend - Legal Spend Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ LexSpend: Legal Spend Analysis")
st.markdown("**AI-Powered Legal Spend Analysis with Google ADK & Local Ollama**")
st.markdown("---")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'anomaly_results' not in st.session_state:
    st.session_state.anomaly_results = None
if 'anomaly_detection_run' not in st.session_state:
    st.session_state.anomaly_detection_run = False

# Sidebar for file upload
st.sidebar.title("📁 Data Management")
uploaded_file = st.sidebar.file_uploader(
    "Upload Legal Spend Data",
    type=['csv', 'xlsx', 'xls'],
    help="Upload a CSV or Excel file with legal spend data"
)

# Process uploaded file
if uploaded_file is not None:
    # Save uploaded file temporarily
    if st.session_state.uploaded_file != uploaded_file:
        with st.spinner("Processing file..."):
            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Validate and load data
            success, message, df = prepare_data_for_analysis(tmp_path)
            
            if success:
                st.session_state.data = df
                st.session_state.uploaded_file = uploaded_file
                st.session_state.file_path = tmp_path
                st.sidebar.success(f"✅ {message}")
                st.sidebar.info(f"Loaded {len(df)} line items")
            else:
                st.sidebar.error(f"❌ {message}")
                st.session_state.data = None

# Display data preview
if st.session_state.data is not None:
    st.sidebar.subheader("📊 Data Preview")
    st.sidebar.dataframe(st.session_state.data.head(), use_container_width=True)
    
    # Anomaly Detection Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Anomaly Detection")
    if st.sidebar.button("Run Anomaly Detection", type="primary"):
        with st.spinner("Running GNN anomaly detection (this may take a few minutes)..."):
            result = detect_anomalies(st.session_state.file_path, train_model=True)
            st.session_state.anomaly_results = result
            st.session_state.anomaly_detection_run = True
            st.sidebar.success("Anomaly detection complete!")
    
    if st.session_state.anomaly_results:
        st.sidebar.text_area("Anomaly Results", st.session_state.anomaly_results, height=200)
    
    # Results display section
    if st.session_state.get('anomaly_detection_run', False):
        st.markdown("---")
        st.subheader("📊 Anomaly Detection Results")
        
        # Session selection
        selected_session = display_recent_sessions()
        
        # Threshold slider
        threshold = st.slider(
            "Review Score Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            key="anomaly_threshold"
        )
        
        # Display results
        display_anomaly_results(session_id=selected_session, threshold=threshold)

# Initialize ADK
try:
    adk_runner, current_session_id = initialize_adk()
    st.sidebar.success(f"✅ ADK Initialized\nSession: ...{current_session_id[-8:]}")
except Exception as e:
    st.error(f"**Fatal Error:** Could not initialize ADK: {e}", icon="❌")
    st.info("**Prerequisite:** Make sure your Ollama server is running with `ollama serve`.")
    st.stop()

# Main chat interface
st.subheader("💬 Chat with LexSpend Agent")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your legal spend data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ollama is analyzing..."):
            # Include file path in context if available
            if st.session_state.data is not None and 'file_path' in st.session_state:
                enhanced_prompt = f"{prompt}\n\n[Data file available at: {st.session_state.file_path}]"
            else:
                enhanced_prompt = prompt
            
            response = run_adk_sync(adk_runner, current_session_id, enhanced_prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Info section
st.sidebar.markdown("---")
st.sidebar.info(
    "**Prerequisite:** Make sure your Ollama server is running:\n"
    "```bash\nollama serve\n```\n\n"
    "**CLI Testing:** You can also test the agent via:\n"
    "```bash\nadk run lexspend\n```"
)

