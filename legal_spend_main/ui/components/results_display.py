"""
Results Display Component
Displays analysis results and visualizations
"""
import streamlit as st
import sys
import os

# Import storage
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data.storage import ResultsStorage


def render_results_display():
    """
    Render analysis results and session history.
    """
    st.subheader("📊 Analysis Results")
    
    # Initialize storage
    storage = ResultsStorage()
    
    # Get recent sessions
    recent_sessions = storage.get_recent_sessions(limit=10)
    
    if recent_sessions:
        st.caption(f"Found {len(recent_sessions)} recent analysis sessions")
        
        # Session selector
        session_options = [
            f"{s['session_id']} - {s['data_source']} ({s['analysis_date']})"
            for s in recent_sessions
        ]
        
        selected_session_idx = st.selectbox(
            "Select Session",
            range(len(session_options)),
            format_func=lambda i: session_options[i],
            key="session_selector"
        )
        
        if selected_session_idx is not None:
            session = recent_sessions[selected_session_idx]
            
            # Display session details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", session['total_records'])
            with col2:
                st.metric("Total Spend", f"${session['total_spend']:,.2f}")
            with col3:
                st.metric("Data Source", session['data_source_type'].upper())
            
            # Get session results
            results = storage.get_session_results(session['session_id'])
            
            if results:
                st.divider()
                st.caption(f"Analysis Results ({len(results)} items)")
                
                for result in results:
                    with st.expander(f"{result['result_type']} - {result['created_at']}"):
                        st.text(result['result_data'])
            else:
                st.info("No analysis results for this session yet")
    else:
        st.info("No analysis sessions found. Start by uploading data and asking questions!")


