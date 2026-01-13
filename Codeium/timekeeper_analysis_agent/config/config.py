
# Copyright 2025 DatSciX
# Configuration Loader

"""
Loads and validates configuration from YAML files using Pydantic.
Based on official Google ADK and ClaimsAssistX patterns.
"""

import yaml
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional

# --- Pydantic Models for Validation ---

class OllamaConfig(BaseModel):
    base_url: HttpUrl
    provider: str
    default_model: str
    timeout: int
    max_retries: int

class AgentsConfig(BaseModel):
    director_model: str
    worker_model: str
    max_analysis_iterations: int

class DataConfig(BaseModel):
    supported_formats: List[str]
    max_file_size_mb: int
    chunk_size_rows: int
    required_columns: List[str]
    optional_columns: List[str]

class AnalysisConfig(BaseModel):
    productivity: Dict[str, Any]
    billing: Dict[str, Any]
    resource: Dict[str, Any]

class ReportingConfig(BaseModel):
    formats: List[str]
    include_visualizations: bool
    summary_length: str
    output_key: str = "final_report" # Added from director_agent

class UIConfig(BaseModel):
    streamlit: Dict[str, Any]
    adk_web: Dict[str, Any]

class LoggingConfig(BaseModel):
    level: str
    file: str
    format: str

class SessionConfig(BaseModel):
    backend: str
    timeout_minutes: int
    max_sessions_per_user: int

class MainConfig(BaseModel):
    ollama: OllamaConfig
    agents: AgentsConfig
    data: DataConfig
    analysis: AnalysisConfig
    reporting: ReportingConfig
    ui: UIConfig
    logging: LoggingConfig
    session: SessionConfig

class ModelInfo(BaseModel):
    parameters: str
    context_length: int
    capabilities: List[str]
    recommended_for: List[str]

class CustomModel(BaseModel):
    base_model: str
    template_modifications: str
    status: str

class ModelPerformance(BaseModel):
    temperature: float
    top_p: float
    top_k: int
    repeat_penalty: float
    num_predict: int

class ModelFallback(BaseModel):
    enabled: bool
    strategy: str
    order: List[str]

class ModelsConfig(BaseModel):
    recommended_models: List[Dict[str, Any]]
    custom_models: Dict[str, CustomModel]
    performance: ModelPerformance
    fallback: ModelFallback

class CombinedConfig(MainConfig):
    models: ModelsConfig

# --- Loading Logic ---

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Loads a YAML file."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def create_config() -> CombinedConfig:
    """Loads, merges, and validates all YAML configurations."""
    config_dir = Path(__file__).parent
    
    # Load main and model configs
    main_config_dict = load_yaml(config_dir / "config.yaml")
    models_config_dict = load_yaml(config_dir / "models.yaml")
    
    # Add the output_key to the reporting section
    main_config_dict['reporting']['output_key'] = "final_report"

    # Combine them
    combined_dict = {**main_config_dict, "models": models_config_dict}
    
    # Validate with Pydantic
    return CombinedConfig(**combined_dict)

# --- Global Config Instance ---

# Create a single, validated config instance for the app to import
config = create_config()
