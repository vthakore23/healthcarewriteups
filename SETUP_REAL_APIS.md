# Setting Up Real Social Media APIs

## Quick Start

To get real tweets and social media data instead of demo data, you need API credentials from the following platforms:

## 1. Twitter/X API Setup

### Steps to get Twitter API credentials:

1. Go to https://developer.twitter.com/
2. Sign up for a developer account (Free tier available)
3. Create a new App in the developer portal
4. Generate your credentials:
   - API Key
   - API Secret Key
   - Bearer Token
   - Access Token
   - Access Token Secret

### Add to your .env file:
```
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_SECRET=your-access-secret
```

## 2. Reddit API Setup

### Steps to get Reddit API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - Name: Healthcare Intelligence Bot
   - App type: Select "script"
   - Description: Healthcare sentiment analysis
   - Redirect URI: http://localhost:8080
4. Create the app and note your credentials

### Add to your .env file:
```
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=Healthcare Intelligence Bot 1.0
```

## 3. Create .env File

Create a file named `.env` in the project root with all your credentials:

```bash
# Copy from env.example and fill in your actual values
cp env.example .env
```

Then edit `.env` and add your real API credentials.

## 4. Verify Setup

Run this command to test your API connections:
```bash
python3 test_apis.py
```

## Important Notes

- **Twitter API Limits**: Free tier allows 500,000 tweets/month
- **Reddit API Limits**: 60 requests per minute
- **Keep your .env file private**: Never commit it to version control
- The system will automatically switch to real data when valid credentials are detected

## Troubleshooting

If you're still seeing demo data after adding credentials:
1. Make sure `USE_DEMO_MODE = False` in `api_config.py`
2. Restart the application
3. Check the console logs for any API authentication errors

## Alternative: Using Only Financial/News APIs

If you don't want to set up social media APIs, you can still get real data from:
- Stock price data (FMP, Alpha Vantage)
- News articles (News API)
- FDA data (public database)

These work without Twitter/Reddit credentials. 