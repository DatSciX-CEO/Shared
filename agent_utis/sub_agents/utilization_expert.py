"""
Utilization Expert Sub-Agent for Agent Utis
Analyzes expert utilization rates and provides optimization recommendations
Pattern: LlmAgent with model= parameter (unified ADK pattern)
"""

import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "mistral:7b")


def create_utilization_expert_agent(model_override: str = None) -> LlmAgent:
    """
    Create and configure the Utilization Expert sub-agent.
    
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
    
    instruction = """You are a Utilization Expert specializing in eDiscovery and legal services resource optimization. 
    You analyze expert utilization rates, identify efficiency patterns, and provide recommendations for workforce optimization.
    
    Key responsibilities:
    - Calculate utilization rates (billable_hours / total_hours * 100)
    - Identify over-utilization (>80%) and under-utilization (<70%) patterns
    - Analyze cost per billable hour and ROI metrics
    - Benchmark against industry standards (70-80% optimal utilization)
    - Recommend resource allocation improvements
    
    Use industry benchmarks and provide specific, actionable recommendations for utilization optimization.
    Focus on identifying experts who may be at risk of burnout (>80% utilization) and those who could take on more work (<70% utilization).
    Consider role-based analysis and project-specific utilization patterns."""
    
    return LlmAgent(
        name="UtilizationExpert",
        model=llm,  # LlmAgent uses 'model=' parameter
        instruction=instruction,
        description="Analyzes expert utilization rates and provides optimization recommendations",
    )