"""
Data Analyst Sub-Agent for Agent Utis
Specializes in CSV data analysis and validation for eDiscovery operations
Pattern: LlmAgent with model= parameter (unified ADK pattern)
"""

import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "mistral:7b")


def create_data_analyst_agent(model_override: str = None) -> LlmAgent:
    """
    Create and configure the Data Analyst sub-agent.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or DEFAULT_MODEL
    
    # Create LiteLlm instance with ollama_chat prefix
    llm = LiteLlm(model=f"ollama_chat/{model}")
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    instruction = """You are a Data Analyst specializing in eDiscovery and legal services data analysis. 
    Your expertise includes processing CSV data containing expert utilization metrics, validating data quality, 
    and performing statistical analysis on legal operations data.
    
    Key responsibilities:
    - Process and validate CSV data uploads
    - Identify data quality issues and patterns
    - Perform initial statistical analysis
    - Provide data insights to support decision-making
    
    Focus on accuracy, data integrity, and clear communication of findings. Always validate data before analysis.
    When analyzing data, provide specific insights about data completeness, patterns, and any anomalies detected."""
    
    return LlmAgent(
        name="DataAnalyst",
        model=llm,  # LlmAgent uses 'model=' parameter
        instruction=instruction,
        description="Specializes in CSV data analysis and validation for eDiscovery operations",
    )