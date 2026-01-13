# Copyright 2025 DatSciX
# Services Module

"""Service modules for Ollama integration and data processing."""

from .ollama_service import get_ollama_model
from .data_processing_service import DataProcessor

__all__ = ["get_ollama_model", "DataProcessor"]