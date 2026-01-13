"""
Analysis Agent for LexSpend - General legal spend analysis
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
analysis_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
)

# Optional: Set environment variables for LiteLLM if needed
if OLLAMA_BASE_URL != "http://localhost:11434":
    os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL

# Define the analysis agent
analysis_agent = LlmAgent(
    name="analysis_agent",
    model=analysis_llm,
    instruction=prompt.SYSTEM_PROMPT,
    description=(
        "A specialized agent for general legal spend analysis. "
        "Can identify top law firms by spend, calculate total costs, "
        "identify cost savings opportunities, and analyze spending trends."
    ),
    tools=[
        FileReaderTool,
        DataAnalysisTool,
    ],
)

