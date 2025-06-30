# 🧬 Daily Healthcare Intelligence System Guide

## Overview

This system automates the daily analysis of healthcare and biotech news from [lifesciencereport.com/newsroom](https://lifesciencereport.com/newsroom), generating investment-grade summaries and in-depth analysis for the investment team.

## Key Features

### 📰 Automated News Monitoring
- **Source**: lifesciencereport.com/newsroom
- **Schedule**: Checks for new articles at 7:01 AM, 8:00 AM, and 9:00 AM ET
- **Focus**: Healthcare and biotech sector news only

### 📝 Investment-Grade Summaries
- **Length**: ~600 words per article (550-650 word range)
- **Structure**: Follows exact investment analysis format
- **Key Sections**:
  - Company Name (with ticker if available)
  - News Event (categorized)
  - News Summary (exactly 5 sentences)
  - Standout Points (meatiest section with all quantifiable data)
  - Additional Developments

### 🔍 Intelligent Article Selection
- Automatically selects 1-2 most interesting events from the day
- Considers:
  - Market impact potential
  - Scientific breakthrough significance
  - Financial implications
  - Strategic importance
  - Novelty of the development

### 💡 In-Depth Investment Analysis
For selected articles, provides additional analysis covering:
1. **Why This Event is Interesting**
   - What makes it stand out
   - Why investors should pay attention
   
2. **Potential Implications (Longer Term)**
   - Company impact (good, bad, or indifferent)
   - Competitive positioning
   - Market opportunities
   
3. **Additional Research & Insights**
   - External sources cited
   - Comparable companies
   - Market dynamics

### 📊 Enhanced Intelligence Features
- **Stock Ticker Intelligence**: Real-time price, market cap, financial health
- **FDA Tracking**: Submission status, approval rates, pipeline data
- **Management Credibility**: Truth Tracker™ scores
- **Clinical Trial Monitoring**: Active programs and phases

### 📁 Report Delivery
- **Primary**: Reports saved locally in reports/ directory
- **Format**: JSON (structured data) + TXT (human-readable)
- **Email**: Optional feature (currently disabled)

## Quick Start

### 1. One-Time Setup
```bash
# Clone repository (if needed)
git clone [repository-url]
cd healthcarewriteups

# Set up environment variables
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"

# For email delivery (optional)
export SENDGRID_API_KEY="your-sendgrid-key"
# OR SMTP credentials
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

### 2. Run Analysis

#### Option A: Run on Schedule (Default)
```bash
./run_healthcare_intelligence.sh
```
This will:
- Check for news at 7:01 AM, 8:00 AM, and 9:00 AM ET daily
- Generate summaries and analysis
- Email reports to the investment team
- Continue running until stopped (Ctrl+C)

#### Option B: Run Once Immediately
```bash
./run_healthcare_intelligence.sh --once
```
This will:
- Check for today's news immediately
- Generate complete report
- Send email and exit

## System Architecture

```
Daily Healthcare Intelligence System
├── Scraping Layer
│   ├── lifesciencereport.com/newsroom monitoring
│   ├── Intelligent article extraction
│   └── Daily deduplication
│
├── AI Analysis Layer
│   ├── 600-word structured summaries
│   ├── Article selection (1-2 most interesting)
│   └── In-depth investment analysis
│
├── Enhancement Layer
│   ├── Stock ticker intelligence
│   ├── FDA database integration
│   └── Management credibility scoring
│
└── Delivery Layer
    ├── HTML/Text email generation
    ├── Automated sending
    └── Local report archival
```

## Configuration

### Email Recipients
Edit `config.py` to update recipients:
```python
EMAIL_RECIPIENTS = ['email1@company.com', 'email2@company.com']
```

### Schedule Times
Modify check times in `config.py`:
```python
CHECK_TIMES = [
    time(7, 1),   # 7:01 AM ET
    time(8, 0),   # 8:00 AM ET
    time(9, 0),   # 9:00 AM ET
]
```

### AI Model Selection
Choose between OpenAI and Anthropic:
```python
AI_MODEL = 'gpt-4-turbo-preview'  # or 'claude-3-opus-20240229'
```

## Report Structure

### Daily Email Contains:

1. **Header Statistics**
   - Total articles analyzed
   - Number selected for deep analysis
   - Date and source

2. **Article Summaries** (All articles)
   - Company name with ticker
   - News event type
   - 5-sentence summary
   - Standout points (detailed metrics)
   - Additional developments
   - Stock intelligence (if available)

3. **In-Depth Analysis** (1-2 selected articles)
   - Why the event is interesting
   - Longer-term implications
   - Additional research with citations

## Troubleshooting

### No Articles Found
- Check if lifesciencereport.com is accessible
- Verify it's a weekday (fewer updates on weekends)
- Check scraper logs in `healthcare_news.log`

### Email Not Sending
- Verify EMAIL_ENABLED = True in config.py
- Check SendGrid API key or SMTP credentials
- Reports are always saved locally in `reports/` directory

### AI Errors
- Ensure API keys are set correctly
- Check API rate limits
- Verify internet connectivity

## Manual Operations

### View Latest Report
```bash
ls -la reports/
cat reports/healthcare_intelligence_[latest].txt
```

### Check System Logs
```bash
tail -f healthcare_news.log
```

### Test Scraper Only
```python
from scraper import LifeScienceScraper
scraper = LifeScienceScraper()
articles = scraper.get_todays_articles()
print(f"Found {len(articles)} articles today")
```

## Investment Value

This system provides:
- **Time Savings**: 2-3 hours daily of manual news review
- **Consistency**: Standardized 600-word summaries
- **Intelligence**: AI-selected most important events
- **Context**: External research and citations
- **Tracking**: Historical archive of all reports

## Support

For issues or enhancements:
1. Check `healthcare_news.log` for errors
2. Verify all API keys are set
3. Ensure Python 3.8+ is installed
4. Reports are always saved locally even if email fails

---

*Built for efficient healthcare investment intelligence - focusing on what matters for investment decisions* 