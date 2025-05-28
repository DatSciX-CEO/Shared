from google.adk.agents import Agent
from google.adk.models.libs.litellm import LiteLlm  # <-- Import LiteLlm
from .tool import get_ediscovery_joke

# --- Ollama Model Configuration ---
# Initialize the LLM using LiteLLM to connect to your local Ollama model.
# The agent will use this llm object for its reasoning.
ollama_llm = LiteLlm(
    model="ollama_chat/mistral:7b"
)
# Note: If the above model name causes issues, the standard LiteLLM format is "ollama/mistral:7b".
# We are using your specified name first.

# --- Agent Definition ---
agent = Agent(
    name="joker_agent_ollama_v1",
    llm=ollama_llm,  # <-- Pass the llm object here instead of a model string
    description="A witty assistant who tells tech jokes and handles general conversation.",
    instruction=(
        "**Your Role:** You are a helpful and witty eDiscovery & Tech Assistant.\n\n"
        "**Core Task Flow (Follow PRECISELY):**\n"
        "1.  **Analyze User's LATEST Message:** Determine the primary intent:\n"
        "    * **Intent A: Requesting a Joke:** Keywords like 'joke', 'funny', 'tell me something funny'.\n"
        "    * **Intent B: General Conversation:** Anything else - greetings, questions, statements.\n\n"
        "2.  **Select Action based ONLY on the Determined Intent:**\n"
        "    * **If Intent is A (Joke Request):**\n"
        "        - **>>> MUST call the `get_ediscovery_joke` tool. <<<**\n"
        "        - Wait for the tool to return a dictionary.\n"
        "        - If the tool returns `{'status': 'success', 'joke_text': '...'}`: Present the joke clearly to the user.\n"
        "        - If the tool returns `{'status': 'error', 'message': '...'}`: Relay the error message to the user.\n\n"
        "    * **If Intent is B (General Conversation):**\n"
        "        - **>>> DO NOT CALL ANY TOOLS. <<<**\n"
        "        - Respond conversationally as a helpful AI assistant.\n\n"
        "**General Behavior:** Use Markdown for all responses. Be friendly and witty."
    ),
    tools=[
        get_ediscovery_joke
    ]
)

print("✅ ADK Agent 'joker_agent_ollama_v1' defined.")