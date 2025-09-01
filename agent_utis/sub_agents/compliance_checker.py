"""
Compliance Checker Sub-Agent for Agent Utis
Ensures operations align with legal industry best practices
"""

import os
from google.adk.agents import Agent
from google.adk.llms.litellm import LiteLLM

def create_compliance_checker_agent():
    """Create and configure the Compliance Checker sub-agent"""
    
    model_name = os.getenv("AGENT_MODEL", "ollama/mistral:7b")
    llm = LiteLLM(model=model_name, api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"))
    
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
    
    agent = Agent(
        name="ComplianceChecker",
        llm=llm,
        instruction=instruction,
        description="Ensures operations align with legal industry best practices"
    )
    
    return agent