import pyjokes
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

def get_ediscovery_joke(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Fetches a random, SFW (Safe-for-Work) programming or tech-related joke.
    This tool should be used when the user explicitly asks for a joke.
    It does not require any arguments.

    Args:
        tool_context: The ADK ToolContext, not used in this tool but included for pattern consistency.

    Returns:
        A dictionary with a 'status' of 'success' and the 'joke_text'.
    """
    print("--- Tool: get_ediscovery_joke called ---")
    try:
        # Fetch a neutral category joke that is SFW
        joke = pyjokes.get_joke(category='neutral')
        return {"status": "success", "joke_text": joke}
    except Exception as e:
        print(f"--- Tool: ERROR - Failed to get joke: {e} ---")
        return {"status": "error", "message": f"Sorry, I couldn't think of a joke right now. Error: {e}"}