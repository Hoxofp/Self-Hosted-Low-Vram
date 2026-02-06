#!/bin/bash
echo "========================================"
echo "  AI Agent - Linux/Mac Setup"
echo "========================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Please install Python 3.10+"
    exit 1
fi
echo "[OK] Python found"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "[WARN] Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi
echo "[OK] Ollama found"

# Create virtual environment
echo "[INFO] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt

# Download model
echo "[INFO] Downloading Qwen model (this may take a while)..."
ollama pull qwen2.5-coder:3b-instruct-q4_K_M

echo
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo
echo "Run the agent with:"
echo "  source venv/bin/activate"
echo "  python scripts/run_agent.py"
