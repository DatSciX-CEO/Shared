"""
Spend Predictor Sub-Agent for Agent Utis
Forecasts future spending based on historical data analysis
Pattern: LlmAgent with model= parameter (unified ADK pattern)
"""

import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "mistral:7b")


def create_spend_predictor_agent(model_override: str = None) -> LlmAgent:
    """
    Create and configure the Spend Predictor sub-agent.
    
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
    
    instruction = """You are a Spend Predictor for legal and eDiscovery services with expertise in financial forecasting. 
    You analyze historical spending patterns and predict future costs using statistical methods.
    
    Key responsibilities:
    - Analyze historical spending trends
    - Forecast future spending using regression analysis
    - Identify cost drivers and budget optimization opportunities
    - Provide confidence intervals and risk assessments
    - Recommend budget allocation strategies
    
    Focus on accuracy in predictions and clear communication of forecast assumptions and limitations.
    When making predictions, always explain the methodology used, confidence level, and factors that could impact accuracy.
    Consider seasonal variations, project types, and expert roles in your analysis."""
    
    return LlmAgent(
        name="SpendPredictor",
        model=llm,  # LlmAgent uses 'model=' parameter
        instruction=instruction,
        description="Forecasts future spending based on historical data analysis",
    )