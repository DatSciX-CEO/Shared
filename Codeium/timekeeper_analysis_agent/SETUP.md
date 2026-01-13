# Timekeeper Analysis Agent - Setup Guide

## Quick Start

### 1. Prerequisites

**Required:**
- Python 3.10 or higher
- Ollama installed and running ([Download](https://ollama.ai/download))
- Recommended Ollama model: `mistral-small3.1` or `llama3.2`

**Verify Ollama Installation:**
```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull the recommended model
ollama pull mistral-small3.1

# Verify model supports tools
ollama show mistral-small3.1
# Should show "tools" in Capabilities section
```

### 2. Installation

```bash
# Clone or navigate to project directory
cd timekeeper_analysis_agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example environment file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Mac/Linux

# Edit .env file with your settings (optional - defaults work for local Ollama)
```

### 4. Run the Application

**Option A: Streamlit Web UI (Recommended)**
```bash
python main.py --ui streamlit
# Opens browser at http://localhost:8501
```

**Option B: Interactive CLI**
```bash
python main.py
```

**Option C: Batch File Analysis**
```bash
python main.py --file path/to/timekeeper_data.csv --analysis-type comprehensive
```

## Usage Examples

### Using the Streamlit UI

1. Launch the application:
   ```bash
   python main.py --ui streamlit
   ```

2. Upload your timekeeper data file (CSV, Excel, or Parquet)

3. Select analysis type:
   - **Comprehensive**: All analyses (productivity, billing, optimization)
   - **Productivity Only**: Focus on utilization and efficiency
   - **Billing Anomalies Only**: Detect unusual patterns
   - **Resource Optimization Only**: Allocation recommendations

4. Click "Start Analysis" and wait for results

5. Review findings and export report in preferred format

### Using Interactive CLI

```bash
$ python main.py

You: Please analyze the timekeeper data at C:\data\timekeepers.csv

Agent: I'll analyze the timekeeper data file. Let me start by loading and validating the data...

[Analysis results appear here]

You: What are the top 3 recommendations?

Agent: Based on the analysis, here are the top 3 recommendations...
```

### Using Batch Mode

```bash
# Comprehensive analysis
python main.py --file data/timekeepers.csv --analysis-type comprehensive

# Productivity analysis only
python main.py --file data/timekeepers.csv --analysis-type productivity

# Billing anomaly detection
python main.py --file data/timekeepers.csv --analysis-type billing

# Resource optimization
python main.py --file data/timekeepers.csv --analysis-type optimization
```

## Data File Requirements

### Required Columns

Your timekeeper data file must include these columns:

- `timekeeper_id`: Unique identifier for each timekeeper
- `date`: Date of entry (YYYY-MM-DD format)
- `hours`: Hours worked/billed (numeric)
- `rate`: Billing rate (numeric)

### Optional Columns (Enhance Analysis)

- `matter_id`: Matter/case identifier
- `task_code`: Task or activity code
- `description`: Work description
- `client_id`: Client identifier
- `billable`: Boolean indicating if hours are billable

### Example Data Format (CSV)

```csv
timekeeper_id,date,hours,rate,matter_id,billable
TK001,2025-01-15,8.5,250,M123,true
TK001,2025-01-16,7.0,250,M123,true
TK002,2025-01-15,6.5,200,M456,true
TK002,2025-01-16,8.0,200,M456,true
```

## Configuration

### Ollama Configuration

Edit `config/config.yaml` to customize Ollama settings:

```yaml
ollama:
  base_url: "http://localhost:11434"
  provider: "ollama_chat"  # Important: use ollama_chat, not ollama
  default_model: "mistral-small3.1"
  timeout: 120
  max_retries: 3
```

### Analysis Parameters

Customize analysis thresholds in `config/config.yaml`:

```yaml
analysis:
  productivity:
    low_hours_threshold: 20
    high_hours_threshold: 60
    billable_target_percentage: 75

  billing:
    rate_variance_threshold: 0.3  # 30% deviation
    hours_spike_threshold: 2.0    # 2x average

  resource:
    utilization_target: 80
    bench_time_threshold: 10
```

## Troubleshooting

### Ollama Connection Issues

**Problem**: `Connection refused` or `Cannot connect to Ollama`

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `curl http://localhost:11434`
3. Verify base_url in config.yaml matches your Ollama endpoint

### Model Not Found

**Problem**: `Model 'mistral-small3.1' not found`

**Solution**:
```bash
ollama pull mistral-small3.1
```

### Tool Support Issues

**Problem**: Infinite tool loops or context loss

**Solution**:
- Ensure you're using `ollama_chat` provider (not `ollama`)
- Verify model supports tools: `ollama show <model_name>`
- Check "tools" appears in Capabilities section

### Import Errors

**Problem**: `ModuleNotFoundError` when running agents

**Solution**:
```bash
# Ensure you're in the project root directory
cd timekeeper_analysis_agent

# Reinstall dependencies
pip install -r requirements.txt
```

### Memory Issues with Large Files

**Problem**: Application crashes with large files

**Solution**:
- Adjust `chunk_size_rows` in config.yaml
- Use Parquet format for better performance with large datasets
- Increase system memory allocation for Python

## Advanced Configuration

### Using Custom Ollama Models

1. Create a custom model template:
   ```bash
   ollama show --modelfile mistral-small3.1 > custom_model.txt
   # Edit custom_model.txt with your modifications
   ollama create my-custom-model -f custom_model.txt
   ```

2. Update config.yaml:
   ```yaml
   agents:
     director_model: "my-custom-model"
     worker_model: "my-custom-model"
   ```

### Switching to Vertex AI (Cloud)

If you want to use Google Vertex AI instead of local Ollama:

1. Set up Google Cloud credentials
2. Update agent files to use Vertex AI models:
   ```python
   # In agents/director_agent.py
   model="gemini-2.0-flash"  # Instead of get_ollama_model()
   ```

## Performance Optimization

### For Large Datasets (>100K records)

1. Enable chunked processing in config.yaml:
   ```yaml
   data:
     chunk_size_rows: 10000
   ```

2. Use Parquet format for faster loading

3. Consider running analysis in batch mode rather than interactive

### For Faster Response Times

1. Use lighter models for worker agents:
   ```yaml
   agents:
     director_model: "mistral-small3.1"
     worker_model: "llama3.2"  # Lighter model
   ```

2. Adjust analysis parameters to reduce iterations:
   ```yaml
   agents:
     max_analysis_iterations: 2  # Reduce from 3
   ```

## Support

For issues, questions, or contributions:
- Review official Google ADK documentation: https://google.github.io/adk-docs
- Check Ollama documentation: https://ollama.ai/docs
- Contact: DatSciX Team

## License

Copyright 2025 DatSciX. All rights reserved.