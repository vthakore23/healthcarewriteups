#!/bin/bash

# Setup script for Healthcare Investment Intelligence Permanent Service
# This configures the service to start automatically on macOS

echo "🛠️  Healthcare Investment Intelligence - Permanent Service Setup"
echo "=============================================================="
echo ""

# Get current directory
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PLIST_FILE="com.healthcare.intelligence.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "📁 Current directory: $CURRENT_DIR"
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x start_permanent_service.sh
chmod +x healthcare_service.py

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "📂 Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Update the plist file with correct paths
echo "📝 Configuring service paths..."
sed "s|REPLACE_WITH_FULL_PATH|$CURRENT_DIR|g" "$PLIST_FILE" > "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "✅ Configuration updated with paths:"
echo "   Working Directory: $CURRENT_DIR"
echo "   Service Script: $CURRENT_DIR/start_permanent_service.sh"
echo "   Log File: $CURRENT_DIR/healthcare_service.log"
echo ""

# Load the service
echo "🚀 Loading the service..."
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null  # Unload if already loaded
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Check if service is loaded
if launchctl list | grep -q "com.healthcare.intelligence"; then
    echo "✅ Service loaded successfully!"
    echo ""
    echo "🎯 Your Healthcare Investment Intelligence Platform is now permanent!"
    echo ""
    echo "What this means:"
    echo "  • The service will start automatically when you log in"
    echo "  • If it crashes, it will automatically restart"
    echo "  • Web dashboard always available at: http://localhost:5001"
    echo "  • Daily analysis runs automatically at 7:01 AM, 8:00 AM, 9:00 AM"
    echo ""
    echo "📊 Access your dashboard: http://localhost:5001"
    echo "📝 View logs: tail -f $CURRENT_DIR/healthcare_service.log"
    echo ""
    echo "🛠️  Service Management Commands:"
    echo "   Start:   launchctl load $LAUNCH_AGENTS_DIR/$PLIST_FILE"
    echo "   Stop:    launchctl unload $LAUNCH_AGENTS_DIR/$PLIST_FILE"
    echo "   Status:  launchctl list | grep healthcare"
    echo ""
else
    echo "❌ Failed to load service. Check the configuration."
    exit 1
fi

# Give the service a moment to start
echo "⏳ Starting service..."
sleep 3

# Check if the web interface is responding
echo "🌐 Checking web interface..."
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Web interface is running!"
    echo ""
    echo "🎉 Setup complete! Your dashboard is ready at:"
    echo "   👉 http://localhost:5001"
else
    echo "⚠️  Web interface may take a moment to start."
    echo "   Check http://localhost:5001 in a few seconds"
fi

echo ""
echo "=============================================================="
echo "🎯 Healthcare Investment Intelligence Platform is now PERMANENT!"
echo "   • Always running in the background"
echo "   • Automatic daily analysis"  
echo "   • Web dashboard always available"
echo "   • Management Truth Tracker™ always active"
echo "   • FDA Decision Analyzer always ready"
echo "==============================================================" 