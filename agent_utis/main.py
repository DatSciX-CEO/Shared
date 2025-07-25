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

from agents import create_agent_system, AgentUtisSystem

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
            st.session_state.agent_system = create_agent_system()
        except Exception as e:
            st.error(f"Failed to initialize AI agents: {e}")
            st.session_state.agent_system = None

def load_example_data() -> pd.DataFrame:
    """Load example CSV data if available"""
    example_path = "data/example_utilization_data.csv"
    if os.path.exists(example_path):
        return pd.read_csv(example_path)
    return None

def validate_csv(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate uploaded CSV data"""
    required_columns = ['expert_name', 'billable_hours', 'total_hours']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    if len(df) == 0:
        return False, "CSV file is empty"
    
    # Check for negative values in numeric columns
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
        date_range = f"{df['date'].min()} to {df['date'].max()}"
        st.sidebar.text(f"Date Range: {date_range}")
    
    # Show data preview
    with st.sidebar.expander("Data Preview"):
        st.dataframe(df.head())

def display_utilization_metrics(metrics: Dict[str, Any]):
    """Display utilization metrics"""
    st.subheader("📈 Utilization Metrics")
    
    if 'error' in metrics:
        st.error(f"Error calculating metrics: {metrics['error']}")
        return
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_util = metrics.get('avg_utilization', 0)
        st.metric("Average Utilization", f"{avg_util:.1f}%", 
                 delta=f"{avg_util - 75:.1f}%" if avg_util else None)
    
    with col2:
        optimal = metrics.get('optimal_range', 0)
        st.metric("Optimal Range (70-80%)", optimal)
    
    with col3:
        over_util = metrics.get('over_utilized', 0)
        st.metric("Over-utilized (>80%)", over_util, 
                 delta=f"-{over_util}" if over_util > 0 else None)
    
    with col4:
        under_util = metrics.get('under_utilized', 0)
        st.metric("Under-utilized (<70%)", under_util,
                 delta=f"-{under_util}" if under_util > 0 else None)
    
    # Display expert analysis if available
    if 'expert_analysis' in metrics:
        st.subheader("🔍 Expert Analysis")
        st.write(metrics['expert_analysis'])

def display_spend_prediction(prediction: Dict[str, Any]):
    """Display spend prediction results"""
    st.subheader("💰 Spend Prediction")
    
    if 'error' in prediction:
        st.error(f"Error in prediction: {prediction['error']}")
        return
    
    if 'predicted_monthly_spend' in prediction:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Predicted Spend", 
                     f"${prediction.get('total_predicted', 0):,.2f}")
            st.metric("Monthly Trend", 
                     f"${prediction.get('historical_trend', 0):,.2f}")
        
        with col2:
            confidence = prediction.get('confidence_level', 'Unknown')
            st.metric("Confidence Level", confidence)
    
    if 'predictive_analysis' in prediction:
        st.subheader("📊 Predictive Analysis")
        st.write(prediction['predictive_analysis'])

def display_compliance_report(report: Dict[str, Any]):
    """Display compliance report"""
    st.subheader("✅ Compliance Report")
    
    if 'error' in report:
        st.error(f"Error in compliance check: {report['error']}")
        return
    
    # Compliance score
    score = report.get('compliance_score', 0)
    st.progress(score / 100)
    st.metric("Compliance Score", f"{score}/100")
    
    # Issues and recommendations
    issues = report.get('issues', [])
    if issues:
        st.subheader("⚠️ Issues Identified")
        for issue in issues:
            st.warning(issue)
    
    recommendations = report.get('recommendations', [])
    if recommendations:
        st.subheader("💡 Recommendations")
        for rec in recommendations:
            st.info(rec)
    
    if 'compliance_analysis' in report:
        st.subheader("🔍 Detailed Analysis")
        st.write(report['compliance_analysis'])

def display_chat_interface():
    """Display chat interface for interactive queries"""
    st.subheader("💬 Ask the Finance Director")
    
    # Display chat history
    for i, (query, response) in enumerate(st.session_state.chat_history):
        with st.expander(f"Query {i+1}: {query[:50]}..."):
            st.write(f"**Q:** {query}")
            st.write(f"**A:** {response}")
    
    # Chat input
    query = st.text_input("Ask a question about your data:", 
                         placeholder="e.g., 'What are the main utilization issues?' or 'Predict Q4 spending'")
    
    if st.button("Ask") and query:
        if st.session_state.agent_system and st.session_state.data is not None:
            with st.spinner("Analyzing your query..."):
                try:
                    response = st.session_state.agent_system.answer_query(
                        query, st.session_state.data, st.session_state.analysis_results
                    )
                    st.session_state.chat_history.append((query, response))
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        else:
            st.warning("Please upload data and ensure AI agents are initialized.")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.title("🤖 Agent Utis")
    st.subtitle("AI-Powered eDiscovery Utilization Analysis")
    st.markdown("---")
    
    # Sidebar for file upload
    st.sidebar.title("📁 Data Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload CSV file with utilization data",
        type=['csv'],
        help="Upload a CSV file with columns: expert_name, billable_hours, total_hours, etc."
    )
    
    # Load example data option
    if st.sidebar.button("Load Example Data"):
        example_data = load_example_data()
        if example_data is not None:
            st.session_state.data = example_data
            st.success("Example data loaded successfully!")
        else:
            st.warning("Example data file not found. Please upload your own CSV file.")
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, message = validate_csv(df)
            
            if is_valid:
                st.session_state.data = df
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                st.session_state.data = None
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            st.session_state.data = None
    
    # Display data and analysis if available
    if st.session_state.data is not None:
        df = st.session_state.data
        display_data_overview(df)
        
        # Run analysis button
        if st.button("🔍 Run Complete Analysis", type="primary"):
            if st.session_state.agent_system:
                with st.spinner("Running comprehensive analysis..."):
                    try:
                        results = st.session_state.agent_system.comprehensive_analysis(df)
                        st.session_state.analysis_results = results
                        st.success("Analysis completed successfully!")
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
            else:
                st.error("AI agents not initialized. Please check Ollama setup.")
        
        # Display analysis results
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Executive Summary
            if 'executive_summary' in results:
                st.subheader("📋 Executive Summary")
                st.write(results['executive_summary'])
                st.markdown("---")
            
            # Detailed sections
            tab1, tab2, tab3, tab4 = st.tabs(["Utilization", "Spend Prediction", "Compliance", "Raw Data"])
            
            with tab1:
                if 'utilization_analysis' in results:
                    display_utilization_metrics(results['utilization_analysis'])
            
            with tab2:
                if 'spend_forecast' in results:
                    display_spend_prediction(results['spend_forecast'])
            
            with tab3:
                if 'compliance_status' in results:
                    display_compliance_report(results['compliance_status'])
            
            with tab4:
                st.subheader("📊 Data Table")
                st.dataframe(df)
        
        # Chat interface
        st.markdown("---")
        display_chat_interface()
    
    else:
        # Welcome message
        st.info("""
        👋 **Welcome to Agent Utis!**
        
        This application helps analyze eDiscovery expert utilization data using AI agents.
        
        **To get started:**
        1. Upload a CSV file with your utilization data
        2. Or click "Load Example Data" to try with sample data
        3. Run the complete analysis to get insights
        4. Ask questions using the chat interface
        
        **Required CSV columns:**
        - `expert_name`: Name of the expert
        - `billable_hours`: Hours billed to clients
        - `total_hours`: Total hours worked
        - Other optional columns: `project`, `cost`, `date`, `hourly_rate`
        """)
    
    # Footer with agent status
    st.markdown("---")
    if st.session_state.agent_system:
        agents_list = st.session_state.agent_system.list_agents()
        st.markdown(f"*Powered by Ollama Mistral 7B and Google ADK | Active Agents: {', '.join(agents_list)}*")
    else:
        st.markdown("*Powered by Ollama Mistral 7B and Google ADK | Status: Agents not initialized*")

if __name__ == "__main__":
    main()