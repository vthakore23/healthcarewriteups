#!/bin/bash

# Healthcare Stock Ticker Intelligence - Quick Lookup
# Usage: ./ticker_lookup.sh TICKER

if [ -z "$1" ]; then
    echo "🧬 Healthcare Stock Ticker Intelligence"
    echo "======================================"
    echo ""
    echo "Usage: ./ticker_lookup.sh TICKER"
    echo ""
    echo "Examples:"
    echo "  ./ticker_lookup.sh MRNA    # Moderna"
    echo "  ./ticker_lookup.sh PFE     # Pfizer"
    echo "  ./ticker_lookup.sh JNJ     # Johnson & Johnson"
    echo "  ./ticker_lookup.sh GILD    # Gilead Sciences"
    echo "  ./ticker_lookup.sh BIIB    # Biogen"
    echo ""
    echo "Features:"
    echo "  • Company financial health"
    echo "  • Management credibility scores"
    echo "  • FDA submission tracking"
    echo "  • Recent developments"
    echo "  • Investment analysis"
    echo ""
    exit 1
fi

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the stock ticker intelligence
echo "🔍 Looking up $1..."
python3 stock_ticker_intelligence.py "$1" 