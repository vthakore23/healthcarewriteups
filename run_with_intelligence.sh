#!/bin/bash

# Healthcare Investment Intelligence - Daily Analysis Script
# Includes Management Truth Tracker™ and FDA Decision Pattern Analyzer

echo "🧬 Healthcare Investment Intelligence System"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Run the enhanced main script with intelligence features
echo ""
echo "Starting Healthcare Investment Intelligence Analysis..."
echo "This includes:"
echo "  ✓ Management Truth Tracker™ - Track executive promises vs delivery"
echo "  ✓ FDA Decision Pattern Analyzer - Predict approval probabilities"
echo "  ✓ Integrated Intelligence - Real-time credibility updates"
echo ""

# Run with current time check
HOUR=$(date +%H)

if [ "$1" == "--demo" ]; then
    echo "Running demo..."
    python3 demo_integrated_intelligence.py
elif [ "$1" == "--force" ] || [ "$HOUR" == "07" ] || [ "$HOUR" == "08" ] || [ "$HOUR" == "09" ]; then
    echo "Running full analysis with intelligence features..."
    python3 main_enhanced_intelligence.py --run-now
else
    echo "Note: Automated runs happen at 7:01 AM, 8:00 AM, and 9:00 AM"
    echo "Use --force to run now, or --demo for demonstration"
    echo ""
    echo "Starting in manual mode..."
    python3 main_enhanced_intelligence.py
fi

echo ""
echo "✅ Analysis complete!"
echo ""
echo "Check the following databases for intelligence data:"
echo "  • management_promises.db - Executive promise tracking"
echo "  • fda_decisions.db - FDA submission analysis"
echo "" 