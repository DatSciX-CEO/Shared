"""
Main Manager Agent for Legal Spend Analysis
Uses Agent class with sub_agents for hierarchical orchestration
Pattern: Agent class (agent_utis) with llm= parameter and sub_agents
"""
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # Unified import pattern across all agents
import os

from .config import AGENT_MODELS, OLLAMA_BASE_URL
from .agents.data_analyst import create_data_analyst_agent
from .agents.spend_analyzer import create_spend_analyzer_agent
from .agents.ediscovery_specialist import create_ediscovery_specialist_agent
from .agents.anomaly_detector import create_anomaly_detector_agent
from .agents.spend_forecaster import create_spend_forecaster_agent
from .agents.compliance_auditor import create_compliance_auditor_agent
from .prompts.manager_prompt import MANAGER_PROMPT
from .tools.data_ingestion_tools import ReadCsvTool, ReadParquetTool


def create_legal_ops_manager(model_overrides: dict = None) -> Agent:
    """
    Create the Manager Agent with all sub-agents.
    Uses Agent class (not LlmAgent) to support sub_agents parameter.
    
    Args:
        model_overrides: Dict mapping agent names to model names
        
    Returns:
        Configured Agent instance with hierarchical sub-agents
    """
    model_overrides = model_overrides or {}
    
    # Create LLM for manager
    manager_model = model_overrides.get("LegalOpsManager") or AGENT_MODELS["LegalOpsManager"]
    llm = LiteLlm(
        model=f"ollama_chat/{manager_model}",
    )

    # Set environment variable if non-default base URL
    if OLLAMA_BASE_URL != "http://localhost:11434":
        os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL
    
    # Initialize all sub-agents with model overrides
    sub_agents = [
        create_data_analyst_agent(model_overrides.get("DataAnalyst")),
        create_spend_analyzer_agent(model_overrides.get("SpendAnalyzer")),
        create_ediscovery_specialist_agent(model_overrides.get("eDiscoverySpecialist")),
        create_anomaly_detector_agent(model_overrides.get("AnomalyDetector")),
        create_spend_forecaster_agent(model_overrides.get("SpendForecaster")),
        create_compliance_auditor_agent(model_overrides.get("ComplianceAuditor")),
    ]
    
    print("✅ Creating Legal Operations Manager with 6 sub-agents")
    print(f"   Manager Model: {manager_model}")
    print(f"   Sub-agents: DataAnalyst, SpendAnalyzer, eDiscoverySpecialist, AnomalyDetector, SpendForecaster, ComplianceAuditor")
    
    return Agent(
        name="LegalOpsManager",
        llm=llm,  # Agent class uses 'llm=' parameter
        instruction=MANAGER_PROMPT,
        description="Orchestrates legal spend analysis by delegating to specialized sub-agents",
        tools=[ReadCsvTool, ReadParquetTool],  # Manager has high-level tools
        sub_agents=sub_agents,  # Register all sub-agents for hierarchical orchestration
    )


# REQUIRED: root_agent variable for ADK CLI discovery
# This makes the agent discoverable via: adk run legal_spend_main
root_agent = create_legal_ops_manager()

print("✅ ADK Agent 'LegalOpsManager' (root_agent) defined and ready")


