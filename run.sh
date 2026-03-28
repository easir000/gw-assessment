#!/bin/bash

# GW Assessment - One-Command Startup
echo "🚀 Starting GW Assessment PoC..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python Version: $python_version"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check seed_data.json
if [ ! -f "seed_data.json" ]; then
    echo "⚠️  Warning: seed_data.json not found!"
fi

# Start server
echo "✅ Server starting on http://127.0.0.1:8000"
uvicorn main:app --host 127.0.0.1 --port 8000 --reload