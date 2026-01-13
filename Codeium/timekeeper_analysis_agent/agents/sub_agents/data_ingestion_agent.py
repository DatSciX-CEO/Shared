# Copyright 2025 DatSciX
# Data Ingestion Agent

"""Agent responsible for loading and validating timekeeper data files."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from prompts import DATA_INGESTION_PROMPT
from services import get_ollama_model
from tools import load_timekeeper_file, validate_timekeeper_data


data_ingestion_agent = Agent(
    name="data_ingestion_agent",
    model=get_ollama_model(),
    description=(
        "Loads and validates timekeeper data from CSV, Excel, or Parquet files. "
        "Performs data quality checks, cleaning, and standardization."
    ),
    instruction=DATA_INGESTION_PROMPT,
    tools=[
        FunctionTool(load_timekeeper_file),
        FunctionTool(validate_timekeeper_data),
    ],
    output_key="timekeeper_data",
)