# Copyright 2025 DatSciX
# Ollama Service Module

"""Service for Ollama LLM integration with Google ADK."""

from google.adk.models.lite_llm import LiteLlm
from config.config import config


def get_ollama_model(model_name: str = None) -> LiteLlm:
    """
    Get configured Ollama model for use with ADK agents.

    Args:
        model_name: Optional model name override. If not provided, uses default from config.

    Returns:
        LiteLlm instance configured for Ollama

    Note:
        Uses ollama_chat provider (not ollama) for proper tool support and context handling.
        Ensure Ollama is running locally: ollama serve
    """
    if model_name is None:
        model_name = config.ollama.default_model

    # Use ollama_chat provider for proper tool support
    model_string = f"{config.ollama.provider}/{model_name}"

    return LiteLlm(model=model_string)