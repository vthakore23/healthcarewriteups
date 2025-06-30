# 🧬 Daily Healthcare Intelligence System

A sophisticated automated system that analyzes healthcare and biotech news from lifesciencereport.com/newsroom, generating investment-grade summaries and analysis for decision makers.

## 🎯 Purpose

This system automates the daily review of healthcare/biotech news, providing:
- Structured 600-word summaries for each article
- Selection of 1-2 most interesting events
- In-depth analysis of why events matter and their implications
- Reports saved locally in the ./reports/ directory

## 🚀 Quick Start

### 1. Setup (One Time Only)

```bash
# Clone and enter directory
cd healthcarewriteups

# Copy environment template
cp env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### 2. Run the System

**Option A: Scheduled Mode (Default)**
```bash
./run_healthcare_intelligence.sh
```
Runs automatically at 7:01 AM, 8:00 AM, and 9:00 AM ET daily.

**Option B: Run Once Now**
```bash
./run_healthcare_intelligence.sh --once
```
Checks for today's news immediately and generates report.

### 3. Test the System

```bash
python3 test_healthcare_intelligence.py
```

## 📊 What It Does

### Daily Workflow

1. **Scrapes News** (7:01 AM, 8:00 AM, 9:00 AM ET)
   - Monitors lifesciencereport.com/newsroom
   - Identifies new healthcare/biotech articles
   - Avoids duplicate processing

2. **Generates Summaries** (~600 words each)
   - Company Name (with ticker)
   - News Event type
   - 5-sentence summary
   - Standout Points (detailed metrics)
   - Additional Developments

3. **Selects Interesting Events** (1-2 articles)
   - Uses AI to identify most significant news
   - Considers market impact, scientific importance

4. **Creates In-Depth Analysis**
   - Why the event is interesting
   - Longer-term implications
   - Additional research with citations

5. **Enhances with Intelligence**
   - Stock ticker data
   - FDA submission tracking
   - Management credibility scores

6. **Delivers Report**
   - Saves locally in reports/ directory
   - Creates both JSON and TXT formats

## 📁 Report Storage

Reports are saved locally in the `reports/` directory. No email functionality is currently enabled.

To view the latest report:
```bash
ls -la reports/
cat reports/healthcare_intelligence_*.txt
```

## 📁 Output Structure

Reports are saved in `reports/` directory:
- `healthcare_intelligence_YYYYMMDD_HHMMSS.json` - Structured data
- `healthcare_intelligence_YYYYMMDD_HHMMSS.txt` - Human-readable format

## 🔧 Configuration

### Required API Keys

Choose one AI provider:
- `OPENAI_API_KEY` - For GPT-4 summaries
- `ANTHROPIC_API_KEY` - For Claude summaries

### Optional Email Setup

Choose one email method:
- `SENDGRID_API_KEY` - Recommended for reliability
- SMTP credentials - For Gmail/Outlook

### Schedule Modification

Edit `config.py` to change check times:
```python
CHECK_TIMES = [
    time(7, 1),   # 7:01 AM ET
    time(8, 0),   # 8:00 AM ET
    time(9, 0),   # 9:00 AM ET
]
```

## 📋 Summary Format

Each article summary follows this exact structure:

```
Company Name: [Company with ticker]

News Event: [Event type]

News Summary:
[5 comprehensive sentences]

Standout Points:
[Detailed metrics, data, mechanisms - the meatiest section]

Additional Developments:
[Related strategic initiatives]
```

## 🔍 Analysis Format

Selected articles receive additional analysis:

1. **Why This Event is Interesting**
   - Unique aspects
   - Investment relevance

2. **Potential Implications**
   - Company impact
   - Market positioning
   - Long-term effects

3. **Additional Research**
   - External sources (cited)
   - Industry context
   - Comparable situations

## 🛠️ Troubleshooting

### No Articles Found
- Check if it's a weekday (fewer weekend updates)
- Verify lifesciencereport.com is accessible
- Check `healthcare_news.log` for errors

### Email Not Sending
- Verify EMAIL_ENABLED = True
- Check email credentials
- Reports always saved locally as backup

### AI Errors
- Verify API keys are set
- Check rate limits
- Ensure internet connectivity

## 📊 System Benefits

- **Time Savings**: 2-3 hours daily
- **Consistency**: Standardized analysis format
- **Intelligence**: AI-selected important events
- **Context**: External research included
- **Archive**: Complete report history

---

*Built for efficient healthcare investment intelligence* 