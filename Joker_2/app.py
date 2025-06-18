import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Google ADK Components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Import our agent definition
from disco_joker.agent import root_agent as joker_agent

# --- Configuration ---
load_dotenv()
APP_NAME_FOR_ADK = "joker_agent_ultra_simple_fixed"
USER_ID = "simple_user"

# --- Ultra Simple ADK Setup (Fixed) ---
@st.cache_resource
def initialize_ultra_simple():
    """Ultra simple - just use fresh sessions each time (we know this works)"""
    print("--- Ultra Simple Init: Using fresh sessions for zero memory ---")
    session_service = InMemorySessionService()
    runner = Runner(agent=joker_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)
    print("--- Ultra Simple Init: Complete ---")
    return runner, session_service

async def run_ultra_simple_fixed(runner: Runner, session_service: InMemorySessionService, user_message: str) -> str:
    """Ultra simple execution - fresh session each time = no memory"""
    
    # Generate a fresh session ID for each interaction
    session_id = f"ultra_simple_{os.urandom(6).hex()}"
    print(f"--- Ultra Simple Run: Creating fresh session {session_id} ---")
    
    # Create the session first
    try:
        await session_service.create_session(
            app_name=APP_NAME_FOR_ADK,
            user_id=USER_ID,
            session_id=session_id,
            state={}
        )
        print(f"--- Ultra Simple Run: Session {session_id} created successfully ---")
    except Exception as e:
        print(f"--- Ultra Simple Run: Session creation warning: {e} ---")
        # Continue anyway - some versions might not need explicit creation
    
    # Create message
    structured_user_message = Content(
        role="user",
        parts=[Part(text=user_message)]
    )
    
    final_response = "[No response generated]"
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=structured_user_message
        ):
            if event.is_final_response():
                print(f"--- Ultra Simple Run: Got final response for {session_id} ---")
                
                if event.content:
                    if isinstance(event.content, str):
                        final_response = event.content
                    elif isinstance(event.content, dict):
                        # Handle different response formats from Ollama
                        if event.content.get("choices") and len(event.content["choices"]) > 0:
                            message = event.content["choices"][0].get("message")
                            if message and message.get("content"):
                                final_response = message["content"]
                        elif 'text' in event.content:
                            final_response = event.content['text']
                        elif 'content' in event.content:
                            final_response = event.content['content']
                        else:
                            final_response = f"Response received: {str(event.content)[:500]}"
                    else:
                        if hasattr(event.content, 'text'):
                            final_response = event.content.text
                        elif hasattr(event.content, 'parts') and event.content.parts:
                            final_response = event.content.parts[0].text
                        else:
                            final_response = f"Response object: {str(event.content)[:500]}"
                else:
                    final_response = "[Event had no content]"
                break
                
    except Exception as e:
        final_response = f"Execution error: {type(e).__name__}: {e}"
        print(f"--- Ultra Simple Run: Exception: {e} ---")
        import traceback
        print(traceback.format_exc())
    
    print(f"--- Ultra Simple Run: Session {session_id} complete ---")
    return final_response

def run_ultra_simple_sync(runner: Runner, session_service: InMemorySessionService, user_message: str) -> str:
    """Synchronous wrapper for ultra simple execution"""
    return asyncio.run(run_ultra_simple_fixed(runner, session_service, user_message))

# --- Streamlit UI (Ultra Simple & Fixed) ---
st.set_page_config(page_title="Ultra Simple Joker Agent", layout="centered")
st.title("😂 Ultra Simple Joker Agent")
st.markdown("Fresh session per interaction = Zero memory!")

st.info("**Prerequisite:** Ollama server running with `ollama serve`", icon="🔌")
st.success("**Zero Memory:** Fresh session each time!", icon="✨")

try:
    runner, session_service = initialize_ultra_simple()
    st.sidebar.success("Ultra Simple ADK Ready", icon="✅")
    st.sidebar.info("Method: Fresh sessions", icon="🔄")
except Exception as e:
    st.error(f"Initialization failed: {e}", icon="❌")
    st.stop()

# Track interactions for demo
if 'interaction_count' not in st.session_state:
    st.session_state.interaction_count = 0

# Chat interface
if prompt := st.chat_input("Ask for a joke or chat..."):
    st.session_state.interaction_count += 1
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Processing interaction #{st.session_state.interaction_count} with fresh session..."):
            response = run_ultra_simple_sync(runner, session_service, prompt)
            st.markdown(response)

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("**Ultra Simple Features:**")
st.sidebar.markdown("✅ Fresh session per interaction")
st.sidebar.markdown("✅ Zero memory between chats")
st.sidebar.markdown("✅ Minimal complexity")
st.sidebar.markdown("✅ No conversation history")
st.sidebar.markdown("---")
st.sidebar.markdown("**Stats:**")
st.sidebar.markdown(f"🔢 Interactions: {st.session_state.interaction_count}")
st.sidebar.markdown("💾 Agent memory: None")
st.sidebar.markdown("🔄 Fresh sessions created")
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works:**")
st.sidebar.text("• Each interaction gets new session ID")
st.sidebar.text("• Agent has no memory of previous chats")
st.sidebar.text("• Each question is independent")
st.sidebar.text("• Maximum simplicity achieved!")