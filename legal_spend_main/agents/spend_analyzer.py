"""
SpendAnalyzer Sub-Agent - Legal cost analysis and optimization
Pattern: LlmAgent with model= parameter (LexSpend pattern)
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AGENT_MODELS, OLLAMA_BASE_URL
from prompts.analyst_prompts import SPEND_ANALYZER_PROMPT
from tools.analysis_tools import CalculateFirmTotalsTool, IdentifyCostSavingsTool, AnalyzeTrendsTool


def create_spend_analyzer_agent(model_override: str = None) -> LlmAgent:
    """
    Create SpendAnalyzer sub-agent with configurable model.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or AGENT_MODELS["SpendAnalyzer"]
    
    # Create LiteLlm instance
    llm = LiteLlm(
        model=f"ollama_chat/{model}",
    )
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    return LlmAgent(
        name="SpendAnalyzer",
        model=llm,
        instruction=SPEND_ANALYZER_PROMPT,
        description="Specializes in calculating firm totals, cost breakdowns, and spending trends",
        tools=[CalculateFirmTotalsTool, IdentifyCostSavingsTool, AnalyzeTrendsTool],
    )


