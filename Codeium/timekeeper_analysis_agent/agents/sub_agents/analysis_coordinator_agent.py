# Copyright 2025 DatSciX
# Analysis Coordinator Agent

"""Agent responsible for coordinating specialized analysis sub-agents."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from prompts import ANALYSIS_COORDINATOR_PROMPT
from services import get_ollama_model
from .productivity_analyst_agent import productivity_analyst
from .billing_anomaly_detector_agent import billing_anomaly_detector
from .resource_optimization_agent import resource_optimizer


analysis_coordinator = Agent(
    name="analysis_coordinator",
    model=get_ollama_model(),
    description=(
        "Coordinates specialized analysis agents to provide comprehensive insights "
        "into timekeeper productivity, billing patterns, and resource optimization."
    ),
    instruction=ANALYSIS_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=productivity_analyst),
        AgentTool(agent=billing_anomaly_detector),
        AgentTool(agent=resource_optimizer),
    ],
    output_key="coordinated_analysis",
)