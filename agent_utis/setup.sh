#!/bin/bash

# Agent Utis MVP Setup Script
# This script sets up the local development environment for Agent Utis with Google ADK

echo "Setting up Agent Utis MVP environment..."

# Create virtual environment
python -m venv venv

# Activate virtual environment (Linux/Mac)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Virtual environment activated."

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Environment file created. Please configure .env with your settings."
fi

echo "Setup complete!"
echo ""
echo "Configuration:"
echo "1. Edit .env file to configure your preferred model and settings"
echo "2. Ensure you have access to the configured LLM model (default: gemini-2.0-flash-exp)"
echo ""
echo "To run the application:"
echo "streamlit run main.py"
echo ""
echo "The application now uses Google ADK with the following architecture:"
echo "- Main Agent: FinanceDirector"
echo "- Sub-Agents: DataAnalyst, UtilizationExpert, SpendPredictor, ComplianceChecker"
echo "- Tools: CSV analysis, utilization metrics, spend prediction, compliance checking"