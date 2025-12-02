"""Sub-agents for legal spend analysis"""
from .data_analyst import create_data_analyst_agent
from .spend_analyzer import create_spend_analyzer_agent
from .ediscovery_specialist import create_ediscovery_specialist_agent
from .anomaly_detector import create_anomaly_detector_agent
from .spend_forecaster import create_spend_forecaster_agent
from .compliance_auditor import create_compliance_auditor_agent

__all__ = [
    "create_data_analyst_agent",
    "create_spend_analyzer_agent",
    "create_ediscovery_specialist_agent",
    "create_anomaly_detector_agent",
    "create_spend_forecaster_agent",
    "create_compliance_auditor_agent",
]


