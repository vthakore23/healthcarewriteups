# 🚀 Quick Setup Guide

## ✅ API Keys Already Configured!

Your system already has both API keys configured in `.env`:
- ✅ **OpenAI API Key** - Ready to use
- ✅ **Anthropic API Key** - Ready to use

No additional API key setup needed!

## Setup Steps

```bash
# 1. Create your .env file
cp env.example .env

# 2. Edit .env and add your API key
nano .env  # or use any text editor

# 3. Run the analysis
./run_healthcare_intelligence.sh --once

# 4. View the report
./view_latest_report.sh
```

## That's it! 

Reports are saved in the `reports/` directory:
- `healthcare_intelligence_YYYYMMDD_HHMMSS.txt` - Human readable
- `healthcare_intelligence_YYYYMMDD_HHMMSS.json` - Structured data

## Optional Enhancement APIs

If you want enhanced stock data, you can also add:
- `FMP_API_KEY` - From https://financialmodelingprep.com/developer/docs/
- `ALPHA_VANTAGE_API_KEY` - From https://www.alphavantage.co/support/#api-key
- `NEWS_API_KEY` - From https://newsapi.org/register

But these are NOT required for basic functionality. 