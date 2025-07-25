#!/bin/bash

# Agent Utis MVP Setup Script
# This script sets up the local development environment for Agent Utis

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

# Install Ollama (if not already installed)
echo "Setting up Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Please install Ollama from https://ollama.ai/"
    echo "After installation, run: ollama pull mistral:7b"
    exit 1
fi

# Pull Mistral model
echo "Pulling Mistral 7B model..."
ollama pull mistral:7b

echo "Setup complete!"
echo "To run the application:"
echo "1. Start Ollama server: ollama serve"
echo "2. Run Streamlit app: streamlit run main.py"