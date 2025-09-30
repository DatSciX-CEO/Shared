from google.adk.agents import LlmAgent
from google.adk.models import ModelFactory
from google.adk.models.ollama import Ollama

from . import prompt
from .tools.file_reader_tool import FileReaderTool
from config import OLLAMA_MODEL

# Register the local Ollama model with the ADK ModelFactory.
# This is the idiomatic way to make a custom model available to LlmAgent.
ModelFactory.update_model_config(
    {
        "ollama-legal-model": { # A custom identifier for our model
            "connector": Ollama(model=OLLAMA_MODEL),
            "config": {
                "temperature": 0.0,
            },
        }
    }
)

# Define the agent declaratively, following ADK best practices.
legal_spend_agent = LlmAgent(
    name="legal_spend_agent",
    model="ollama-legal-model",  # Use the identifier registered in the ModelFactory
    instruction=prompt.SYSTEM_PROMPT,
    description="An agent that analyzes legal spend data from CSV or Excel files.",
    tools=[FileReaderTool()],
)

# The root_agent is the entry point for the ADK CLI.
root_agent = legal_spend_agent
