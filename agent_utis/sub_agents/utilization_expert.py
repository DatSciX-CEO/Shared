"""
Utilization Expert Sub-Agent for Agent Utis
Analyzes expert utilization rates and provides optimization recommendations
"""

import os
from google.adk.agents import Agent
from google.adk.llms.litellm import LiteLLM

def create_utilization_expert_agent():
    """Create and configure the Utilization Expert sub-agent"""
    
    model_name = os.getenv("AGENT_MODEL", "ollama/mistral:7b")
    llm = LiteLLM(model=model_name, api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"))
    
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
    
    agent = Agent(
        name="UtilizationExpert",
        llm=llm,
        instruction=instruction,
        description="Analyzes expert utilization rates and provides optimization recommendations"
    )
    
    return agent