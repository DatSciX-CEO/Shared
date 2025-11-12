"""
eDiscovery Agent for LexSpend - Specialized eDiscovery spend analysis
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from .. import prompt
from ..tools.file_reader_tool import FileReaderTool
from ..tools.data_analysis_tool import DataAnalysisTool

# Create LiteLlm instance for this agent
ediscovery_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
)

# Optional: Set environment variables for LiteLLM if needed
if OLLAMA_BASE_URL != "http://localhost:11434":
    os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL

# Define the eDiscovery agent
ediscovery_agent = LlmAgent(
    name="ediscovery_agent",
    model=ediscovery_llm,
    instruction=prompt.EDISCOVERY_PROMPT,
    description=(
        "A specialized agent for eDiscovery spend analysis. "
        "Identifies eDiscovery-related line items, analyzes document review costs, "
        "evaluates privilege review expenditures, and assesses technology-assisted review costs."
    ),
    tools=[
        FileReaderTool,
        DataAnalysisTool,
    ],
)

