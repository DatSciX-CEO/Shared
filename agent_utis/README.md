# Agent Utis MVP

AI-Powered eDiscovery Utilization Analysis Application

## Overview

Agent Utis is a local AI agent application designed for eDiscovery vendors (similar to Consilio and LOD) to analyze expert utilization rates, billable hours, cost efficiency, predictive spend, and resource optimization in legal and eDiscovery contexts.

## Features

- **Hierarchical AI Agents**: Finance Director orchestrates specialized sub-agents
  - Data Analyst: CSV processing and validation
  - Utilization Expert: Metrics calculation and analysis
  - Spend Predictor: Forecasting using regression analysis
  - Compliance Checker: Best practices alignment

- **Interactive Streamlit UI**: 
  - CSV file upload and validation
  - Interactive chat interface for expert consultations
  - Comprehensive dashboards and visualizations
  - Real-time analysis and reporting

- **Local Processing**: 
  - No cloud dependencies
  - Uses Ollama with Mistral 7B model
  - Complete data privacy and security

## Requirements

- Python 3.8+
- Ollama installed locally
- Minimum 8GB RAM (recommended 16GB for optimal performance)

## Installation & Setup

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd agent_utis
```

### 2. Run Setup Script

#### On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install and Setup Ollama

1. Download Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Install following platform-specific instructions
3. Pull the Mistral model:
```bash
ollama pull mistral:7b
```

## Running the Application

### 1. Start Ollama Server

```bash
ollama serve
```

Keep this terminal open - the server needs to run in the background.

### 2. Start the Streamlit Application

In a new terminal:

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run the application
streamlit run main.py
```

### 3. Access the Application

Open your browser and navigate to: `http://localhost:8501`

## Usage Guide

### 1. Data Upload

- Upload a CSV file with utilization data
- Required columns: `expert_name`, `billable_hours`, `total_hours`
- Optional columns: `project`, `cost`, `date`, `hourly_rate`, `role`
- Or use "Load Example Data" to try with sample data

### 2. Run Analysis

- Click "Run Complete Analysis" to process your data
- The Finance Director will orchestrate all sub-agents
- View results in organized tabs: Utilization, Spend Prediction, Compliance

### 3. Interactive Queries

- Use the chat interface to ask specific questions
- Examples:
  - "What are the main utilization issues?"
  - "Predict next quarter spending"
  - "Which experts are over-utilized?"
  - "Show cost efficiency by role"

## CSV Data Format

### Required Columns
- `expert_name`: Name of the expert/consultant
- `billable_hours`: Hours billed to clients
- `total_hours`: Total hours worked

### Optional Columns
- `expert_id`: Unique identifier
- `role`: Expert's role (e.g., "Document Reviewer", "Legal Analyst")
- `project_name`: Project identification
- `date`: Date of record (YYYY-MM-DD format)
- `hourly_rate`: Billing rate per hour
- `total_cost`: Total cost for the period
- `utilization_rate`: Pre-calculated utilization percentage

### Example Data Structure

```csv
expert_name,role,billable_hours,total_hours,hourly_rate,total_cost,date
Sarah Johnson,Document Reviewer,152,200,125,19000,2024-01-31
Michael Chen,Legal Analyst,180,200,150,27000,2024-01-31
```

## Agent Architecture

### Finance Director (Orchestrator)
- Coordinates all sub-agents
- Synthesizes comprehensive reports
- Handles complex queries
- Provides executive summaries

### Data Analyst
- Validates CSV data quality
- Performs statistical analysis
- Identifies data patterns and anomalies

### Utilization Expert
- Calculates utilization rates and metrics
- Identifies over/under-utilization
- Provides optimization recommendations
- Industry benchmark comparisons (70-80% target)

### Spend Predictor
- Forecasts future spending using linear regression
- Analyzes spending trends
- Provides budget recommendations

### Compliance Checker
- Ensures alignment with legal industry best practices
- Identifies compliance risks
- Provides improvement recommendations

## Key Metrics

- **Utilization Rate**: (Billable Hours / Total Hours) × 100
- **Cost Per Billable Hour**: Total Cost / Billable Hours
- **Industry Benchmarks**: 70-80% utilization target
- **Efficiency Metrics**: Revenue vs. cost analysis

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama server is running: `ollama serve`
   - Verify Mistral model is installed: `ollama list`

2. **CSV Upload Issues**
   - Check file format and required columns
   - Ensure no special characters in file path
   - Verify data types (numeric columns should contain numbers)

3. **Memory Issues**
   - Close other applications to free RAM
   - Consider using smaller datasets for testing
   - Restart Ollama if experiencing slowdowns

4. **Agent Response Errors**
   - Check Ollama logs for model issues
   - Verify internet connection for initial setup
   - Restart the application if agents become unresponsive

### Performance Optimization

- Use SSD storage for better I/O performance
- Allocate sufficient RAM (16GB recommended)
- Close unnecessary applications while running analysis
- Use example data first to verify setup

## Development

### Project Structure

```
agent_utis/
├── main.py              # Streamlit application
├── agents.py            # AI agent definitions
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
├── README.md           # This file
├── data/               # Example data
│   └── example_utilization_data.csv
└── tests/              # Test files (future)
```

### Adding New Features

1. Extend agent classes in `agents.py`
2. Add utility functions in `utils.py`
3. Update UI components in `main.py`
4. Follow existing error handling patterns

### Testing

Use the provided example CSV data to test functionality:
- Load example data from the UI
- Run complete analysis
- Test various query types in chat interface

## Security & Privacy

- **Local Processing**: All data remains on your machine
- **No Cloud Dependencies**: No external API calls after setup
- **Data Isolation**: Each session is independent
- **Secure by Design**: No data transmission or storage

## License

This project is intended for demonstration and educational purposes. Please ensure compliance with your organization's software policies.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify Ollama installation and model availability
3. Review CSV data format requirements
4. Ensure all dependencies are properly installed

---

*Powered by Ollama Mistral 7B and designed for eDiscovery utilization analysis*