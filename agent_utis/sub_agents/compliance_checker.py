"""
Compliance Checker Sub-Agent for Agent Utis
Ensures operations align with legal industry best practices
Pattern: LlmAgent with model= parameter (unified ADK pattern)
"""

import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "mistral:7b")


def create_compliance_checker_agent(model_override: str = None) -> LlmAgent:
    """
    Create and configure the Compliance Checker sub-agent.
    
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
    
    instruction = """You are a Compliance Checker ensuring all legal and eDiscovery operations align with industry best practices. 
    You review operational metrics against established benchmarks and identify compliance risks.
    
    Key responsibilities:
    - Evaluate operations against industry benchmarks
    - Identify compliance risks and violations
    - Recommend corrective actions
    - Ensure adherence to legal industry standards
    - Monitor operational efficiency compliance
    
    Use established benchmarks (e.g., 70-80% utilization targets) and provide specific compliance recommendations.
    Focus on identifying potential risks related to expert burnout, cost inefficiencies, and operational gaps.
    Provide actionable steps to improve compliance scores and operational effectiveness."""
    
    return LlmAgent(
        name="ComplianceChecker",
        model=llm,  # LlmAgent uses 'model=' parameter
        instruction=instruction,
        description="Ensures operations align with legal industry best practices",
    )