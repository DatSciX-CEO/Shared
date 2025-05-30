import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Google ADK Components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
# Import the Content class for creating proper messages
from google.genai.types import Content, Part

# Import our agent definition from the agents module.
from disco_joker.agent import root_agent as joker_agent

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
    
    # Create a proper Content object instead of a dictionary
    structured_user_message = Content(
        role="user",
        parts=[Part(text=user_message)]
    )
    
    final_response = "[Agent did not produce a response]" # Default
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=structured_user_message):
            if event.is_final_response():
                print(f"--- ADK Run: Final response event received. Content type: {type(event.content)}, Content: {str(event.content)[:500]} ---") # Debug print
                
                current_final_response_text = "[Agent finished but produced no understandable text output]"
                if event.content:
                    if isinstance(event.content, str):
                        current_final_response_text = event.content
                    elif isinstance(event.content, dict):
                        # Most direct way LiteLLM/Ollama might return text via ADK
                        if event.content.get("choices") and isinstance(event.content["choices"], list) and len(event.content["choices"]) > 0:
                            message = event.content["choices"][0].get("message")
                            if message and message.get("content"):
                                current_final_response_text = message["content"]
                        # Simpler dictionary structures ADK might normalize to
                        elif 'text' in event.content:
                            current_final_response_text = event.content['text']
                        elif 'content' in event.content: 
                            current_final_response_text = event.content['content']
                        else:
                            print(f"--- ADK Run: WARNING - Final event.content is a dictionary, but no expected text key found. Dic Content: {str(event.content)[:500]} ---")
                    else: # Fallback for other object types if ADK wraps it differently
                        if hasattr(event.content, 'text'):
                            current_final_response_text = event.content.text
                        elif hasattr(event.content, 'parts') and event.content.parts and hasattr(event.content.parts[0], 'text'):
                             current_final_response_text = event.content.parts[0].text # Less likely for Ollama output
                        else:
                            print(f"--- ADK Run: WARNING - Final event content is of unexpected type or structure. Content: {str(event.content)[:500]} ---")
                
                final_response = current_final_response_text
                break 
    except Exception as e:
        final_response = f"An error occurred: {type(e).__name__}: {e}"
        print(f"--- ADK Run: EXCEPTION during agent execution: {type(e).__name__}: {e} ---")
        # For detailed debugging of the exception itself:
        import traceback
        print(traceback.format_exc())
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