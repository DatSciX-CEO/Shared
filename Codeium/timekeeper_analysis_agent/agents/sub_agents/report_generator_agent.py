# Copyright 2025 DatSciX
# Report Generator Agent

"""Agent responsible for synthesizing findings into comprehensive reports."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from prompts import REPORT_GENERATOR_PROMPT
from services import get_ollama_model
from tools import export_report


report_generator = Agent(
    name="report_generator",
    model=get_ollama_model(),
    description=(
        "Synthesizes analysis findings from multiple agents into comprehensive, "
        "actionable reports with visualizations and prioritized recommendations."
    ),
    instruction=REPORT_GENERATOR_PROMPT,
    tools=[
        FunctionTool(export_report),
    ],
    output_key="final_report",
)