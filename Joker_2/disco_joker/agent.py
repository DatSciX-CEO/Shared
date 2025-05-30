from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tool import get_ediscovery_joke # Relative import for the tool

# --- Ollama Model Configuration ---
ollama_llm = LiteLlm(
    model="ollama_chat/mistral:7b"
)

# --- Agent Definition ---
root_agent = LlmAgent(
    name="disco_joker",
    model=ollama_llm,
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
        "        - **If the tool returns `{'status': 'success', 'joke_text': '...'}`: Your response to the user MUST be ONLY the joke_text itself. Do not call any other tools or functions. Just output the joke directly.**\n" # <-- More explicit instruction here
        "        - If the tool returns `{'status': 'error', 'message': '...'}`: Relay the error message directly to the user. Do not call any other tools.\n\n"
        "    * **If Intent is B (General Conversation):**\n"
        "        - **>>> DO NOT CALL ANY TOOLS. <<<**\n"
        "        - Respond conversationally as a helpful AI assistant.\n\n"
        "**General Behavior:** Use Markdown for all responses. Be friendly and witty. **When providing a joke from the tool, only provide the joke text.**" # <-- Reinforcement
    ),
    tools=[
        get_ediscovery_joke
    ]
)

print("✅ ADK LlmAgent 'disco_joker' (as root_agent) defined.")