"""
DataAnalyst Sub-Agent - Data loading and validation
Pattern: LlmAgent with model= parameter (LexSpend pattern)
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import sys

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AGENT_MODELS, OLLAMA_BASE_URL
from prompts.analyst_prompts import DATA_ANALYST_PROMPT
from tools.data_ingestion_tools import ReadCsvTool, ReadParquetTool, ReadSqlServerTool, ListSqlTablesTool


def create_data_analyst_agent(model_override: str = None) -> LlmAgent:
    """
    Create DataAnalyst sub-agent with configurable model.
    
    Args:
        model_override: Optional model name to override default
        
    Returns:
        Configured LlmAgent instance
    """
    model = model_override or AGENT_MODELS["DataAnalyst"]
    
    # Create LiteLlm instance
    llm = LiteLlm(
        model=f"ollama_chat/{model}",
    )
    
    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    return LlmAgent(
        name="DataAnalyst",
        model=llm,  # LlmAgent uses 'model=' parameter
        instruction=DATA_ANALYST_PROMPT,
        description="Specializes in loading and validating legal spend data from CSV, Parquet, or SQL Server",
        tools=[ReadCsvTool, ReadParquetTool, ReadSqlServerTool, ListSqlTablesTool],
    )


