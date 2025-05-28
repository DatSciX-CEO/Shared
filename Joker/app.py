import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Google ADK Components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Import our agent definition from the agents module
from agents.joker.agent import agent as joker_agent

# --- Configuration ---
load_dotenv()
APP_NAME_FOR_ADK = "joker_agent_app_ollama_v1"
USER_ID = "streamlit_user_ollama_v1"

# --- ADK Initialization (cached for performance) ---
@st.cache_resource
def initialize_adk():
    print("--- ADK Init: Initializing Runner and Session Service... ---")
    session_service = InMemorySessionService()
    runner = Runner(agent=joker_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)

    if 'adk_session_id' not in st.session_state:
        session_id = f"streamlit_session_{os.urandom(4).hex()}"
        st.session_state.adk_session_id = session_id
        session_service.create_session(app_name=APP_NAME_FOR_ADK, user_id=USER_ID, session_id=session_id, state={})
        print(f"--- ADK Init: Created new ADK session ID: {session_id} ---")
    else:
        session_id = st.session_state.adk_session_id
        if not session_service.get_session(app_name=APP_NAME_FOR_ADK, user_id=USER_ID, session_id=session_id):
            print(f"--- ADK Init: Recreating missing session {session_id} in memory... ---")
            session_service.create_session(app_name=APP_NAME_FOR_ADK, user_id=USER_ID, session_id=session_id, state={})

    print("--- ADK Init: Initialization complete. ---")
    return runner, st.session_state.adk_session_id

async def run_adk_async(runner: Runner, session_id: str, user_message: str) -> str:
    print(f"--- ADK Run: Processing user query for session {session_id} ---")
    final_response = "[Agent did not produce a response]"
    try:
        # The runner can directly accept the user's text string
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_message):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
    except Exception as e:
        final_response = f"An error occurred: {e}"
        print(f"--- ADK Run: EXCEPTION during agent execution: {e} ---")
    return final_response

def run_adk_sync(runner: Runner, session_id: str, user_message: str) -> str:
    return asyncio.run(run_adk_async(runner, session_id, user_message))

# --- Streamlit UI ---
st.set_page_config(page_title="ADK Joker Agent (Ollama)", layout="centered")
st.title("😂 The Joker Agent")
st.markdown("Powered by Google ADK & a local Ollama model. Ask for a joke or just chat!")

# Prerequisite Check for Ollama
st.info("**Prerequisite:** Make sure your Ollama server is running in a separate terminal with `ollama serve`.", icon="🔌")

# Initialize ADK
try:
    adk_runner, current_session_id = initialize_adk()
    st.sidebar.success(f"ADK Initialized\nSession: ...{current_session_id[-8:]}", icon="✅")
except Exception as e:
    st.error(f"**Fatal Error:** Could not initialize ADK: {e}", icon="❌")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me for a joke..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ollama is thinking..."):
            response = run_adk_sync(adk_runner, current_session_id, prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})