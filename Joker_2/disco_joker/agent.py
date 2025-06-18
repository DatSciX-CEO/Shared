from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tool import get_ediscovery_joke # Relative import for the tool
import os

# --- Ollama Model Configuration ---
# Allow configuration via environment variables
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Create LiteLLM instance with minimal configuration
ollama_llm = LiteLlm(
    model=f"ollama_chat/{ollama_model}",
)

# --- Agent Definition ---
root_agent = LlmAgent(
    name="disco_joker",
    model=ollama_llm,
    description="A witty assistant who tells tech jokes and handles general conversation.",
    instruction=(
        "You are a helpful and witty eDiscovery & Tech Assistant.\n\n"
        "**CRITICAL RULES:**\n\n"
        "1. **When user asks for a joke** (words like 'joke', 'funny', 'humor'):\n"
        "   - Call the `get_ediscovery_joke` tool\n"
        "   - The tool returns: `{'status': 'success', 'joke_text': '...'}`\n"
        "   - **OUTPUT ONLY THE JOKE TEXT - NO JSON, NO FORMATTING, NO COMMENTARY**\n"
        "   - Example: If tool returns `{'status': 'success', 'joke_text': 'Why did the lawyer...'}`,\n"
        "     you output ONLY: `Why did the lawyer...`\n\n"
        "2. **For all other messages**:\n"
        "   - DO NOT call any tools\n"
        "   - Respond naturally as a helpful assistant\n"
        "   - Be friendly and conversational\n\n"
        "**REMEMBER:** When you get a joke from the tool, output ONLY the joke_text value, nothing else!"
    ),
    tools=[
        get_ediscovery_joke
    ]
)

print("✅ ADK LlmAgent 'disco_joker' (as root_agent) defined.")
print(f"   - Using Ollama model: {ollama_model}")
print(f"   - Ollama base URL: {ollama_base_url}")

# Optional: Set environment variables for LiteLLM if needed
if ollama_base_url != "http://localhost:11434":
    os.environ["OLLAMA_API_BASE"] = ollama_base_url