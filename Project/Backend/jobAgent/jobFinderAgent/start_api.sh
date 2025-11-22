#!/bin/bash

# Job Agent Integration - Startup Script

echo "========================================"
echo "🚀 Job Agent Integration Startup"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "api.py" ]; then
    echo "❌ Error: Please run this script from the jobFinderAgent directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with NEBIUS_API_KEY"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Kill any existing process on port 5001
echo "🧹 Cleaning up existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null

echo ""
echo "✅ Starting Job Agent API Server..."
echo "📡 API will be available at: http://localhost:5001"
echo ""
echo "To test the API, open another terminal and run:"
echo "  curl http://localhost:5001/api/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""

# Start the API server
python api.py
