"""
Anomaly Agent for LexSpend - GNN-based anomaly detection for document review
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
from ..tools.anomaly_detection_tool import AnomalyDetectionTool

# Create LiteLlm instance for this agent
anomaly_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
)

# Optional: Set environment variables for LiteLLM if needed
if OLLAMA_BASE_URL != "http://localhost:11434":
    os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL

# Define the anomaly detection agent
anomaly_agent = LlmAgent(
    name="anomaly_agent",
    model=anomaly_llm,
    instruction=prompt.ANOMALY_PROMPT,
    description=(
        "A specialized agent for anomaly detection in legal spend data. "
        "Uses Graph Neural Networks to identify line items that require human review, "
        "especially document review activities billed by inappropriate timekeepers or at unusual rates."
    ),
    tools=[
        FileReaderTool,
        AnomalyDetectionTool,
    ],
)

