"""
Spend Predictor Sub-Agent for Agent Utis
Forecasts future spending based on historical data analysis
"""

import os
from google.adk.agents import Agent
from google.adk.llms.litellm import LiteLLM

def create_spend_predictor_agent():
    """Create and configure the Spend Predictor sub-agent"""
    
    model_name = os.getenv("AGENT_MODEL", "ollama/mistral:7b")
    llm = LiteLLM(model=model_name, api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"))
    
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
    
    agent = Agent(
        name="SpendPredictor",
        llm=llm,
        instruction=instruction,
        description="Forecasts future spending based on historical data analysis"
    )
    
    return agent