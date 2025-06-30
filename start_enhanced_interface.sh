#!/bin/bash

# Healthcare Investment Intelligence Platform - Enhanced Interface
# Includes Stock Ticker Intelligence with Management Truth Tracker™

echo "🧬 Healthcare Investment Intelligence Platform"
echo "==========================================="
echo "📊 Features:"
echo "   • Daily healthcare news analysis"
echo "   • Stock ticker intelligence lookup"
echo "   • Management Truth Tracker™"
echo "   • FDA Decision Pattern Analyzer"
echo "   • Executive credibility checking"
echo ""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for yfinance specifically
if ! python3 -c "import yfinance" 2>/dev/null; then
    echo "📦 Installing yfinance for stock data..."
    pip install -q yfinance
fi

# Create necessary directories
mkdir -p reports cache data templates

# Start the enhanced interface
echo ""
echo "🚀 Starting Healthcare Investment Intelligence Platform..."
echo "🌐 Opening web interface at http://localhost:5001"
echo ""
echo "📈 Stock Ticker Lookup: Enter any healthcare/biotech ticker"
echo "🕵️ Executive Credibility: Check management track records"
echo "🧬 FDA Analysis: View approval probabilities"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the enhanced web interface
python3 web_interface_enhanced.py 