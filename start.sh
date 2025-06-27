#!/bin/bash
# Healthcare News Automation - Quick Start Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Running setup..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Set Python alias for consistency
alias python=python3

# Show menu
echo ""
echo "======================================================"
echo "   HEALTHCARE NEWS AUTOMATION - OPTIMIZED VERSION"
echo "======================================================"
echo ""
echo "Select an option:"
echo "1) Run demo (3 articles)"
echo "2) Run full analysis (no email)"
echo "3) Run with email"
echo "4) Run on schedule"
echo "5) Test email configuration"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "Running demo mode..."
        python main_optimized.py --demo
        ;;
    2)
        echo "Running full analysis (no email)..."
        python main_optimized.py --local-only
        ;;
    3)
        echo "Running with email..."
        python main_optimized.py --run-now
        ;;
    4)
        echo "Running on schedule..."
        python main_optimized.py --schedule
        ;;
    5)
        echo "Testing email..."
        python main_optimized.py --test-email
        ;;
    *)
        echo "Invalid choice. Running demo mode..."
        python main_optimized.py --demo
        ;;
esac 