#!/bin/bash
# View the latest Healthcare Intelligence Report

echo "🧬 Healthcare Intelligence Report Viewer"
echo "======================================="
echo ""

# Check if reports directory exists
if [ ! -d "reports" ]; then
    echo "❌ No reports directory found. Run the analysis first:"
    echo "   ./run_healthcare_intelligence.sh --once"
    exit 1
fi

# Find the latest text report
LATEST_REPORT=$(ls -t reports/healthcare_intelligence_*.txt 2>/dev/null | head -n1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ No reports found. Run the analysis first:"
    echo "   ./run_healthcare_intelligence.sh --once"
    exit 1
fi

# Extract date from filename
REPORT_DATE=$(basename "$LATEST_REPORT" | sed 's/healthcare_intelligence_//;s/.txt//')

echo "📄 Latest Report: $REPORT_DATE"
echo ""
echo "Options:"
echo "1) View in terminal (less)"
echo "2) View in terminal (cat)"
echo "3) Open in default text editor"
echo "4) Show file location only"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        less "$LATEST_REPORT"
        ;;
    2)
        cat "$LATEST_REPORT"
        ;;
    3)
        if command -v open &> /dev/null; then
            open "$LATEST_REPORT"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$LATEST_REPORT"
        else
            echo "Could not determine default text editor. Opening with 'vi'..."
            vi "$LATEST_REPORT"
        fi
        ;;
    4)
        echo ""
        echo "📁 Report location: $LATEST_REPORT"
        echo ""
        echo "You can open it with:"
        echo "  cat $LATEST_REPORT"
        echo "  less $LATEST_REPORT"
        echo "  open $LATEST_REPORT"
        ;;
    *)
        echo "Invalid option. Showing file location:"
        echo "📁 $LATEST_REPORT"
        ;;
esac 