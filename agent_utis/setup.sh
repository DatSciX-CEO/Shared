#!/bin/bash

# Agent Utis MVP Setup Script
echo "======================================"
echo "Setting up Agent Utis MVP Environment"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama is not installed!"
    echo "Please install Ollama from: https://ollama.ai/"
    echo "After installation, run: ollama pull mistral:7b"
else
    echo "Ollama detected. Checking for Mistral model..."
    if ollama list | grep -q "mistral:7b"; then
        echo "✓ Mistral:7b model is available"
    else
        echo "Pulling Mistral:7b model..."
        ollama pull mistral:7b
    fi
fi

# Create data directory if it doesn't exist
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOL
# Agent Utis Configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=mistral:7b
LOG_LEVEL=INFO
EOL
    echo "Created .env file with default configuration"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To run Agent Utis:"
echo "1. Start Ollama: ollama serve"
echo "2. In a new terminal, activate venv and run:"
echo "   source venv/bin/activate  # Linux/Mac"
echo "   streamlit run main.py"
echo ""
echo "The app will be available at: http://localhost:8501"