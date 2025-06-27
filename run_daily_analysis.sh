#!/bin/bash
# Simple script to run daily healthcare news analysis
# This automates the complete healthcare news workflow

echo "🏥 HEALTHCARE NEWS AUTOMATION"
echo "Daily Analysis for Healthcare Team"
echo "================================"
echo ""

# Navigate to project directory and activate virtual environment
cd "$(dirname "$0")"
source venv/bin/activate

echo "📊 Running daily healthcare news analysis..."
echo "• Checking lifesciencereport.com/newsroom for new articles"
echo "• Generating 600-word summaries for each article" 
echo "• Selecting 1-2 most interesting events for additional analysis"
echo "• Generating comprehensive reports for download"
echo ""

# Run the production analysis
python3 run_production.py

echo ""
echo "✅ Daily analysis complete!"
echo "" 