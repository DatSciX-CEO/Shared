# Copyright 2025 DatSciX
# Streamlit UI for Timekeeper Analysis Agent

"""Streamlit web interface for the Timekeeper Analysis Agent system."""

import streamlit as st
import sys
from pathlib import Path
import os
import asyncio

# Add parent directory to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents import timekeeper_director


# Page configuration
st.set_page_config(
    page_title="Timekeeper Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()

if "runner" not in st.session_state:
    st.session_state.runner = Runner(
        agent=timekeeper_director,
        app_name="timekeeper_analysis",
        session_service=st.session_state.session_service
    )

    if "session_id" not in st.session_state:
        session = asyncio.run(st.session_state.session_service.create_session(user_id="streamlit_user", app_name="timekeeper_analysis"))
        st.session_state.session_id = session.id

if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


# Header
st.markdown('<div class="main-header">📊 Timekeeper Analysis Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-powered analysis of timekeeper data for eDiscovery operations</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This application uses a hierarchical AI agent system to analyze timekeeper data:

    - **Productivity Analysis**: Utilization, efficiency, trends
    - **Billing Anomaly Detection**: Unusual patterns, compliance issues
    - **Resource Optimization**: Allocation recommendations

    Powered by Google ADK with local Ollama models.
    """)

    st.divider()

    st.header("System Status")
    st.metric("Active Session", st.session_state.session_id[:8] + "...")
    st.metric("Agent Status", "🟢 Ready" if st.session_state.runner else "🔴 Not Ready")

    st.divider()

    if st.button("🔄 Reset Session"):
        st.session_state.messages = []
        st.session_state.analysis_complete = False
        session = st.session_state.session_service.create_session(user_id="streamlit_user", app_name="timekeeper_analysis")
        st.session_state.session_id = session.id
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Analysis Workflow")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Timekeeper Data File",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Upload a CSV, Excel, or Parquet file containing timekeeper data"
    )

    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = Path("temp_uploads")
        temp_path.mkdir(exist_ok=True)
        file_path = temp_path / uploaded_file.name

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Comprehensive Analysis", "Productivity Only", "Billing Anomalies Only", "Resource Optimization Only"]
        )

        # Start analysis button
        if st.button("🚀 Start Analysis", type="primary"):
            with st.spinner("Analyzing timekeeper data..."):
                try:
                    # Construct prompt based on analysis type and file path
                    prompt = f"Please analyze the timekeeper data file at {file_path}. "
                    if analysis_type == "Comprehensive Analysis":
                        prompt += "Provide a comprehensive analysis including productivity, billing anomalies, and resource optimization."
                    elif analysis_type == "Productivity Only":
                        prompt += "Focus on productivity analysis only."
                    elif analysis_type == "Billing Anomalies Only":
                        prompt += "Focus on detecting billing anomalies and compliance issues only."
                    else:
                        prompt += "Focus on resource optimization recommendations only."

                    # Define an async function to handle the async generator
                    async def get_response_events():
                        response_parts = []
                        async for event in st.session_state.runner.stream_query(
                            user_id="streamlit_user",
                            session_id=st.session_state.session_id,
                            message=prompt
                        ):
                            if hasattr(event, 'text'):
                                response_parts.append(event.text)
                        return "".join(response_parts)

                    # Run the async function to get the full response
                    response = asyncio.run(get_response_events())

                    # Store in messages
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.analysis_complete = True

                    st.success("✅ Analysis complete!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")

with col2:
    st.header("Quick Stats")
    if uploaded_file:
        st.info(f"**File**: {uploaded_file.name}")
        st.info(f"**Size**: {uploaded_file.size / 1024:.2f} KB")
    else:
        st.info("No file uploaded yet")

# Display conversation history
if st.session_state.messages:
    st.divider()
    st.header("Analysis Results")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Export options
if st.session_state.analysis_complete:
    st.divider()
    st.header("Export Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Export as Markdown"):
            st.info("Markdown export functionality coming soon")

    with col2:
        if st.button("📊 Export as PDF"):
            st.info("PDF export functionality coming soon")

    with col3:
        if st.button("💾 Export as JSON"):
            st.info("JSON export functionality coming soon")

# Footer
st.divider()
st.caption("Powered by Google ADK + Ollama | Built by DatSciX")


if __name__ == "__main__":
    st.markdown("Run with: `streamlit run streamlit_app.py`")
