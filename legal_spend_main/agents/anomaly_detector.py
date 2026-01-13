"""
AnomalyDetector Sub-Agent - Unusual billing pattern detection
Pattern: LlmAgent with model= parameter (LexSpend pattern)
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AGENT_MODELS, OLLAMA_BASE_URL
from prompts.analyst_prompts import ANOMALY_DETECTOR_PROMPT
from tools.anomaly_tools import DetectAnomaliesTool


def create_anomaly_detector_agent(model_override: str = None) -> LlmAgent:
    """
    Create AnomalyDetector sub-agent with configurable model.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or AGENT_MODELS["AnomalyDetector"]
    
    # Create LiteLlm instance
    llm = LiteLlm(
        model=f"ollama_chat/{model}",
    )
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    return LlmAgent(
        name="AnomalyDetector",
        model=llm,
        instruction=ANOMALY_DETECTOR_PROMPT,
        description="Specializes in identifying unusual billing patterns and compliance issues",
        tools=[DetectAnomaliesTool],
    )


