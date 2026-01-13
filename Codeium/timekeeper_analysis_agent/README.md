# Timekeeper Analysis Agent System

## Overview
Hierarchical AI agent system built with Google ADK for analyzing timekeeper data in eDiscovery vendor operations. Uses Ollama for local LLM processing with dual UI options (Streamlit and ADK Web).

## Architecture

### Hierarchical Agent Structure
```
TimekeeperDirector (Orchestrator)
├── DataIngestionAgent (CSV/Excel/Parquet processing)
├── TimekeeperAnalysisCoordinator
│   ├── ProductivityAnalystAgent
│   ├── BillingAnomalyDetectorAgent
│   └── ResourceOptimizationAgent
└── ReportGeneratorAgent
```

## Features
- **Local Processing**: All LLM operations run locally via Ollama
- **Multi-Format Support**: CSV, Excel, Parquet file ingestion
- **Hierarchical Analysis**: Specialized sub-agents for different analysis dimensions
- **Dual UI**: Choose between Streamlit or ADK Web interface
- **Accurate Implementation**: Based on official Google ADK documentation

## Technology Stack
- **Agent Framework**: Google ADK (Agent Development Kit)
- **LLM Backend**: Ollama (local models)
- **UI Options**: Streamlit / ADK Web
- **Data Processing**: Pandas, Polars
- **Configuration**: YAML-based config files

## Project Structure
```
timekeeper_analysis_agent/
├── config/
│   ├── config.yaml
│   └── models.yaml
├── prompts/
│   ├── director_prompt.py
│   ├── data_ingestion_prompt.py
│   ├── analysis_coordinator_prompt.py
│   ├── productivity_analyst_prompt.py
│   ├── billing_anomaly_prompt.py
│   ├── resource_optimization_prompt.py
│   └── report_generator_prompt.py
├── agents/
│   ├── __init__.py
│   ├── director_agent.py
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── data_ingestion_agent.py
│   │   ├── analysis_coordinator_agent.py
│   │   ├── productivity_analyst_agent.py
│   │   ├── billing_anomaly_detector_agent.py
│   │   ├── resource_optimization_agent.py
│   │   └── report_generator_agent.py
├── tools/
│   ├── __init__.py
│   ├── file_loader_tool.py
│   ├── data_validator_tool.py
│   ├── statistical_analysis_tool.py
│   └── report_export_tool.py
├── services/
│   ├── __init__.py
│   ├── ollama_service.py
│   └── data_processing_service.py
├── ui/
│   ├── streamlit_app.py
│   └── adk_web_app.py
├── requirements.txt
└── main.py
```

## Setup Instructions

### Prerequisites
1. Install Ollama: https://ollama.ai/download
2. Pull required models (e.g., mistral, llama3.2)
3. Python 3.10+

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify Ollama is running
ollama serve
```

### Configuration
Edit `config/config.yaml`:
```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "mistral-small3.1"  # or your preferred model

agents:
  director_model: "mistral-small3.1"
  worker_model: "mistral-small3.1"

data:
  supported_formats: ["csv", "xlsx", "parquet"]
  max_file_size_mb: 500
```

## Usage

### Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

### ADK Web UI
```bash
python ui/adk_web_app.py
```

### Programmatic Usage
```python
from agents.director_agent import timekeeper_director
from google.adk.runners import Runner

runner = Runner(agent=timekeeper_director, app_name="timekeeper_analysis")
result = runner.run(
    user_id="analyst_001",
    message="Analyze productivity trends from uploaded_timekeepers.csv"
)
```

## Development Notes
- All agents use Ollama via `ollama_chat` provider (not `ollama`)
- Config and prompt files follow ClaimsAssistX structure
- Based on official ADK samples from adk-samples/python/agents
- Hierarchical structure uses AgentTool for sub-agent delegation