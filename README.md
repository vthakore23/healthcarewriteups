# 🧬 Healthcare Investment Intelligence Platform

A comprehensive real-time intelligence platform for pharmaceutical and biotech investment analysis, providing **social sentiment analysis**, **stock intelligence**, and **executive credibility tracking** - all powered by real APIs with no demo data.

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repository-url>
cd healthcarewriteups
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp env.example .env
# Edit .env with your API keys:
# - TWITTER_BEARER_TOKEN (required for Twitter data)
# - ANTHROPIC_API_KEY (required for AI analysis)
# - OPENAI_API_KEY (optional backup AI)
# - NEWS_API_KEY (optional news data)
```

### 3. Run Platform
```bash
./run_platform.sh
# Access: http://localhost:5001
```

## 📊 Platform Features

### 🐦 Social Sentiment Analysis
- **Real Twitter API v2** integration with Bearer Token
- **Reddit web scraping** (50+ posts per drug query)
- **StockTwits financial sentiment**
- **Enhanced content filtering** for medical relevance
- **Real-time sentiment scoring** with Claude AI

### 📈 Stock Intelligence  
- **Multi-source stock data** with smart fallbacks
- **Real-time price analysis** via yfinance + web scraping
- **Technical indicators** (moving averages, volatility)
- **Investment signals** (Buy/Sell/Hold recommendations)
- **Rate limit handling** with multiple data sources

### 👔 Executive Credibility
- **Real executive data** from company filings
- **Recent news analysis** for executive mentions
- **Multi-source data collection** (yfinance + news APIs)
- **Company metrics integration**

## 🔧 Technical Architecture

### Core Components
- **Flask Web Framework** - REST APIs + web interface
- **Real-time Data Sources** - Twitter, Reddit, yfinance, news APIs
- **AI Analysis** - Anthropic Claude + OpenAI GPT integration
- **Smart Caching** - SQLite databases for performance
- **Rate Limiting** - Intelligent backoff and fallback strategies

### Data Flow
1. **Input**: Drug name or stock ticker
2. **Collection**: Multi-platform real-time data gathering
3. **Filtering**: Medical relevance validation
4. **Analysis**: AI-powered sentiment and trend analysis
5. **Output**: Interactive dashboard with charts and insights

## 📋 API Endpoints

### Social Sentiment
- `GET /api/drug_sentiment_with_posts/{drug_name}` - Complete sentiment analysis
- `GET /api/search_drugs?q={query}` - Drug name search

### Stock Intelligence
- `GET /api/search_ticker?ticker={symbol}` - Stock analysis
- Returns: Real-time price, technical indicators, investment signals

### Executive Credibility
- `GET /api/executive_credibility/{ticker}` - Executive analysis
- Returns: Executive data, recent news, company metrics

## 🌟 Key Differentiators

### ✅ **100% Real Data**
- No demo data or mock responses
- All results from live APIs and web scraping
- Real-time social media sentiment analysis

### ✅ **Advanced Rate Limiting**
- Smart fallback data sources
- Intelligent backoff strategies
- Multiple API redundancy

### ✅ **Medical Context Filtering**
- Spam and promotional content removal
- Medical relevance scoring
- Context extraction for drug discussions

### ✅ **Comprehensive Coverage**
- Social media (Twitter, Reddit, StockTwits)
- Financial data (real-time stock prices)
- Executive intelligence (news + filings)
- AI-powered analysis and insights

## 🛠 Installation & Setup

### Prerequisites
- Python 3.9+
- Active internet connection
- API keys (see Configuration section)

### Dependencies
```bash
# Core dependencies
flask>=2.0.0
pandas>=1.3.0
numpy>=1.21.0
yfinance>=0.2.0
tweepy>=4.0.0
anthropic>=0.5.0
beautifulsoup4>=4.10.0
plotly>=5.0.0
requests>=2.25.0
```

### Configuration
1. **Twitter API** - Get Bearer Token from developer.twitter.com
2. **Anthropic API** - Get API key from console.anthropic.com  
3. **Optional APIs** - OpenAI, News API for enhanced functionality

## 📈 Usage Examples

### Social Sentiment Analysis
```bash
# Search for drug sentiment
curl "http://localhost:5001/api/drug_sentiment_with_posts/Ozempic"

# Returns: Real tweets, Reddit posts, sentiment analysis, charts
```

### Stock Intelligence
```bash
# Get stock analysis
curl "http://localhost:5001/api/search_ticker?ticker=MRNA"

# Returns: Real-time price, technical analysis, investment signals
```

### Executive Credibility
```bash
# Analyze executives
curl "http://localhost:5001/api/executive_credibility/PFE"

# Returns: Executive data, recent news, company metrics
```

## 🚀 Deployment

### Local Development
```bash
python3 web_interface_enhanced_social.py
```

### Production Deployment
```bash
# Use a production WSGI server
gunicorn --bind 0.0.0.0:5001 web_interface_enhanced_social:app
```

## 📊 Project Structure
```
healthcarewriteups/
├── web_interface_enhanced_social.py  # Main Flask application
├── social_media_sentiment.py        # Sentiment analysis engine
├── real_data_scraper.py             # Multi-platform data scraper
├── stock_ticker_intelligence.py     # Stock analysis engine
├── templates/                       # Frontend templates
├── cache/                          # Data cache
├── reports/                        # Generated reports
└── requirements.txt                # Dependencies
```

## 🔍 Troubleshooting

### Common Issues
1. **Twitter API Rate Limits** - Platform implements 60s backoff automatically
2. **Stock Data Rate Limits** - Multiple fallback sources implemented
3. **Missing API Keys** - Check .env file configuration
4. **No Data Found** - Verify ticker symbols and drug names

### Debug Mode
```bash
export FLASK_DEBUG=1
python3 web_interface_enhanced_social.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API setup documentation
3. Open an issue on GitHub

---

**Built with real data, real APIs, and real intelligence for healthcare investment decisions.** 