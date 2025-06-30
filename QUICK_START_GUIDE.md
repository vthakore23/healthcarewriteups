# 🚀 Healthcare Investment Intelligence - Quick Start Guide

## 🎯 How to Run the App

### Option 1: Web Dashboard (Recommended) 
**Easiest way to use the platform:**

```bash
./start_interface.sh
```

Then open your browser to: **http://localhost:5001**

You'll get a beautiful dashboard with:
- ✅ One-click daily analysis
- ✅ Real-time progress tracking  
- ✅ Download reports instantly
- ✅ Management Truth Tracker™
- ✅ FDA Decision Analyzer
- ✅ Executive credibility checking

### Option 2: Enhanced Command Line
**Full intelligence features:**

```bash
# Run comprehensive analysis with all intelligence features
python main_enhanced_intelligence.py --run-now

# Demo mode - see all features in action
python main_enhanced_intelligence.py --demo

# Check which executive promises are coming due
python main_enhanced_intelligence.py --check-promises

# Interactive demo of intelligence system
python demo_integrated_intelligence.py
```

### Option 3: Standard Command Line
**Traditional analysis:**

```bash
# Quick daily analysis
./run_daily_analysis.sh

# With intelligence features  
./run_with_intelligence.sh

# Standard optimized version
python main_optimized.py --demo
```

### Option 4: Executive Credibility Checker
**Standalone tool to research executives:**

```bash
# Search for executives or companies
python check_executive_credibility.py search "John Smith"

# Check specific executive credibility 
python check_executive_credibility.py check "John Smith" --company "BioPharma Inc"

# Check company-wide credibility
python check_executive_credibility.py company "BioPharma Inc"
```

---

## 🔄 Make It Permanent (Always Running)

**Want the app to run 24/7 without having to start it manually?**

### Step 1: Setup the Permanent Service

```bash
chmod +x setup_permanent_service.sh
./setup_permanent_service.sh
```

### Step 2: That's It! 

The service is now **permanently running** and will:
- ✅ **Start automatically** when you log in
- ✅ **Restart automatically** if it crashes
- ✅ **Web dashboard always available** at http://localhost:5001
- ✅ **Run daily analysis automatically** at 7:01 AM, 8:00 AM, 9:00 AM
- ✅ **Keep all intelligence features active** 24/7

### Permanent Service Features

Once set up, you get:

1. **Always-On Web Dashboard**
   - Access http://localhost:5001 anytime
   - No need to start anything manually

2. **Automatic Daily Analysis**
   - Runs at exactly 7:01 AM, 8:00 AM, 9:00 AM Eastern
   - Emails reports automatically
   - Generates 600-word summaries for every article

3. **24/7 Intelligence Services**
   - Management Truth Tracker™ always analyzing
   - FDA Decision Analyzer always ready
   - Executive credibility database always updated

4. **Auto-Restart Protection**
   - If service crashes, it automatically restarts
   - Never miss a day of analysis

---

## 🛠️ Service Management Commands

### Check if service is running:
```bash
launchctl list | grep healthcare
```

### Stop the permanent service:
```bash
launchctl unload ~/Library/LaunchAgents/com.healthcare.intelligence.plist
```

### Start the permanent service:
```bash
launchctl load ~/Library/LaunchAgents/com.healthcare.intelligence.plist
```

### View live logs:
```bash
tail -f healthcare_service.log
```

### Remove permanent service completely:
```bash
launchctl unload ~/Library/LaunchAgents/com.healthcare.intelligence.plist
rm ~/Library/LaunchAgents/com.healthcare.intelligence.plist
```

---

## 📊 What You Get

### Daily Automated Analysis
- ✅ **Every article gets 600-word summary** (not just selected ones)
- ✅ **5 required sections**: Company, Event, Summary, Standout Points, Additional Developments
- ✅ **1-2 most interesting articles** get additional deep analysis
- ✅ **Management credibility analysis** for every executive mentioned
- ✅ **FDA approval probability** for regulatory submissions

### Intelligence Features
- 🕵️ **Management Truth Tracker™**: Tracks what executives promise vs. deliver
- 📊 **FDA Decision Analyzer**: Predicts approval probability using historical patterns  
- 🚨 **Real-time Investment Alerts**: High-priority warnings
- 📅 **Promise Calendar**: Track upcoming deadlines for executive commitments
- 💡 **Executive Credibility Scores**: See who actually delivers on promises

### Professional Reports
- 📄 **Beautiful HTML reports** ready for sharing
- 📈 **Market intelligence** with real-time stock data
- 🔍 **Competitive analysis** and peer comparison
- ⚠️ **Risk factors** and investment warnings
- 💰 **Investment signals** and recommendations

---

## 🎯 Quick Decision Tree

**Just want to try it once?**
→ Run `./start_interface.sh` and go to http://localhost:5001

**Want to see all intelligence features?**
→ Run `python main_enhanced_intelligence.py --demo`

**Want it running 24/7 automatically?**
→ Run `./setup_permanent_service.sh`

**Want to research a specific executive?**
→ Run `python check_executive_credibility.py search "Executive Name"`

---

## 📞 Troubleshooting

### Web interface won't start:
```bash
# Check if port 5001 is available
lsof -i :5001

# Kill any existing processes
pkill -f "healthcare"

# Restart the service
./start_interface.sh
```

### Missing dependencies:
```bash
# Reinstall requirements
pip install -r requirements.txt

# Or run setup
python3 setup.py
```

### Service not starting automatically:
```bash
# Check service status
launchctl list | grep healthcare

# Reload the service
launchctl unload ~/Library/LaunchAgents/com.healthcare.intelligence.plist
launchctl load ~/Library/LaunchAgents/com.healthcare.intelligence.plist
```

---

## 🎉 Success!

Once running, you'll have:
- **Professional-grade healthcare investment intelligence**
- **Automated daily analysis** with 600-word summaries
- **Management accountability tracking**
- **FDA approval probability predictions**
- **Real-time market intelligence**
- **Beautiful web dashboard** always available

**Access your dashboard at: http://localhost:5001**

*The most advanced healthcare investment intelligence platform - now running permanently in the background!* 