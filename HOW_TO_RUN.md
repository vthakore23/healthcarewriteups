# How to Run Healthcare Investment Intelligence Platform

This app analyzes healthcare news each morning and generates comprehensive investment-grade reports with **groundbreaking intelligence features** including Management Truth Tracking™, FDA Decision Pattern Analysis, and **NEW Stock Ticker Intelligence**.

## 🆕 Stock Ticker Intelligence (NEW!)

Get instant, comprehensive intelligence on any healthcare/biotech stock:

### Quick Lookup
```bash
./ticker_lookup.sh MRNA   # Get Moderna intelligence report
```

### Enhanced Web Interface with Stock Search
```bash
./start_enhanced_interface.sh
```
Then visit http://localhost:5001 and use the stock ticker search feature!

### What You Get:
- 📊 **Real-time financials** - Market cap, cash burn, runway
- 🕵️ **Management credibility** - Truth Tracker™ scores
- 🧬 **FDA intelligence** - Submission history & approval rates
- 💊 **Pipeline analysis** - Clinical programs & milestones
- 📈 **Investment analysis** - Risk assessment & recommendations

Try these popular tickers: MRNA, PFE, JNJ, GILD, BIIB, REGN, VRTX

## 🚀 Quick Start (Web Interface - Recommended!)

Launch the beautiful web interface:
```bash
./start_interface.sh
```

This will:
- Start a web interface at http://localhost:5001
- Let you run analysis with a single click
- Show real-time progress updates
- Allow you to view and download reports instantly

## 🧬 NEW! Enhanced Intelligence Analysis

Run with Management Truth Tracker™ & FDA Decision Analyzer:
```bash
# Full intelligence analysis with all features
python main_enhanced_intelligence.py --run-now

# Demo mode - see intelligence features in action
python main_enhanced_intelligence.py --demo

# Check which executive promises are coming due
python main_enhanced_intelligence.py --check-promises

# Run interactive intelligence demo
python demo_integrated_intelligence.py
```

### Intelligence Features:
- **🕵️ Management Truth Tracker™** - Tracks what executives promise vs. deliver
- **📊 FDA Decision Analyzer** - Predicts approval probability using historical patterns
- **🚨 Real-time Alerts** - High-priority investment warnings
- **📅 Promise Calendar** - Track upcoming deadlines for executive commitments

## 📋 Standard Command Line Options

For direct command line usage:
```bash
./run_daily_analysis.sh
```

This will:
- Check lifesciencereport.com/newsroom for new articles
- Generate 600-word summaries for each article
- Select 1-2 most interesting events for additional analysis  
- Create comprehensive reports for download

## 📅 For Daily Automation

To run automatically at 7:01 AM, 8:00 AM, and 9:00 AM Eastern Time:

```bash
source venv/bin/activate
python3 main_optimized.py --schedule
```

This will keep running and automatically execute at the scheduled times.

## 🧪 For Testing

To test with just a few articles (no email):
```bash
source venv/bin/activate  
python3 main_optimized.py --demo
```

## 🌐 Web Interface Features

The web interface provides:
- **One-click analysis** - Just click "Generate Daily Writeups"
- **Real-time progress** - Watch the analysis progress with live updates
- **Report management** - View all your reports in one place
- **Instant download** - Download HTML or JSON reports immediately
- **Beautiful presentation** - Clean, professional interface

## 📁 Where to Find Reports

Reports are saved in the `reports/` folder:
- `report_YYYY-MM-DD.html` - Beautiful formatted report
- `report_YYYY-MM-DD.json` - Raw data

## 🔧 If Python Command Not Found

If you get "command not found: python", use:
```bash
python3 instead of python
```

## ✅ What the App Does

Complete healthcare news automation with investment-grade analysis:

1. ✅ **Smart article discovery** - Automatically finds new articles from lifesciencereport.com/newsroom
2. ✅ **Professional summaries** - Generates 600-word structured analysis for each article
3. ✅ **Intelligent selection** - Picks 1-2 most interesting events automatically  
4. ✅ **Deep analysis** - Provides detailed investment-focused insights
5. ✅ **Beautiful reports** - Creates stunning HTML reports ready for sharing
6. ✅ **Multiple formats** - Generates both HTML (beautiful) and JSON (data) reports
7. ✅ **Web interface** - Easy-to-use dashboard for running analysis and downloading reports

**Key Features:**
- 🚀 **One-click operation** through web interface
- 📊 **Real-time progress tracking** 
- 📁 **Automatic report management**
- 💎 **Professional, investment-grade analysis**
- 🕐 **Can run on schedule** (7:01 AM, 8:00 AM, 9:00 AM ET)

## 📋 Report Structure

Each article summary includes:

**Required Sections (600 words total):**
- **Company Name** - Company with ticker if available
- **News Event** - Type of development (e.g., Data Release, Partnership, etc.)
- **News Summary** - 5-sentence overview with key figures and implications
- **Standout Points** - The "meatiest" section with ALL quantifiable data:
  - Exact percentages, patient numbers, p-values
  - Financial figures and market size
  - Clinical trial details and timelines
  - Safety profiles and efficacy data
  - Mechanism of action explanations
- **Additional Developments** - Related partnerships, collaborations, strategic initiatives

**Additional Analysis (for selected articles):**
- **Why This Event is Interesting** - What makes it stand out
- **Potential Implications** - Longer-term impact analysis
- **Additional Research** - External insights with source citations

## 🔍 Verify Requirements

To verify all requirements are properly implemented:
```bash
python3 verify_requirements.py
```

This will check:
- ✅ Correct schedule times (7:01 AM, 8:00 AM, 9:00 AM)
- ✅ 600-word summary generation
- ✅ All required sections present
- ✅ "Standout Points" as meatiest section
- ✅ 1-2 article selection logic
- ✅ 400-600 word additional analysis

The reports are ready to download and share - comprehensive investment intelligence at your fingertips! 