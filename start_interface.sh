#!/bin/bash
# Healthcare News Automation - Web Interface Launcher
# Beautiful, easy-to-use interface for running analysis and downloading reports

echo "🚀 HEALTHCARE NEWS AUTOMATION"
echo "   Web Interface Launcher"
echo "================================"
echo ""

# Navigate to project directory and activate virtual environment
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "🌐 Starting Healthcare News Automation Interface..."
echo "📊 You can access the interface at: http://localhost:5001"
echo "💡 Use the web interface to:"
echo "   • Run full healthcare news analysis"
echo "   • View and download reports"
echo "   • Monitor analysis progress in real-time"
echo ""
echo "🔄 The interface will open automatically..."
echo "   Press Ctrl+C to stop the server"
echo ""

# Open browser automatically (works on macOS)
sleep 3 && open http://localhost:5001 &

# Start the Flask web interface
python3 web_interface.py 