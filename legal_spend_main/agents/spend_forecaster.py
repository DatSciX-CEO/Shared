"""
SpendForecaster Sub-Agent - Budget predictions and planning
Pattern: LlmAgent with model= parameter (LexSpend pattern)
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AGENT_MODELS, OLLAMA_BASE_URL
from prompts.analyst_prompts import SPEND_FORECASTER_PROMPT
from tools.forecasting_tools import ForecastSpendTool
from tools.analysis_tools import AnalyzeTrendsTool


def create_spend_forecaster_agent(model_override: str = None) -> LlmAgent:
    """
    Create SpendForecaster sub-agent with configurable model.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or AGENT_MODELS["SpendForecaster"]
    
    # Create LiteLlm instance
    llm = LiteLlm(
        model=f"ollama_chat/{model}",
    )
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    return LlmAgent(
        name="SpendForecaster",
        model=llm,
        instruction=SPEND_FORECASTER_PROMPT,
        description="Specializes in predicting future spend and budget requirements",
        tools=[ForecastSpendTool, AnalyzeTrendsTool],
    )


