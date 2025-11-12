# LexSpend Quick Start Guide

## Prerequisites

1. **Install Ollama** from https://ollama.com
2. **Pull a model**:
   ```bash
   ollama pull llama2
   # Or
   ollama pull mistral:7b
   ```

## Setup

```bash
cd LexSpend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application

### Option 1: Streamlit UI (Recommended)

1. **Start Ollama** (in separate terminal):
   ```bash
   ollama serve
   ```

2. **Run Streamlit**:
   ```bash
   streamlit run ui/app.py
   ```

3. **Use the interface**:
   - Upload `data/sample_legal_spend.csv` or your own file
   - Chat with the agent: "What are the top 5 law firms by spend?"
   - Run anomaly detection to find high-risk items

### Option 2: ADK CLI

1. **Start Ollama** (in separate terminal):
   ```bash
   ollama serve
   ```

2. **Run ADK agent**:
   ```bash
   adk run lexspend
   ```

3. **Try these commands**:
   ```
   Analyze the legal spend data in data/sample_legal_spend.csv
   What are the top 5 law firms by spend?
   Calculate the total spend
   Identify cost savings opportunities
   Run anomaly detection on data/sample_legal_spend.csv
   ```

### Option 3: ADK Web Interface

```bash
adk web
```

Then select `lexspend` from the list of available agents.

## Testing Anomaly Detection

The GNN-based anomaly detection will:
1. Build a graph from your data
2. Train a model (takes a few minutes)
3. Score each line item (0-1, higher = higher risk)
4. Save results to SQLite database

High-risk items typically include:
- Partners billing for document review
- Unusually high rates for routine tasks
- Ambiguous descriptions

## Troubleshooting

**Ollama not found**: Make sure Ollama is installed and `ollama serve` is running

**Import errors**: Ensure you're in the LexSpend directory and virtual environment is activated

**Model not found**: Check that you've pulled the model: `ollama list`

**GNN training slow**: This is normal for first run. Reduce `GNN_EPOCHS` in `config.py` for faster testing.

