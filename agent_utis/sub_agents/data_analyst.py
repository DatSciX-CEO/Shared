"""
Data Analyst Sub-Agent for Agent Utis
Specializes in CSV data analysis and validation for eDiscovery operations
"""

import os
from google.adk.agents import Agent

def create_data_analyst_agent():
    """Create and configure the Data Analyst sub-agent"""
    
    model = os.getenv("AGENT_MODEL", "gemini-2.0-flash-exp")
    
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
        model=model,
        instruction=instruction,
        description="Specializes in CSV data analysis and validation for eDiscovery operations"
    )
    
    return agent