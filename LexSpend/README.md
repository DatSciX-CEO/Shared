# LexSpend: Legal Spend Analysis with Google ADK

AI-powered legal spend analysis application using Google's Agent Development Kit (ADK) with local processing via Ollama. Features advanced anomaly detection using Graph Neural Networks (GNN) to identify document review anomalies and eDiscovery spend analysis.

## Features

- **AI Agents**: Conversational analysis using Google ADK with local Ollama models
- **File Upload**: Support for CSV and Excel files
- **Anomaly Detection**: GNN-based unsupervised anomaly detection for identifying high-risk line items
- **eDiscovery Analysis**: Specialized analysis for eDiscovery-related expenditures
- **Local Processing**: 100% local processing - no cloud dependencies
- **Streamlit UI**: Interactive web interface for file upload and agent interaction
- **ADK CLI**: Command-line interface for quick testing

## Technology Stack

- **Framework**: Google ADK (Agent Development Kit)
- **UI**: Streamlit
- **LLM**: Ollama (local models via LiteLLM)
- **ML/GNN**: PyTorch + PyTorch Geometric
- **NLP**: Hugging Face transformers (Sentence-BERT)
- **Data**: Pandas, SQLite

## Installation

### Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.com
   # Then pull a model:
   ollama pull llama2
   # Or use another model like mistral:7b
   ollama pull mistral:7b
   ```

### Setup

1. **Clone/Navigate to LexSpend directory**
   ```bash
   cd LexSpend
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Ollama model (optional)**
   ```bash
   # Set environment variable or edit config.py
   export OLLAMA_MODEL=llama2
   # Or for mistral
   export OLLAMA_MODEL=mistral:7b
   ```

## Usage

### Streamlit UI (Recommended)

1. **Start Ollama server** (in a separate terminal)
   ```bash
   ollama serve
   ```

2. **Run Streamlit app**
   ```bash
   streamlit run ui/app.py
   ```

3. **Use the interface**:
   - Upload a CSV or Excel file with legal spend data
   - Chat with the AI agent about your data
   - Run anomaly detection to identify high-risk items
   - View results with threshold filtering

### ADK CLI (Quick Testing)

1. **Start Ollama server** (in a separate terminal)
   ```bash
   ollama serve
   ```

2. **Run ADK agent**
   ```bash
   adk run lexspend
   ```

3. **Interact with the agent**:
   ```
   Analyze the legal spend data in data/sample_legal_spend.csv
   What are the top 5 law firms by spend?
   Identify potential cost savings opportunities.
   ```

### ADK Web Interface

For quick testing and debugging:
```bash
adk web
```

## Data Format

Your CSV or Excel file should include the following columns (or similar):

- **Position Title** (or Timekeeper, Role): e.g., "Partner", "Associate", "Paralegal"
- **Units** (or Hours, Billable Hours): Number of hours/units billed
- **Bill Rate** (or Rate, Hourly Rate): Billing rate per hour/unit
- **Cost** (or Total Cost, Amount): Total cost for the line item
- **Line Item Description** (or Description, Activity): Free-text description of the work
- **Type of Case** (or Case Type, Matter Type): e.g., "Litigation", "Contract", "Regulatory"

The system will automatically detect alternative column names and normalize them.

## Anomaly Detection

The GNN-based anomaly detection system:

1. **Builds a graph** from your tabular data with:
   - LineItem nodes (one per row)
   - Timekeeper nodes (from Position Title)
   - CaseType nodes (from Type of Case)

2. **Generates embeddings** for line item descriptions using Sentence-BERT

3. **Trains a Graph Autoencoder** to learn normal patterns

4. **Calculates review scores** (0-1) where higher scores indicate higher risk

5. **Saves results** to SQLite database for persistence

**High-risk items** typically include:
- Partners billing for document review work
- Unusually high rates for routine tasks
- Ambiguous descriptions that might hide inappropriate billing

## Project Structure

```
LexSpend/
├── lexspend/              # Main package (ADK agent)
│   ├── agent.py          # Root agent definition (root_agent)
│   ├── prompt.py         # System prompts
│   ├── tools/            # ADK tools
│   │   ├── file_reader_tool.py
│   │   ├── data_analysis_tool.py
│   │   └── anomaly_detection_tool.py
│   ├── models/           # ML models
│   │   ├── embeddings.py
│   │   ├── graph_builder.py
│   │   └── gnn_model.py
│   └── data/             # Data processing
│       ├── preprocessing.py
│       └── storage.py
├── ui/                   # Streamlit UI
│   └── app.py
├── data/                 # Sample data
│   └── sample_legal_spend.csv
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## ADK Conventions

This project follows Google ADK best practices:

- **Package Structure**: `lexspend/lexspend/agent.py` with `root_agent` export
- **Model Configuration**: Uses `ModelFactory` with `Ollama` connector
- **Agent Definition**: Uses `LlmAgent` declarative pattern
- **Tools**: Inherit from `Tool` base class
- **CLI Discovery**: `adk run lexspend` works via `root_agent` export

## Configuration

Edit `config.py` to customize:

- **Ollama Model**: `OLLAMA_MODEL` (default: "llama2")
- **GNN Parameters**: Embedding dimensions, epochs, learning rate
- **Sentence-BERT Model**: Default is "all-MiniLM-L6-v2"
- **Database Path**: SQLite database location

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama is running: `ollama serve`
- Check model is available: `ollama list`
- Verify model name in `config.py` matches your Ollama model

### Import Errors

- Ensure you're in the LexSpend directory
- Activate virtual environment if using one
- Install all dependencies: `pip install -r requirements.txt`

### GNN Training Issues

- Ensure PyTorch and PyTorch Geometric are installed correctly
- Check CUDA availability if using GPU
- Reduce `GNN_EPOCHS` in `config.py` for faster testing

## Future Enhancements

- Multiple analysis types (Doc Review, Privilege Review, etc.)
- Database connectivity (beyond file upload)
- Graph visualization
- Model persistence and retraining
- Batch processing for multiple files
- Additional graph node types (Timekeeper Name, Matter ID)

## License

[Your License Here]

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK Python GitHub](https://github.com/google/adk-python)
- [Ollama Documentation](https://docs.ollama.com/)
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)

