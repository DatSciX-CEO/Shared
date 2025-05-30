import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Google ADK Components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.messages import Message # <-- ADDED IMPORT

# Import our agent definition from the agents module.
from disco_joker.agent import root_agent as joker_agent # Ensure you're importing root_agent

# --- Configuration ---
load_dotenv()
APP_NAME_FOR_ADK = "joker_agent_app_ollama_final"
USER_ID = "streamlit_user_ollama_final"

# --- ADK Initialization (cached for performance) ---
@st.cache_resource
def initialize_adk():
    print("--- ADK Init: Initializing Runner and Session Service... ---")
    session_service = InMemorySessionService()
    runner = Runner(agent=joker_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)

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
    print(f"--- ADK Run: Processing user query for session {session_id} ---")
    
    # Create an ADK Message object from the user's input string
    adk_user_message = Message(role="user", content=user_message) # <-- MODIFIED HERE
    
    final_response = "[Agent did not produce a response]"
    try:
        # Pass the structured ADK Message object as new_message
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=adk_user_message): # <-- MODIFIED HERE
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
    except Exception as e:
        final_response = f"An error occurred: {type(e).__name__}: {e}" # Added error type
        print(f"--- ADK Run: EXCEPTION during agent execution: {type(e).__name__}: {e} ---") # Added error type
    return final_response

def run_adk_sync(runner: Runner, session_id: str, user_message: str) -> str:
    return asyncio.run(run_adk_async(runner, session_id, user_message))

# --- Streamlit UI ---
st.set_page_config(page_title="ADK Joker Agent (Ollama)", layout="centered")
st.title("😂 The Joker Agent")
st.markdown("Powered by Google ADK & a local Ollama model. Ask for a joke or just chat!")

st.info("**Prerequisite:** Make sure your Ollama server is running in a separate terminal with `ollama serve`.", icon="🔌")

try:
    adk_runner, current_session_id = initialize_adk()
    st.sidebar.success(f"ADK Initialized\nSession: ...{current_session_id[-8:]}", icon="✅")
except Exception as e:
    st.error(f"**Fatal Error:** Could not initialize ADK: {e}", icon="❌")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me for a joke..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ollama is thinking..."):
            response = run_adk_sync(adk_runner, current_session_id, prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})