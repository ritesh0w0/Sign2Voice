#!/usr/bin/env bash
# ====================================================
#              Sign2Voice Launcher (Unix/macOS)
# ====================================================

set -e

echo "===================================================="
echo "          Sign2Voice - AI Sign Language System       "
echo "===================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    echo "Please install Python 3.10+ from https://python.org or via brew / apt."
    exit 1
fi

echo "[1/3] Python environment verified: $(python3 --version)"

# 2. Virtual environment setup (optional but recommended)
if [ ! -d "venv" ]; then
    echo "[2/3] Creating virtual environment 'venv'..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[2/3] Installing dependencies..."
pip install -r requirements.txt

# 3. Start server
echo ""
echo "[3/3] Starting Sign2Voice Server..."
echo "Application running at: http://localhost:8000"
echo "Press Ctrl+C to terminate."
echo ""

python3 main.py

