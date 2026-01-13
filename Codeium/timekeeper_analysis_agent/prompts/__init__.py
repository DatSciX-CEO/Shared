# Copyright 2025 DatSciX
# Timekeeper Analysis Agent - Prompt Definitions

"""
Prompt definitions for the Timekeeper Analysis Agent system.

This module exports all prompt strings used by agents in the hierarchy.
Prompts follow the structure from official ADK samples and ClaimsAssistX.
"""

from .director_prompt import DIRECTOR_PROMPT
from .data_ingestion_prompt import DATA_INGESTION_PROMPT
from .analysis_coordinator_prompt import ANALYSIS_COORDINATOR_PROMPT
from .productivity_analyst_prompt import PRODUCTIVITY_ANALYST_PROMPT
from .billing_anomaly_prompt import BILLING_ANOMALY_PROMPT
from .resource_optimization_prompt import RESOURCE_OPTIMIZATION_PROMPT
from .report_generator_prompt import REPORT_GENERATOR_PROMPT

__all__ = [
    "DIRECTOR_PROMPT",
    "DATA_INGESTION_PROMPT",
    "ANALYSIS_COORDINATOR_PROMPT",
    "PRODUCTIVITY_ANALYST_PROMPT",
    "BILLING_ANOMALY_PROMPT",
    "RESOURCE_OPTIMIZATION_PROMPT",
    "REPORT_GENERATOR_PROMPT",
]