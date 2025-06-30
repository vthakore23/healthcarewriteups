#!/bin/bash

# Healthcare Intelligence Platform Launcher

echo "Starting Enhanced Healthcare Intelligence Platform..."

# Check if port 5001 is in use and kill any existing processes
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 5001 is in use. Stopping existing processes..."
    lsof -Pi :5001 -sTCP:LISTEN -t | xargs kill -9
    sleep 1
fi

# Start the enhanced platform
echo "Launching enhanced web interface on http://localhost:5001/"
python3 web_interface_enhanced_social.py 