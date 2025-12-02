# Quick Start Guide - Legal Spend Main

Get up and running with the **Legal Spend Analysis** hierarchical agent system in under 5 minutes.

## ✅ Prerequisites Check

Run these commands in your terminal to ensure your environment is ready.

1.  **Check Python** (Requires 3.8+):
    ```bash
    python --version
    ```
2.  **Check Ollama**:
    ```bash
    ollama --version
    ```
    *If not installed, download from [ollama.ai](https://ollama.ai).*

## 🚀 Step 1: Prepare the AI Models

The system requires local LLMs to function. We recommend `mistral` for general tasks.

```bash
# 1. Start the Ollama server (keep this terminal window open)
ollama serve

# 2. In a new terminal, download the base models
ollama pull mistral:7b
ollama pull llama2
```

## 📦 Step 2: Install the Application

Set up the project and its dependencies.

```bash
# Navigate to the project folder
cd legal_spend_main

# Install Python requirements
pip install -r requirements.txt
```

## 🖥️ Step 3: Launch the Interface

Start the Streamlit web application.

```bash
cd ui
streamlit run app.py
```

**Success!** The app should open automatically at `http://localhost:8501`.

## 🎮 Step 4: Your First Analysis

Once the app is running:

1.  **Upload Data**:
    *   Go to the sidebar **Data Source**.
    *   Select **CSV**.
    *   Upload a sample legal spend CSV file (see example below if you don't have one).
    *   Wait for the "✅ Data Source: CSV" confirmation.

2.  **Ask a Question**:
    *   Type in the chat box: **"Analyze this data and tell me which law firms we spend the most with."**
    *   The **LegalOpsManager** will delegate this to the **SpendAnalyzer** and return the results.

3.  **Try Advanced Queries**:
    *   *"Are there any anomalies in the billing?"* (Triggers AnomalyDetector)
    *   *"Identify potential cost savings in document review."* (Triggers eDiscoverySpecialist)
    *   *"Forecast our spending for the next quarter."* (Triggers SpendForecaster)

## 📄 Sample Data (Copy & Save as `sample.csv`)

If you don't have data, save this text as `sample.csv` to test the system:

```csv
law_firm,amount,date,description,timekeeper,rate,hours
Smith & Associates,5000.00,2024-01-15,Document review,John Partner,850,10
Johnson Legal,3500.00,2024-01-16,Legal research,Jane Associate,350,10
Williams Law,8000.00,2024-01-17,Deposition preparation,Bob Senior,400,20
Smith & Associates,4200.00,2024-01-18,Trial preparation,Sarah Partner,850,4.9
Johnson Legal,6100.00,2024-01-19,Document review,Mike Associate,350,17.4
TechLaw LLP,12000.00,2024-01-20,Patent filing,Alice Expert,600,20
```

## ❓ Troubleshooting

*   **App won't start?** Check if you are in the `legal_spend_main/ui` directory when running `streamlit`.
*   **Agents silent?** Ensure `ollama serve` is running in the background.
*   **SQL Errors?** If using SQL mode, verify you have the `ODBC Driver 17 for SQL Server` installed.
