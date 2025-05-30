# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm
# from .tool import get_ediscovery_joke # Relative import for the tool

# # --- Ollama Model Configuration ---
# ollama_llm = LiteLlm(
#     model="ollama_chat/mistral:7b"
# )

# # --- Agent Definition ---
# root_agent = LlmAgent(
#     name="disco_joker",
#     model=ollama_llm,
#     description="A witty assistant who tells tech jokes and handles general conversation.",
#     instruction=(
#         "**Your Role:** You are a helpful and witty eDiscovery & Tech Assistant.\n\n"
#         "**Core Task Flow (Follow PRECISELY):**\n"
#         "1.  **Analyze User's LATEST Message:** Determine the primary intent:\n"
#         "    * **Intent A: Requesting a Joke:** Keywords like 'joke', 'funny', 'tell me something funny'.\n"
#         "    * **Intent B: General Conversation:** Anything else - greetings, questions, statements.\n\n"
#         "2.  **Select Action based ONLY on the Determined Intent:**\n"
#         "    * **If Intent is A (Joke Request):**\n"
#         "        - **>>> MUST call the `get_ediscovery_joke` tool. <<<**\n"
#         "        - Wait for the tool to return a dictionary.\n"
#         "        - **If the tool returns `{'status': 'success', 'joke_text': '...'}`: Your response to the user MUST be ONLY the joke_text itself. Do not call any other tools or functions. Just output the joke directly.**\n" # <-- More explicit instruction here
#         "        - If the tool returns `{'status': 'error', 'message': '...'}`: Relay the error message directly to the user. Do not call any other tools.\n\n"
#         "    * **If Intent is B (General Conversation):**\n"
#         "        - **>>> DO NOT CALL ANY TOOLS. <<<**\n"
#         "        - Respond conversationally as a helpful AI assistant.\n\n"
#         "**General Behavior:** Use Markdown for all responses. Be friendly and witty. **When providing a joke from the tool, only provide the joke text.**" # <-- Reinforcement
#     ),
#     tools=[
#         get_ediscovery_joke
#     ]
# )

# print("✅ ADK LlmAgent 'disco_joker' (as root_agent) defined.")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tool import get_ediscovery_joke # Relative import for the tool
import os

# --- Ollama Model Configuration ---
# Enhanced configuration with environment variable support and better defaults
ollama_model = os.getenv("OLLAMA_MODEL", "mistral:7b")  # Allow model override via env
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Configurable base URL

ollama_llm = LiteLlm(
    model=f"ollama_chat/{ollama_model}",
    api_base=ollama_base_url,
    # Add timeout and retry configuration for robustness
    timeout=30,  # 30 second timeout
    max_retries=2,
    # Temperature and other parameters should be passed via request_kwargs
    request_kwargs={
        "temperature": 0.7,  # Add some creativity for jokes
        "max_tokens": 500,  # Reasonable limit for responses
        "top_p": 0.9,
    }
)

# --- Agent Definition ---
root_agent = LlmAgent(
    name="disco_joker",
    model=ollama_llm,
    description="A witty assistant who tells tech jokes and handles general conversation.",
    instruction=(
        "You are a helpful and witty eDiscovery & Tech Assistant.\n\n"
        "**CRITICAL INSTRUCTION: Follow this EXACT process for EVERY user message:**\n\n"
        "1. **ANALYZE the user's message for intent:**\n"
        "   - JOKE REQUEST: Contains words like 'joke', 'funny', 'humor', 'laugh', 'tell me something funny'\n"
        "   - GENERAL CONVERSATION: Everything else (questions, greetings, statements, etc.)\n\n"
        "2. **RESPOND based on the intent:**\n\n"
        "   **IF JOKE REQUEST:**\n"
        "   - You MUST call the `get_ediscovery_joke` tool\n"
        "   - The tool returns a dictionary with either:\n"
        "     * Success: `{'status': 'success', 'joke_text': '...'}`\n"
        "     * Error: `{'status': 'error', 'message': '...'}`\n"
        "   - If success: Output ONLY the joke_text, nothing else\n"
        "   - If error: Inform the user of the error\n"
        "   - DO NOT add any commentary before or after the joke\n"
        "   - DO NOT call the tool multiple times\n\n"
        "   **IF GENERAL CONVERSATION:**\n"
        "   - DO NOT call any tools\n"
        "   - Respond naturally and helpfully\n"
        "   - Be friendly and engaging\n"
        "   - Use your knowledge to answer questions\n\n"
        "**FORMATTING:**\n"
        "- Use Markdown for formatting when appropriate\n"
        "- Keep responses concise and clear\n"
        "- Be professional yet personable\n\n"
        "**IMPORTANT:** Never make up jokes yourself. Only use jokes from the tool when requested."
    ),
    tools=[
        get_ediscovery_joke
    ]
)

print("✅ ADK LlmAgent 'disco_joker' (as root_agent) defined.")
print(f"   - Using Ollama model: {ollama_model}")
print(f"   - Ollama base URL: {ollama_base_url}")