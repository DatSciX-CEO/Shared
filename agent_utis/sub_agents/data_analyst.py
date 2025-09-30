"""
Data Analyst Sub-Agent for Agent Utis
Specializes in CSV data analysis and validation for eDiscovery operations
"""

import os
from google.adk.agents import Agent
from google.adk.llms.litellm import LiteLLM

def create_data_analyst_agent():
    """Create and configure the Data Analyst sub-agent"""
    
    model_name = os.getenv("AGENT_MODEL", "ollama/mistral:7b")
    llm = LiteLLM(model=model_name, api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"))
    
    instruction = """You are a Data Analyst specializing in eDiscovery and legal services data analysis. 
    Your expertise includes processing CSV data containing expert utilization metrics, validating data quality, 
    and performing statistical analysis on legal operations data.
    
    Key responsibilities:
    - Process and validate CSV data uploads
    - Identify data quality issues and patterns
    - Perform initial statistical analysis
    - Provide data insights to support decision-making
    
    Focus on accuracy, data integrity, and clear communication of findings. Always validate data before analysis.
    When analyzing data, provide specific insights about data completeness, patterns, and any anomalies detected."""
    
    agent = Agent(
        name="DataAnalyst",
        llm=llm,
        instruction=instruction,
        description="Specializes in CSV data analysis and validation for eDiscovery operations"
    )
    
    return agent