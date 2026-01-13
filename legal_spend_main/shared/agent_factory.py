"""
Agent Factory
Reusable functions for creating agents with custom configurations
Can be imported by other applications for integration
"""
from typing import Dict, Optional
import sys
import os

# Import agent creation functions
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from agent import create_legal_ops_manager
from agents.data_analyst import create_data_analyst_agent
from agents.spend_analyzer import create_spend_analyzer_agent
from agents.ediscovery_specialist import create_ediscovery_specialist_agent
from agents.anomaly_detector import create_anomaly_detector_agent
from agents.spend_forecaster import create_spend_forecaster_agent
from agents.compliance_auditor import create_compliance_auditor_agent


def create_agent_with_config(
    agent_type: str = "manager",
    model_override: Optional[str] = None,
    model_overrides: Optional[Dict[str, str]] = None
) -> object:
    """
    Factory function to create agents with custom configurations.
    
    Args:
        agent_type: Type of agent to create. Options:
            - "manager": Full hierarchical system with all sub-agents
            - "data_analyst": Data loading and validation agent
            - "spend_analyzer": Spend analysis agent
            - "ediscovery": eDiscovery specialist agent
            - "anomaly": Anomaly detection agent
            - "forecaster": Spend forecasting agent
            - "compliance": Compliance auditing agent
        model_override: Model name to use (for single agents)
        model_overrides: Dict of agent names to models (for manager)
        
    Returns:
        Configured agent instance
        
    Example:
        >>> # Create full hierarchical system
        >>> manager = create_agent_with_config("manager")
        >>> 
        >>> # Create single specialized agent
        >>> analyst = create_agent_with_config("data_analyst", model_override="llama2")
        >>> 
        >>> # Create manager with custom models
        >>> models = {"LegalOpsManager": "mistral:7b", "DataAnalyst": "llama2"}
        >>> manager = create_agent_with_config("manager", model_overrides=models)
    """
    agent_creators = {
        "manager": lambda: create_legal_ops_manager(model_overrides),
        "data_analyst": lambda: create_data_analyst_agent(model_override),
        "spend_analyzer": lambda: create_spend_analyzer_agent(model_override),
        "ediscovery": lambda: create_ediscovery_specialist_agent(model_override),
        "anomaly": lambda: create_anomaly_detector_agent(model_override),
        "forecaster": lambda: create_spend_forecaster_agent(model_override),
        "compliance": lambda: create_compliance_auditor_agent(model_override),
    }
    
    if agent_type not in agent_creators:
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Valid options: {', '.join(agent_creators.keys())}"
        )
    
    return agent_creators[agent_type]()


def get_available_agent_types() -> Dict[str, str]:
    """
    Get a dictionary of available agent types and their descriptions.
    
    Returns:
        Dict mapping agent type to description
    """
    return {
        "manager": "Full hierarchical system with all sub-agents",
        "data_analyst": "Data loading and validation specialist",
        "spend_analyzer": "Legal spend analysis and cost optimization",
        "ediscovery": "eDiscovery and document review cost analysis",
        "anomaly": "Unusual billing pattern detection",
        "forecaster": "Budget predictions and spend forecasting",
        "compliance": "Policy violations and billing guideline checks",
    }


