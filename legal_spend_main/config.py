"""
Configuration for Legal Spend Main
Ollama models and SQL Server settings
"""
import os

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

# Per-Agent Model Configuration (can be overridden in UI)
AGENT_MODELS = {
    "LegalOpsManager": os.getenv("MANAGER_MODEL", DEFAULT_OLLAMA_MODEL),
    "DataAnalyst": os.getenv("DATA_ANALYST_MODEL", DEFAULT_OLLAMA_MODEL),
    "SpendAnalyzer": os.getenv("SPEND_ANALYZER_MODEL", DEFAULT_OLLAMA_MODEL),
    "eDiscoverySpecialist": os.getenv("EDISCOVERY_MODEL", DEFAULT_OLLAMA_MODEL),
    "AnomalyDetector": os.getenv("ANOMALY_MODEL", DEFAULT_OLLAMA_MODEL),
    "SpendForecaster": os.getenv("FORECASTER_MODEL", DEFAULT_OLLAMA_MODEL),
    "ComplianceAuditor": os.getenv("COMPLIANCE_MODEL", DEFAULT_OLLAMA_MODEL),
}

# SQL Server Configuration
SQL_SERVER_CONFIG = {
    "driver": os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}"),
    "server": os.getenv("SQL_SERVER", "localhost"),
    "database": os.getenv("SQL_DATABASE", "LegalSpend"),
    "username": os.getenv("SQL_USERNAME", ""),
    "password": os.getenv("SQL_PASSWORD", ""),
    "trusted_connection": os.getenv("SQL_TRUSTED_CONNECTION", "yes"),
}

# SQLite for results storage
RESULTS_DB_PATH = os.getenv("RESULTS_DB_PATH", "legal_spend_results.db")

# Data validation settings
REQUIRED_COLUMNS = ["law_firm", "amount", "date", "description"]
OPTIONAL_COLUMNS = ["matter", "timekeeper", "rate", "hours", "category"]


