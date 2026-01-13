"""
Agent Chat Component
Renders the chat interface for interacting with agents
"""
import streamlit as st


def render_agent_chat():
    """
    Render the chat interface for agent interactions.
    Displays chat history and input field.
    """
    st.subheader("💬 Chat with Legal Ops Manager")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input is handled in main app
    # This component just renders the history


