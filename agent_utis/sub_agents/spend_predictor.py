"""
Spend Predictor Sub-Agent for Agent Utis
Forecasts future spending based on historical data analysis
"""

import os
from google.adk.agents import Agent

def create_spend_predictor_agent():
    """Create and configure the Spend Predictor sub-agent"""
    
    model = os.getenv("AGENT_MODEL", "gemini-2.0-flash-exp")
    
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
        model=model,
        instruction=instruction,
        description="Forecasts future spending based on historical data analysis"
    )
    
    return agent