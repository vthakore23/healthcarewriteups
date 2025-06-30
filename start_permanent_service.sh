#!/bin/bash

# Healthcare Investment Intelligence - Permanent Service Starter
# This script starts the service that runs continuously

echo "🎯 Healthcare Investment Intelligence Platform"
echo "=============================================="
echo "Starting permanent service..."
echo ""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 setup.py"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required modules are installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, requests, beautifulsoup4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Make the service script executable
chmod +x healthcare_service.py

echo "🚀 Starting Healthcare Investment Intelligence Service..."
echo ""
echo "Features that will be available:"
echo "  ✅ Web Dashboard: http://localhost:5001"
echo "  ✅ Management Truth Tracker™"
echo "  ✅ FDA Decision Analyzer"
echo "  ✅ Automatic daily analysis (7:01 AM, 8:00 AM, 9:00 AM)"
echo "  ✅ Real-time market intelligence"
echo "  ✅ Executive credibility checking"
echo ""
echo "📊 Access your dashboard at: http://localhost:5001"
echo "📝 Service logs saved to: healthcare_service.log"
echo ""
echo "🛑 Press Ctrl+C to stop the service"
echo "=============================================="
echo ""

# Start the permanent service
python3 healthcare_service.py 