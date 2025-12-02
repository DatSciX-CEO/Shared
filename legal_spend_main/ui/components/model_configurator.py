"""
Model Configurator Component
Allows per-agent model selection from available Ollama models
"""
import streamlit as st
import subprocess
from typing import List


def get_available_ollama_models() -> List[str]:
    """
    Query Ollama for installed models.
    
    Returns:
        List of available model names
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    # Extract model name (first column)
                    model_name = line.split()[0]
                    models.append(model_name)
            
            return models if models else ["mistral:7b", "llama2"]
        else:
            return ["mistral:7b", "llama2", "codellama"]
            
    except Exception as e:
        print(f"Error querying Ollama models: {e}")
        return ["mistral:7b", "llama2", "codellama"]


def render_model_configurator():
    """
    Render per-agent model selection UI in Streamlit sidebar.
    Updates st.session_state.agent_models with selected models.
    """
    st.sidebar.subheader("🤖 Model Selection")
    
    available_models = get_available_ollama_models()
    
    agent_names = [
        "LegalOpsManager",
        "DataAnalyst",
        "SpendAnalyzer",
        "eDiscoverySpecialist",
        "AnomalyDetector",
        "SpendForecaster",
        "ComplianceAuditor"
    ]
    
    # Initialize session state for agent models
    if 'agent_models' not in st.session_state:
        st.session_state.agent_models = {}
    
    with st.sidebar.expander("Configure Agent Models", expanded=False):
        st.caption("Select Ollama models for each agent")
        
        for agent_name in agent_names:
            # Get current selection or default to first model
            default_idx = 0
            if agent_name in st.session_state.agent_models:
                try:
                    default_idx = available_models.index(st.session_state.agent_models[agent_name])
                except ValueError:
                    default_idx = 0
            
            selected = st.selectbox(
                f"{agent_name}",
                options=available_models,
                index=default_idx,
                key=f"model_select_{agent_name}",
                help=f"Select Ollama model for {agent_name}"
            )
            st.session_state.agent_models[agent_name] = selected
        
        # Show summary
        st.divider()
        unique_models = set(st.session_state.agent_models.values())
        st.caption(f"Using {len(unique_models)} unique model(s)")
        
        # Refresh models button
        if st.button("🔄 Refresh Model List", key="refresh_models"):
            st.cache_data.clear()
            st.rerun()


