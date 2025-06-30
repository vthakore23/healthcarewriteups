#!/bin/bash
# Daily Healthcare Intelligence System Startup Script
# Analyzes healthcare/biotech news from lifesciencereport.com/newsroom

echo "🧬 Daily Healthcare Intelligence System"
echo "======================================"
echo "📰 Source: lifesciencereport.com/newsroom"
echo "📁 Output: Reports saved to ./reports/ directory"
echo "⏰ Schedule: 7:01 AM, 8:00 AM, 9:00 AM ET"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for API keys
echo ""
echo "🔑 Checking configuration..."

if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: No AI API key found!"
    echo "   Set either OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable"
    echo ""
fi

echo "📁 Reports will be saved in the ./reports/ directory"
echo ""

# Parse command line arguments
if [ "$1" = "--once" ]; then
    echo "🚀 Running one-time analysis..."
    python3 daily_healthcare_intelligence.py --once
elif [ "$1" = "--help" ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --once    Run analysis once immediately"
    echo "  --help    Show this help message"
    echo ""
    echo "Default: Run on schedule (7:01 AM, 8:00 AM, 9:00 AM ET)"
else
    echo "🏃 Starting scheduled service..."
    echo "   Press Ctrl+C to stop"
    echo ""
    python3 daily_healthcare_intelligence.py
fi 