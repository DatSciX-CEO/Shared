"""
Main ADK Agent for LexSpend - Legal Spend Analysis
Following Google ADK conventions with LiteLlm and LlmAgent
Orchestrates specialized agents for different analysis tasks
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os

from . import prompt
from .tools.file_reader_tool import FileReaderTool
from .tools.data_analysis_tool import DataAnalysisTool
from .tools.anomaly_detection_tool import AnomalyDetectionTool
from .agents.analysis_agent import analysis_agent
from .agents.ediscovery_agent import ediscovery_agent
from .agents.anomaly_agent import anomaly_agent

# Import config from parent directory
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

# --- Ollama Model Configuration ---
# Use LiteLlm to connect to local Ollama model
# Format: "ollama_chat/{model_name}"
ollama_llm = LiteLlm(
    model=f"ollama_chat/{OLLAMA_MODEL}",
)

# Optional: Set environment variables for LiteLLM if needed
if OLLAMA_BASE_URL != "http://localhost:11434":
    os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL

# Enhanced system prompt for orchestration
orchestration_prompt = f"""{prompt.SYSTEM_PROMPT}

**Agent Orchestration Guidelines:**

You are the main orchestrator for legal spend analysis. You have access to specialized sub-agents and tools:

1. **For General Analysis** (top firms, totals, cost savings, trends):
   - Use the `data_analysis` tool directly, OR
   - Delegate to the analysis_agent when complex multi-step analysis is needed

2. **For eDiscovery-Specific Analysis**:
   - When users ask about document review, privilege review, TAR, or eDiscovery costs:
   - Delegate to the ediscovery_agent for specialized eDiscovery expertise

3. **For Anomaly Detection**:
   - When users want to identify high-risk line items or detect billing anomalies:
   - Use the `anomaly_detection` tool to run GNN-based anomaly detection
   - This will identify items requiring human review (e.g., Partners billing for document review)

4. **For File Operations**:
   - Always use the `file_reader` tool first to load and understand the data structure

**Delegation Strategy:**
- Start by understanding the user's request
- Load data using file_reader if needed
- Choose the appropriate tool or agent based on the analysis type
- Provide clear, actionable insights based on the results
"""

# Define the main agent declaratively, following ADK best practices.
# This agent orchestrates all tools and can delegate to specialized agents.
lexspend_agent = LlmAgent(
    name="lexspend_agent",
    model=ollama_llm,  # Pass the llm object directly
    instruction=orchestration_prompt,
    description=(
        "An expert legal spend analyst that orchestrates analysis of legal spend data from CSV or Excel files. "
        "Can identify top law firms, calculate totals, find cost savings, analyze eDiscovery spend, "
        "and detect anomalies in billing patterns. Delegates to specialized agents when appropriate."
    ),
    tools=[
        FileReaderTool,
        DataAnalysisTool,
        AnomalyDetectionTool,
    ],
    # Note: ADK agents can reference other agents in their context
    # The LLM will be instructed to use appropriate tools and agents
)

# The root_agent is the entry point for the ADK CLI.
# This makes the agent discoverable via: adk run lexspend
root_agent = lexspend_agent

