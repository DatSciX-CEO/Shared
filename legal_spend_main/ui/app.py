"""
Streamlit UI for Legal Spend Main
Integrates Google ADK agents with Streamlit for hierarchical agent system
Pattern: Follows LexSpend/ui/app.py structure
"""
import os
import asyncio
import streamlit as st
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import agent
from agent import create_legal_ops_manager

# Import UI components
from components.model_configurator import render_model_configurator
from components.data_source_selector import render_data_source_selector
from components.agent_chat import render_agent_chat
from components.results_display import render_results_display

# Configuration
APP_NAME = "legal_spend_main_app"
USER_ID = "streamlit_user"


def get_model_config_hash(model_overrides: dict = None) -> str:
    """Generate a hash of model configuration for cache invalidation."""
    import hashlib
    config_str = str(sorted((model_overrides or {}).items()))
    return hashlib.md5(config_str.encode()).hexdigest()[:8]


def initialize_adk(model_overrides: dict = None):
    """
    Initialize ADK Runner and Session Service.
    Reinitializes when model configuration changes.

    Args:
        model_overrides: Dict mapping agent names to model names

    Returns:
        Tuple of (runner, session_id)
    """
    # Check if model config has changed
    current_hash = get_model_config_hash(model_overrides)
    previous_hash = st.session_state.get('model_config_hash', '')

    # Force reinitialization if models changed
    if current_hash != previous_hash:
        st.session_state.model_config_hash = current_hash
        if 'adk_runner' in st.session_state:
            del st.session_state.adk_runner
        if 'adk_session_service' in st.session_state:
            del st.session_state.adk_session_service
        # Generate new session ID when models change
        st.session_state.adk_session_id = f"session_{os.urandom(4).hex()}"
        print(f"--- ADK Init: Model config changed, reinitializing... ---")

    # Return cached runner if available
    if 'adk_runner' in st.session_state:
        return st.session_state.adk_runner, st.session_state.adk_session_id

    print("--- ADK Init: Initializing Runner and Session Service... ---")

    # Create agent with model overrides
    agent = create_legal_ops_manager(model_overrides)

    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    if 'adk_session_id' not in st.session_state:
        session_id = f"session_{os.urandom(4).hex()}"
        st.session_state.adk_session_id = session_id
    else:
        session_id = st.session_state.adk_session_id

    print(f"--- ADK Init: Creating ADK session ID: {session_id} ---")
    asyncio.run(session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state={}
    ))

    # Cache the runner and session service
    st.session_state.adk_runner = runner
    st.session_state.adk_session_service = session_service

    print("--- ADK Init: Initialization complete. ---")
    return runner, session_id


async def run_adk_async(runner: Runner, session_id: str, user_message: str) -> str:
    """
    Run ADK agent asynchronously.
    
    Args:
        runner: ADK Runner instance
        session_id: Session identifier
        user_message: User's message
        
    Returns:
        Agent's response as string
    """
    print(f"--- ADK Run: Processing user query for session {session_id} ---")
    
    # Create a proper Content object
    structured_message = Content(
        role="user",
        parts=[Part(text=user_message)]
    )
    
    final_response = "[No response]"
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=structured_message):
            if event.is_final_response():
                print(f"--- ADK Run: Final response event received ---")
                
                if event.content:
                    # Extract text from response (handle various formats)
                    if isinstance(event.content, str):
                        final_response = event.content
                    elif hasattr(event.content, 'text'):
                        final_response = event.content.text
                    elif hasattr(event.content, 'parts') and event.content.parts:
                        if hasattr(event.content.parts[0], 'text'):
                            final_response = event.content.parts[0].text
                    elif isinstance(event.content, dict):
                        if 'text' in event.content:
                            final_response = event.content['text']
                        elif 'content' in event.content:
                            final_response = event.content['content']
                
                break
    except Exception as e:
        final_response = f"An error occurred: {type(e).__name__}: {e}"
        print(f"--- ADK Run: EXCEPTION during agent execution: {type(e).__name__}: {e} ---")
        import traceback
        print(traceback.format_exc())
    
    return final_response


def run_adk_sync(runner: Runner, session_id: str, user_message: str) -> str:
    """
    Run ADK agent synchronously.
    
    Args:
        runner: ADK Runner instance
        session_id: Session identifier
        user_message: User's message
        
    Returns:
        Agent's response as string
    """
    return asyncio.run(run_adk_async(runner, session_id, user_message))


# --- Streamlit UI ---
st.set_page_config(
    page_title="Legal Spend Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ Legal Spend Analysis - Hierarchical Agent System")
st.markdown("**AI-Powered Legal Spend Analysis with Google ADK & Ollama**")
st.markdown("*Manager Agent orchestrating 6 specialized sub-agents*")
st.markdown("---")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent_models' not in st.session_state:
    st.session_state.agent_models = {}

# Sidebar: Agent Configuration
st.sidebar.title("⚙️ Agent Configuration")
render_model_configurator()

# Sidebar: Data Source Selection
st.sidebar.markdown("---")
render_data_source_selector()

# Initialize ADK with model overrides
try:
    adk_runner, current_session_id = initialize_adk(st.session_state.agent_models)
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ ADK Ready")
    st.sidebar.caption(f"Session: ...{current_session_id[-8:]}")
except Exception as e:
    st.error(f"**Fatal Error:** Could not initialize ADK: {e}", icon="❌")
    st.info("**Prerequisite:** Make sure your Ollama server is running with `ollama serve`.")
    st.stop()

# Main content area with tabs
tab1, tab2 = st.tabs(["💬 Chat", "📊 Results"])

with tab1:
    # Main chat interface
    st.subheader("💬 Chat with Legal Ops Manager")
    st.caption("Ask questions about your legal spend data. The manager will delegate to specialized agents.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your legal spend data..."):
        # Add data context if available
        enhanced_prompt = prompt
        if st.session_state.get('data_loaded', False):
            if st.session_state.get('data_source_type') in ['csv', 'parquet']:
                enhanced_prompt = f"{prompt}\n\n[Data file available at: {st.session_state.data_file_path}]"
            elif st.session_state.get('data_source_type') == 'sql':
                sql_config = st.session_state.get('sql_config', {})
                enhanced_prompt = f"{prompt}\n\n[SQL Server: {sql_config.get('server')}/{sql_config.get('database')}, Table: {sql_config.get('table_name')}]"
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Ollama is analyzing..."):
                response = run_adk_sync(adk_runner, current_session_id, enhanced_prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    # Results display
    render_results_display()

# Info section in sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "**Prerequisite:** Make sure your Ollama server is running:\n"
    "```bash\nollama serve\n```\n\n"
    "**CLI Testing:** You can also test the agent via:\n"
    "```bash\nadk run legal_spend_main\n```\n\n"
    "**Agent Hierarchy:**\n"
    "- LegalOpsManager (orchestrator)\n"
    "  - DataAnalyst\n"
    "  - SpendAnalyzer\n"
    "  - eDiscoverySpecialist\n"
    "  - AnomalyDetector\n"
    "  - SpendForecaster\n"
    "  - ComplianceAuditor"
)


