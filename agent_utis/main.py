"""
Agent Utis MVP - Streamlit Application
eDiscovery utilization analysis with AI agents
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
import json

from agents import create_agent_system, FinanceDirector
from utils import (
    validate_data_types, 
    calculate_derived_metrics,
    generate_utilization_insights,
    create_visualization
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Agent Utis - eDiscovery Utilization Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent_system' not in st.session_state:
        try:
            with st.spinner("Initializing AI agents..."):
                st.session_state.agent_system = create_agent_system()
                st.success("AI agents initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize AI agents: {e}")
            st.info("Please ensure Ollama is running with: ollama serve")
            st.session_state.agent_system = None

def load_example_data() -> pd.DataFrame:
    """Load example CSV data"""
    example_path = "data/example_utilization_data.csv"
    if os.path.exists(example_path):
        return pd.read_csv(example_path)
    else:
        # Create example data if file doesn't exist
        example_data = pd.DataFrame({
            'expert_name': ['Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Wilson', 'Lisa Thompson'],
            'role': ['Document Reviewer', 'Legal Analyst', 'Senior Reviewer', 'Document Analyst', 'Legal Tech Specialist'],
            'billable_hours': [152, 180, 140, 120, 165],
            'total_hours': [200, 200, 180, 160, 180],
            'hourly_rate': [125, 150, 175, 100, 200],
            'total_cost': [19000, 27000, 24500, 12000, 33000],
            'date': ['2024-01-31'] * 5
        })
        return example_data

def validate_csv(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate uploaded CSV data"""
    required_columns = ['expert_name', 'billable_hours', 'total_hours']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    if len(df) == 0:
        return False, "CSV file is empty"
    
    # Check for negative values
    numeric_cols = ['billable_hours', 'total_hours']
    for col in numeric_cols:
        if col in df.columns and (df[col] < 0).any():
            return False, f"Negative values found in {col}"
    
    return True, "Valid CSV data"

def display_data_overview(df: pd.DataFrame):
    """Display data overview in sidebar"""
    st.sidebar.subheader("📊 Data Overview")
    st.sidebar.metric("Total Records", len(df))
    st.sidebar.metric("Columns", len(df.columns))
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"
        st.sidebar.text(f"Date Range: {date_range}")
    
    with st.sidebar.expander("Data Preview"):
        st.dataframe(df.head())

def display_analysis_results(results: Dict[str, Any]):
    """Display comprehensive analysis results"""
    
    # Executive Summary
    if 'executive_summary' in results and results['executive_summary']:
        st.subheader("📋 Executive Summary")
        st.write(results['executive_summary'])
        st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Utilization", "💰 Spend Forecast", "✅ Compliance", "📊 Data Overview"])
    
    with tab1:
        util_data = results.get('utilization_analysis', {})
        if 'error' not in util_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_util = util_data.get('avg_utilization', 0)
                st.metric("Average Utilization", f"{avg_util:.1f}%", 
                         delta=f"{avg_util - 75:.1f}%" if avg_util else None)
            
            with col2:
                optimal = util_data.get('optimal_range', 0)
                st.metric("In Optimal Range", optimal)
            
            with col3:
                over_util = util_data.get('over_utilized', 0)
                st.metric("Over-utilized", over_util,
                         delta_color="inverse" if over_util > 0 else "normal")
            
            with col4:
                under_util = util_data.get('under_utilized', 0)
                st.metric("Under-utilized", under_util,
                         delta_color="inverse" if under_util > 0 else "normal")
            
            if 'expert_analysis' in util_data:
                st.subheader("Expert Analysis")
                st.write(util_data['expert_analysis'])
            
            # Role analysis chart
            if 'role_analysis' in util_data and st.session_state.data is not None:
                fig = create_visualization(st.session_state.data, 'role_comparison')
                st.pyplot(fig)
        else:
            st.error(f"Error in utilization analysis: {util_data['error']}")
    
    with tab2:
        spend_data = results.get('spend_forecast', {})
        if 'error' not in spend_data:
            if 'predicted_monthly_spend' in spend_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Predicted Spend", 
                             f"${spend_data.get('total_predicted', 0):,.2f}")
                    st.metric("Monthly Trend", 
                             f"${spend_data.get('historical_trend', 0):,.2f}")
                
                with col2:
                    confidence = spend_data.get('confidence_level', 'Unknown')
                    st.metric("Confidence Level", confidence)
                
                if 'analysis' in spend_data:
                    st.subheader("Predictive Analysis")
                    st.write(spend_data['analysis'])
            else:
                st.info(spend_data.get('error', 'No prediction available'))
        else:
            st.error(f"Error in spend forecast: {spend_data['error']}")
    
    with tab3:
        compliance_data = results.get('compliance_status', {})
        if 'error' not in compliance_data:
            score = compliance_data.get('compliance_percentage', 0)
            st.progress(score / 100)
            st.metric("Compliance Score", f"{score:.0f}%")
            
            issues = compliance_data.get('issues', [])
            if issues:
                st.subheader("⚠️ Issues Identified")
                for issue in issues:
                    st.warning(issue)
            
            recommendations = compliance_data.get('recommendations', [])
            if recommendations:
                st.subheader("💡 Recommendations")
                for rec in recommendations:
                    st.info(rec)
            
            if 'analysis' in compliance_data:
                st.subheader("Compliance Analysis")
                st.write(compliance_data['analysis'])
        else:
            st.error(f"Error in compliance check: {compliance_data['error']}")
    
    with tab4:
        data_overview = results.get('data_overview', {})
        if 'error' not in data_overview:
            st.json(data_overview)
        else:
            st.error(f"Error in data overview: {data_overview['error']}")

def display_chat_interface():
    """Display chat interface for interactive queries"""
    st.subheader("💬 Ask the Finance Director")
    
    # Display chat history
    for i, (query, response) in enumerate(st.session_state.chat_history):
        with st.expander(f"Q{i+1}: {query[:50]}...", expanded=(i == len(st.session_state.chat_history) - 1)):
            st.write(f"**Question:** {query}")
            st.write(f"**Answer:** {response}")
    
    # Chat input
    query = st.text_input("Ask a question about your data:", 
                         placeholder="e.g., 'What are the main utilization issues?' or 'Which experts need attention?'",
                         key="chat_input")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🤖 Ask", type="primary") and query:
            if st.session_state.agent_system and st.session_state.data is not None:
                with st.spinner("Analyzing your query..."):
                    try:
                        response = st.session_state.agent_system.answer_query(
                            query, 
                            st.session_state.data,
                            st.session_state.analysis_results
                        )
                        st.session_state.chat_history.append((query, response))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing query: {e}")
            else:
                st.warning("Please upload data and ensure AI agents are initialized.")
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.title("🤖 Agent Utis")
    st.markdown("**AI-Powered eDiscovery Utilization Analysis** | Local LLM Processing with Ollama")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📁 Data Management")
    
    # File uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Required: expert_name, billable_hours, total_hours"
    )
    
    # Load example data
    if st.sidebar.button("📋 Load Example Data"):
        example_data = load_example_data()
        st.session_state.data = example_data
        st.success("Example data loaded!")
        st.rerun()
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, message = validate_csv(df)
            
            if is_valid:
                # Validate and prepare data
                df = validate_data_types(df)
                df = calculate_derived_metrics(df)
                
                st.session_state.data = df
                st.sidebar.success(f"✅ {message}")
            else:
                st.sidebar.error(f"❌ {message}")
                st.session_state.data = None
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")
            st.session_state.data = None
    
    # Main content area
    if st.session_state.data is not None:
        df = st.session_state.data
        display_data_overview(df)
        
        # Analysis controls
        col1, col2, col3 = st.columns([2, 2, 6])
        
        with col1:
            if st.button("🔍 Run Analysis", type="primary"):
                if st.session_state.agent_system:
                    with st.spinner("Running comprehensive analysis..."):
                        try:
                            results = st.session_state.agent_system.comprehensive_analysis(df)
                            st.session_state.analysis_results = results
                            st.success("Analysis completed!")
                        except Exception as e:
                            st.error(f"Analysis error: {e}")
                else:
                    st.error("AI agents not initialized")
        
        with col2:
            if st.button("📥 Export Results"):
                if st.session_state.analysis_results:
                    results_json = json.dumps(st.session_state.analysis_results, default=str, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=results_json,
                        file_name=f"agent_utis_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        # Display results
        if st.session_state.analysis_results:
            display_analysis_results(st.session_state.analysis_results)
        
        # Chat interface
        st.markdown("---")
        display_chat_interface()
        
    else:
        # Welcome screen
        st.info("""
        ### 👋 Welcome to Agent Utis!
        
        This application analyzes eDiscovery expert utilization using local AI agents.
        
        **Getting Started:**
        1. Ensure Ollama is running: `ollama serve`
        2. Upload your CSV file or load example data
        3. Run analysis to get comprehensive insights
        4. Ask questions using the chat interface
        
        **Required CSV columns:**
        - `expert_name`: Expert identifier
        - `billable_hours`: Hours billed to clients  
        - `total_hours`: Total hours worked
        
        **Optional columns:**
        - `role`, `project_name`, `date`, `hourly_rate`, `total_cost`
        """)
        
        # System status
        if st.session_state.agent_system:
            st.success("✅ AI Agents Ready")
        else:
            st.error("❌ AI Agents Not Initialized")
            if st.button("🔄 Retry Initialization"):
                st.session_state.clear()
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by Ollama + Mistral:7b | Running 100% Locally*")

if __name__ == "__main__":
    main()