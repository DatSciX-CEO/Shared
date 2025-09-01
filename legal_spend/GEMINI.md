# Gemini Context: Legal Spend Analysis Agent

## Project Overview

This project contains an AI agent designed to analyze legal spend data from local files (CSV or Excel). The agent acts as an expert legal spend analyst, summarizing key findings, identifying top law firms by spend, and highlighting potential cost-saving areas.

**Key Technologies & Architecture:**

*   **Framework:** Google Agent Development Kit (ADK)
*   **Language:** Python
*   **LLM:** The agent is configured to use a local Ollama instance with the `llama2` model. The connection is managed idiomatically through the ADK's `ModelFactory` and `Ollama` connector.
*   **Core Agent:** The primary logic is encapsulated in `legal_spend.agent.legal_spend_agent`, which is an `LlmAgent`.
*   **Tools:** The agent is equipped with a `FileReaderTool` that uses the `pandas` library to read and parse CSV and Excel files.

## Building and Running

### 1. Installation

Install the required Python dependencies from the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

### 2. Running the Agent

To run the agent, ensure your local Ollama service is active and then use the Google ADK command-line tool:

```sh
adk run legal_spend
```

Once the agent is running, you can interact with it in the terminal. To have it analyze a file, provide a prompt that includes the full path to your data file.

**Example Interaction:**

```
Analyze the legal spend data in C:\data\acme_corp_legal_spend_q3.xlsx
```

### 3. Testing

`TODO`: The project includes an empty `test_legal_spend.py` file. A testing framework like `pytest` should be implemented. Once tests are written, they can likely be run with a standard command:

```sh
pytest
```

## Development Conventions

*   **Agent Definition:** The project follows the declarative `LlmAgent` pattern. The main agent instance is defined as `root_agent` in `legal_spend/agent.py` to make it discoverable by the ADK CLI.
*   **Model Configuration:** Local models are registered via the `ModelFactory` in `agent.py`. The specific model name (e.g., "llama2") is managed in `config.py`.
*   **Tools:** Custom tools should be created in the `legal_spend/tools/` directory and inherit from the `adk.tools.Tool` class.
*   **Prompts:** System prompts and other instructional text for the agent are centralized in `legal_spend/prompt.py`.
