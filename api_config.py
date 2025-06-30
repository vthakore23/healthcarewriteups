"""
API Configuration for Social Media Sentiment Analysis
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Healthcare Intelligence Bot 1.0')

# Twitter/X API
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'aYk8ON0651HwWCeGddiAXOyY3')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')

# News API
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '6f3c4287-b498-473b-b9bd-2f49978c4e4f')

# Reddit Configuration
REDDIT_SUBREDDITS = {
    'healthcare': [
        'medicine', 'pharmacy', 'biotech', 'pharma', 'healthcare',
        'AskDocs', 'ChronicPain', 'migraine', 'diabetes', 'cancer',
        'MultipleSclerosis', 'rheumatoid', 'CrohnsDisease', 'Psoriasis',
        'ADHD', 'bipolar', 'depression', 'anxiety'
    ],
    'investment': [
        'biotechstocks', 'stocks', 'investing', 'wallstreetbets',
        'SecurityAnalysis', 'StockMarket'
    ],
    'disease_specific': [
        'Epilepsy', 'Fibromyalgia', 'lupus', 'CysticFibrosis',
        'Hemophilia', 'rarediseases', 'invisibleillness'
    ]
}

# Date Range Configuration
DATA_START_DATE = "2023-01-01"  # Start of data collection
DATA_END_DATE = "2024-12-31"    # End of data collection

# Data Types Configuration
REDDIT_DATA_TYPES = {
    'posts': True,          # Collect posts/submissions
    'comments': True,       # Collect comments
    'user_attributes': {    # User data to collect
        'karma': True,
        'account_age': True,
        'verified': True
    },
    'subreddit_attributes': {  # Subreddit data
        'subscribers': True,
        'created_date': True,
        'description': True
    }
}

# Rate Limiting
REDDIT_REQUESTS_PER_MINUTE = 60
TWITTER_REQUESTS_PER_15MIN = 300

# Demo Mode
USE_DEMO_MODE = False  # Real mode - ALWAYS use real data when available 