<!-- 1a7b034d-939f-4cca-90c4-b719ffd8f97a 2f0ea3fb-9ebc-4892-8918-ebe512fe2036 -->
# LexSpend: Legal Spend Analysis with Google ADK & GNN Anomaly Detection

## Project Overview

Build a comprehensive legal spend analysis application in the `LexSpend` folder that combines:

- **Google ADK agents** for conversational analysis and insights
- **Streamlit UI** for file upload and interaction
- **ADK web interface** for quick testing
- **GNN-based anomaly detection** for identifying document review anomalies
- **eDiscovery spend finder** for specialized eDiscovery analysis
- **Local processing** with Ollama (no cloud dependencies)

## Architecture

### Technology Stack

- **Framework**: Google ADK (Agent Development Kit) - Python
- **UI**: Streamlit + ADK web interface
- **LLM**: Ollama (local models via LiteLLM connector)
- **ML/GNN**: PyTorch + PyTorch Geometric for anomaly detection
- **NLP**: Hugging Face transformers (Sentence-BERT for embeddings)
- **Data**: Pandas, SQLite (for result persistence)
- **File Processing**: pandas, openpyxl

### Project Structure

```
LexSpend/
├── lexspend/                    # Main package
│   ├── __init__.py
│   ├── agent.py                 # Root ADK agent definition
│   ├── config.py                # Configuration (Ollama model, etc.)
│   ├── prompt.py                # System prompts for agents
│   ├── agents/                  # Specialized agents
│   │   ├── __init__.py
│   │   ├── analysis_agent.py    # General legal spend analysis
│   │   ├── ediscovery_agent.py  # eDiscovery spend finder
│   │   └── anomaly_agent.py     # GNN anomaly detection agent
│   ├── tools/                   # ADK tools
│   │   ├── __init__.py
│   │   ├── file_reader_tool.py  # CSV/Excel file reading
│   │   ├── data_analysis_tool.py # Basic analysis operations
│   │   └── anomaly_detection_tool.py # GNN anomaly scoring
│   ├── models/                  # ML models
│   │   ├── __init__.py
│   │   ├── gnn_model.py         # Graph Autoencoder for anomaly detection
│   │   ├── graph_builder.py     # Graph construction from tabular data
│   │   └── embeddings.py        # Sentence-BERT text embeddings
│   ├── data/                    # Data processing
│   │   ├── __init__.py
│   │   ├── preprocessing.py     # Data validation and cleaning
│   │   └── storage.py           # SQLite persistence
│   └── services/                # Business logic
│       ├── __init__.py
│       └── analysis_service.py  # Analysis orchestration
├── ui/                          # Streamlit UI
│   ├── app.py                   # Main Streamlit application
│   └── components/              # Reusable UI components
│       ├── file_upload.py
│       ├── results_table.py
│       └── chat_interface.py
├── tests/                       # Unit tests
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_gnn.py
├── data/                        # Sample data
│   └── sample_legal_spend.csv
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
└── .env.example                 # Environment variables template
```

## Implementation Plan

### Phase 1: Core ADK Agent Setup

1. **Project Structure**: Create LexSpend folder with proper Python package structure
2. **ADK Configuration**: Set up Ollama model connection using LiteLLM connector (following Joker_2 pattern)
3. **Root Agent**: Create main `root_agent` in `lexspend/agent.py` using `LlmAgent` pattern
4. **File Reader Tool**: Implement CSV/Excel file reading tool using pandas
5. **Basic Agent**: Create analysis agent for general legal spend insights

### Phase 2: Streamlit UI Integration

1. **Streamlit App**: Create `ui/app.py` with ADK Runner integration (following Joker_2/app.py pattern)
2. **File Upload**: Implement Streamlit file_uploader for CSV/Excel files
3. **Session Management**: Set up ADK InMemorySessionService with proper session handling
4. **Chat Interface**: Build conversational UI for agent interactions
5. **Data Display**: Show uploaded data preview and analysis results

### Phase 3: Advanced Analysis Agents

1. **eDiscovery Agent**: Create specialized agent for eDiscovery spend identification
2. **Analysis Tools**: Build tools for:

   - Top law firms by spend
   - Total spend calculations
   - Cost savings identification
   - Trend analysis
   - Utilization rate calculations

3. **Agent Orchestration**: Connect agents to root agent for delegation

### Phase 4: GNN Anomaly Detection System

1. **Data Preprocessing**: 

   - Validate required columns (Position Title, Units/Hours, Bill Rate, Cost, Line Item Description, Type of Case)
   - Handle missing data
   - Data type validation

2. **NLP Embeddings**:

   - Integrate Sentence-BERT model (all-MiniLM-L6-v2) via transformers
   - Generate embeddings for Line Item Description text
   - Handle empty/missing descriptions

3. **Graph Construction**:

   - Build heterogeneous graph with:
     - LineItem nodes (with features: Units, Bill Rate, Cost, Text Embedding)
     - Timekeeper nodes (from Position Title)
     - CaseType nodes
   - Create edges: Timekeeper → LineItem, CaseType → LineItem

4. **GNN Model**:

   - Implement Graph Autoencoder (GAE) using PyTorch Geometric
   - Encoder: GraphSAGE layers
   - Decoder: Reconstruction network
   - Training: Unsupervised learning on graph structure

5. **Anomaly Scoring**:

   - Calculate reconstruction error for each LineItem
   - Generate review scores (0-1 scale)
   - Save results to SQLite database

### Phase 5: UI for Anomaly Detection

1. **Analysis Workflow**:

   - "Run Analysis" button triggers GNN processing
   - Progress indicators for model training/inference
   - Results saved to SQLite

2. **Results Display**:

   - Data table with Review Score column
   - Sortable by score
   - Threshold slider to filter high-risk items
   - Export functionality

3. **Integration**: Connect GNN tool to ADK agent for conversational queries

### Phase 6: Testing & Documentation

1. **Unit Tests**: Test agents, tools, and GNN components
2. **Integration Tests**: Test full workflow from file upload to results
3. **Sample Data**: Create example legal spend CSV with various scenarios
4. **Documentation**: README with setup, usage, and architecture details
5. **ADK Web Testing**: Ensure `adk run lexspend` works for CLI testing

## Key Files to Create

### Core ADK Files

- `lexspend/agent.py`: Root agent with Ollama LiteLLM configuration
- `lexspend/tools/file_reader_tool.py`: File upload and parsing
- `lexspend/agents/analysis_agent.py`: General analysis agent
- `lexspend/agents/ediscovery_agent.py`: eDiscovery specialist agent
- `lexspend/agents/anomaly_agent.py`: GNN anomaly detection agent

### GNN Implementation

- `lexspend/models/gnn_model.py`: Graph Autoencoder implementation
- `lexspend/models/graph_builder.py`: Tabular data → graph conversion
- `lexspend/models/embeddings.py`: Sentence-BERT text embeddings
- `lexspend/tools/anomaly_detection_tool.py`: ADK tool wrapper for GNN

### UI Files

- `ui/app.py`: Main Streamlit app with ADK integration
- `ui/components/results_table.py`: Anomaly results display with threshold slider

### Configuration

- `lexspend/config.py`: Ollama model configuration
- `requirements.txt`: All dependencies (google-adk, streamlit, pandas, torch, torch-geometric, transformers, etc.)

## Dependencies

### Core

- `google-adk` (latest version per official docs)
- `streamlit>=1.28.0`
- `pandas>=2.0.0`
- `openpyxl` (for Excel support)

### ML/GNN

- `torch>=2.0.0`
- `torch-geometric>=2.3.0`
- `transformers>=4.30.0` (for Sentence-BERT)
- `sentencepiece` (for transformers)

### Local LLM

- `litellm` (for Ollama connection)
- `ollama` (Python client, optional)

### Data Storage

- `sqlite3` (built-in, but may need wrapper)

## Conformance to Official Documentation

1. **ADK Patterns**: Follow official ADK patterns from https://google.github.io/adk-docs/

   - Use `LlmAgent` for agent definitions
   - Use `Tool` base class for custom tools
   - Use `Runner` and `InMemorySessionService` for Streamlit integration
   - Use LiteLLM connector for Ollama (as shown in Joker_2 example)

2. **Ollama Integration**: Follow Ollama documentation

   - Use `ollama_chat/{model}` format for LiteLLM
   - Support environment variables for model selection
   - Handle connection errors gracefully

3. **Project Structure**: Follow ADK best practices

   - `root_agent` export for CLI discovery
   - Modular tool and agent organization
   - Clear separation of concerns

## Future Enhancements (Modular Design)

- Multiple analysis types (Doc Review, Privilege Review, etc.)
- Database connectivity (beyond file upload)
- Additional graph node types (Timekeeper Name, Matter ID, etc.)
- Visualization of graph structure
- Model persistence and retraining
- Batch processing for multiple files

### To-dos

- [ ] Create LexSpend folder structure with all directories and __init__.py files
- [ ] Create requirements.txt with all dependencies (google-adk, streamlit, pandas, torch, torch-geometric, transformers, etc.)
- [ ] Create lexspend/config.py with Ollama model configuration and environment variable support
- [ ] Implement lexspend/tools/file_reader_tool.py for CSV/Excel file reading using pandas
- [ ] Create lexspend/agent.py with root_agent using LlmAgent, LiteLLM connector for Ollama, and file reader tool
- [ ] Create lexspend/agents/analysis_agent.py for general legal spend analysis (top firms, totals, cost savings)
- [ ] Create lexspend/tools/data_analysis_tool.py with functions for spend calculations, top firms, trends
- [ ] Create lexspend/agents/ediscovery_agent.py specialized for eDiscovery spend identification and analysis
- [ ] Implement lexspend/models/embeddings.py with Sentence-BERT model integration for text embeddings
- [ ] Implement lexspend/models/graph_builder.py to convert tabular data to heterogeneous graph (LineItem, Timekeeper, CaseType nodes)
- [ ] Implement lexspend/models/gnn_model.py with Graph Autoencoder (GAE) using PyTorch Geometric for anomaly detection
- [ ] Create lexspend/tools/anomaly_detection_tool.py as ADK tool wrapper for GNN anomaly scoring
- [ ] Create lexspend/agents/anomaly_agent.py that uses anomaly detection tool for document review identification
- [ ] Implement lexspend/data/preprocessing.py for data validation, cleaning, and required column checking
- [ ] Implement lexspend/data/storage.py for SQLite persistence of analysis results
- [ ] Create ui/app.py with Streamlit UI, ADK Runner integration, file uploader, and chat interface
- [ ] Create ui/components/results_table.py with anomaly results display, threshold slider, and filtering
- [ ] Connect all agents (analysis, ediscovery, anomaly) to root agent for proper delegation and orchestration
- [ ] Create data/sample_legal_spend.csv with example data including various scenarios for testing
- [ ] Create README.md with setup instructions, usage guide, architecture overview, and ADK/Ollama configuration
- [ ] Create basic unit tests for agents, tools, and GNN components in tests/ directory