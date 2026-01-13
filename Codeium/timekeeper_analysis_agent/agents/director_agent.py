# Copyright 2025 DatSciX
# Timekeeper Director Agent

"""Main orchestrator agent for timekeeper analysis system."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from prompts import DIRECTOR_PROMPT
from services import get_ollama_model
from config.config import config
from .sub_agents import (
    data_ingestion_agent,
    analysis_coordinator,
    report_generator
)


timekeeper_director = Agent(
    name="timekeeper_director",
    model=get_ollama_model(config.agents.director_model),
    description=(
        "Main orchestrator for timekeeper data analysis in eDiscovery operations. "
        "Coordinates data ingestion, analysis, and reporting to provide comprehensive "
        "insights into productivity, billing integrity, and resource optimization."
    ),
    instruction=DIRECTOR_PROMPT,
    tools=[
        AgentTool(agent=data_ingestion_agent),
        AgentTool(agent=analysis_coordinator),
        AgentTool(agent=report_generator),
    ],
    output_key=config.reporting.output_key,
)


# Export as root_agent for compatibility with ADK patterns
root_agent = timekeeper_director