# File: debug_agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.models.libs.litellm import LiteLlm

print("--- Starting Debug Script ---")
print("Attempting to define the LlmAgent...")

try:
    # Step 1: Initialize the LiteLlm object
    # Using the standard LiteLLM naming convention for this test.
    print("Initializing LiteLlm with model 'ollama/mistral:7b'...")
    ollama_llm = LiteLlm(
        model="ollama/mistral:7b"
    )
    print("LiteLlm initialized successfully.")

    # Step 2: Define the LlmAgent
    # Using the most basic parameters possible.
    print("Defining LlmAgent with minimal parameters...")
    agent = LlmAgent(
        llm=ollama_llm,
        name="test_agent", 
        description="A test agent.",
        instruction="You are a test agent."
    )
    print("\n✅✅✅ SUCCESS: LlmAgent 'test_agent' was defined without errors! ✅✅✅")
    print("\nThis means the issue lies in how the agent is imported or used in your main app.py, not in the definition itself.")

except Exception as e:
    print("\n❌❌❌ ERROR: An exception occurred while defining the agent. ❌❌❌")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease send this entire error message back.")

print("\n--- Debug Script Finished ---")