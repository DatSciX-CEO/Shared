"""
eDiscoverySpecialist Sub-Agent - Document review and eDiscovery cost analysis
Pattern: LlmAgent with model= parameter (LexSpend pattern)
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AGENT_MODELS, OLLAMA_BASE_URL
from prompts.analyst_prompts import EDISCOVERY_SPECIALIST_PROMPT
from tools.analysis_tools import CalculateFirmTotalsTool, IdentifyCostSavingsTool
from tools.anomaly_tools import DetectAnomaliesTool


def create_ediscovery_specialist_agent(model_override: str = None) -> LlmAgent:
    """
    Create eDiscoverySpecialist sub-agent with configurable model.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or AGENT_MODELS["eDiscoverySpecialist"]
    
    # Create LiteLlm instance
    llm = LiteLlm(
        model=f"ollama_chat/{model}",
    )
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    return LlmAgent(
        name="eDiscoverySpecialist",
        model=llm,
        instruction=EDISCOVERY_SPECIALIST_PROMPT,
        description="Specializes in analyzing document review and eDiscovery-related costs",
        tools=[CalculateFirmTotalsTool, IdentifyCostSavingsTool, DetectAnomaliesTool],
    )


