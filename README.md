# 🧬 Healthcare Writeups

**AI-powered daily healthcare news analysis platform that generates comprehensive investment intelligence writeups from Life Science Report and other healthcare sources.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI GPT-4](https://img.shields.io/badge/AI-GPT--4-orange.svg)](https://openai.com/)

## ✨ Features

- 🚀 **One-Click Analysis** - Beautiful web interface for easy operation
- 📊 **Real-Time Progress** - Live updates during analysis
- 💎 **Investment-Grade Reports** - Professional 600-word structured summaries
- 🎯 **Smart Article Selection** - Automatically identifies most interesting events
- 📱 **Modern Web Interface** - Clean, responsive dashboard
- 📁 **Multiple Export Formats** - HTML (beautiful) and JSON (data) reports
- 🕐 **Scheduled Analysis** - Runs at 7:01 AM, 8:00 AM, 9:00 AM ET
- ⚡ **Optimized Performance** - Parallel processing for 3-5x faster analysis

## 🎯 What It Does

1. **Discovers New Articles** - Automatically scrapes lifesciencereport.com/newsroom
2. **Generates Professional Summaries** - Creates 600-word structured analysis for each article
3. **Intelligent Event Selection** - Picks 1-2 most interesting developments
4. **Deep Investment Analysis** - Provides detailed insights on implications and opportunities
5. **Beautiful Report Generation** - Creates stunning HTML reports ready to share
6. **Real-Time Dashboard** - Monitor progress and download reports instantly

## 🚀 Quick Start

### Web Interface (Recommended)
```bash
./start_interface.sh
```
Opens at `http://localhost:5000` with:
- One-click analysis execution
- Real-time progress tracking
- Report management dashboard
- Instant download capabilities

### Command Line
```bash
./run_daily_analysis.sh
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vthakore23/healthcare-news-automation.git
   cd healthcare-news-automation
   ```

2. **Set up environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

4. **Run the application**
   ```bash
   ./start_interface.sh
   ```

## 📋 Report Structure

Each analysis includes:

### Article Summaries
- **Company Name** - Target organization
- **News Event** - Type of development (earnings, data release, partnership, etc.)
- **News Summary** - 5-sentence overview with key figures and implications
- **Standout Points** - Quantifiable data and unique aspects affecting valuation
- **Additional Developments** - Related partnerships, acquisitions, collaborations

### Deep Analysis
- **Investment Significance** - Why the event matters to investors
- **Potential Implications** - Long-term financial and competitive impacts
- **Additional Insights** - Industry context, technical background, precedents

## 🔧 Configuration

Key settings in `config.py`:
- **Schedule Times** - Customize analysis schedule
- **Word Counts** - Adjust summary lengths
- **AI Models** - Switch between GPT-4 and Claude
- **Article Filtering** - Configure source parameters

## 📁 Output Files

Reports are saved in the `reports/` directory:
- `report_YYYY-MM-DD.html` - Beautiful formatted report
- `report_YYYY-MM-DD.json` - Raw data for further processing

## 🛡️ Security

- API keys stored in environment variables
- No sensitive data committed to repository
- Local processing ensures data privacy
- Comprehensive .gitignore for security

## 🚀 Performance

- **Parallel Processing** - 3-5x faster than sequential analysis
- **Smart Caching** - Avoids reprocessing duplicate articles
- **Rate Limit Handling** - Automatic retry with exponential backoff
- **Memory Efficient** - Optimized for large-scale article processing

## 📊 Tech Stack

- **Backend** - Python 3.8+, Flask
- **AI** - OpenAI GPT-4, Anthropic Claude
- **Web Scraping** - BeautifulSoup, Selenium
- **Frontend** - HTML5, CSS3, Vanilla JavaScript
- **Data** - JSON, HTML export formats

## 🕐 Scheduling

For automated daily analysis:
```bash
python3 main_optimized.py --schedule
```

Runs automatically at:
- 7:01 AM Eastern Time
- 8:00 AM Eastern Time  
- 9:00 AM Eastern Time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions or issues:
1. Check the [Issues](https://github.com/vthakore23/healthcare-news-automation/issues) page
2. Create a new issue with detailed information
3. Include logs and error messages when applicable

---

**Built for healthcare investment professionals who need reliable, comprehensive news analysis.** 