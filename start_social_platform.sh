#!/bin/bash

echo "🚀 Starting Healthcare Intelligence Platform with Social Media Sentiment Analysis"
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade requirements
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data if needed
echo "Setting up NLTK data..."
python3 -c "import nltk; nltk.download('vader_lexicon', quiet=True)"

# Initialize databases if needed
echo "Initializing databases..."
python3 -c "from social_media_sentiment import SocialMediaSentimentAnalyzer; analyzer = SocialMediaSentimentAnalyzer()"

# Start the web interface
echo ""
echo "🌟 Starting web interface..."
echo "=============================================================="
echo "Platform will be available at: http://localhost:5001"
echo ""
echo "Features available:"
echo "✅ Social Media Sentiment Analysis (Reddit, Twitter, Forums)"
echo "✅ Stock Ticker Intelligence"
echo "✅ Executive Credibility Tracker"
echo "✅ FDA Decision Predictions"
echo ""
echo "API Keys configured:"
echo "✅ News API: Configured"
echo "✅ Twitter API: Configured"
echo "⚠️  Reddit API: Pending (using demo mode)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================================="

# Run the enhanced web interface
python3 web_interface_social.py 