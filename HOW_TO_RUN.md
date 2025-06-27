# How to Run Healthcare News Automation

This app analyzes healthcare news each morning and generates comprehensive reports that you can download and send to your team.

## 🚀 Quick Start (Web Interface - Recommended!)

Launch the beautiful web interface:
```bash
./start_interface.sh
```

This will:
- Start a web interface at http://localhost:5000
- Let you run analysis with a single click
- Show real-time progress updates
- Allow you to view and download reports instantly

## 📋 Command Line Option

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
- **One-click analysis** - Just click "Run Full Analysis"
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

Complete healthcare news automation with amazing reports:

1. ✅ **Smart article discovery** - Automatically finds new articles from lifesciencereport.com
2. ✅ **Professional summaries** - Generates 600-word structured analysis for each article
3. ✅ **Intelligent selection** - Picks 1-2 most interesting events automatically  
4. ✅ **Deep analysis** - Provides detailed investment-focused insights
5. ✅ **Beautiful reports** - Creates stunning HTML reports you can send directly
6. ✅ **Multiple formats** - Generates both HTML (beautiful) and JSON (data) reports
7. ✅ **Web interface** - Easy-to-use dashboard for running analysis and downloading reports

**Key Features:**
- 🚀 **One-click operation** through web interface
- 📊 **Real-time progress tracking** 
- 📁 **Automatic report management**
- 💎 **Professional, investment-grade analysis**
- 🕐 **Can run on schedule** (7:01 AM, 8:00 AM, 9:00 AM ET)

The reports are ready to send - just download and forward to your team! 