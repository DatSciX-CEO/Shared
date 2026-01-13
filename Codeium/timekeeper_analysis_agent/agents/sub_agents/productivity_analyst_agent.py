# Copyright 2025 DatSciX
# Productivity Analyst Agent

"""Agent specialized in analyzing timekeeper productivity metrics."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from prompts import PRODUCTIVITY_ANALYST_PROMPT
from services import get_ollama_model
from tools import calculate_statistics


productivity_analyst = Agent(
    name="productivity_analyst",
    model=get_ollama_model(),
    description=(
        "Analyzes timekeeper productivity metrics including utilization rates, "
        "billable percentages, efficiency gaps, and performance trends."
    ),
    instruction=PRODUCTIVITY_ANALYST_PROMPT,
    tools=[
        FunctionTool(calculate_statistics),
    ],
    output_key="productivity_analysis",
)