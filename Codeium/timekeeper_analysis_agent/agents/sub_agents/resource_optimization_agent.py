# Copyright 2025 DatSciX
# Resource Optimization Agent

"""Agent specialized in resource allocation and optimization recommendations."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from prompts import RESOURCE_OPTIMIZATION_PROMPT
from services import get_ollama_model
from tools import calculate_statistics


resource_optimizer = Agent(
    name="resource_optimizer",
    model=get_ollama_model(),
    description=(
        "Analyzes resource allocation patterns and recommends optimization strategies "
        "to maximize utilization, reduce bench time, and improve efficiency."
    ),
    instruction=RESOURCE_OPTIMIZATION_PROMPT,
    tools=[
        FunctionTool(calculate_statistics),
    ],
    output_key="resource_optimization_analysis",
)