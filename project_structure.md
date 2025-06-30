# Healthcare Intelligence Platform - Project Structure

## 📁 Core Application Files

### Web Interface & APIs
- `web_interface_enhanced_social.py` - Main Flask application with all APIs
- `templates/dashboard_enhanced_social.html` - Frontend UI template

### Data Collection & Analysis
- `social_media_sentiment.py` - Social media sentiment analysis engine
- `real_data_scraper.py` - Multi-platform data scraper (Twitter, Reddit, etc.)
- `stock_ticker_intelligence.py` - Basic stock intelligence
- `enhanced_stock_intelligence.py` - Advanced stock analysis (optional)

### Intelligence Systems
- `management_truth_tracker.py` - Executive credibility tracking
- `integrated_intelligence_system.py` - Combined intelligence analysis
- `ai_generator_optimized.py` - AI-powered report generation

### Configuration & Setup
- `config.py` - Application configuration
- `api_config.py` - API keys and credentials
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys)
- `env.example` - Example environment file

## 📁 Databases & Data
- `drug_company_mapping.db` - Drug-to-company mappings
- `social_media_sentiment.db` - Cached social media data
- `stock_intelligence_cache.db` - Stock data cache
- `management_promises.db` - Executive promises tracking
- `fda_decisions.db` - FDA decision history

## 📁 Scripts & Utilities
- `run_platform.sh` - Start the platform
- `setup.py` - Installation setup
- `populate_sample_data.py` - Initialize databases
- `test_*.py` - Various test scripts
- `verify_requirements.py` - Dependency verification

## 📁 Documentation
- `README.md` - Main documentation
- `HOW_TO_RUN.md` - Running instructions
- `HEALTHCARE_INTELLIGENCE_GUIDE.md` - Feature guide
- `SETUP_REAL_APIS.md` - API setup instructions

## 📁 Reports & Output
- `reports/` - Generated intelligence reports
- `cache/` - Temporary cache files

## 🚀 Main Entry Points
1. **Web Platform**: `python3 web_interface_enhanced_social.py`
2. **CLI Analysis**: `python3 integrated_intelligence_system.py`
3. **Batch Processing**: `python3 daily_healthcare_intelligence.py`

## 🔧 Key Features
- **Social Sentiment Analysis**: Real Twitter API + Reddit scraping
- **Stock Intelligence**: Multi-source financial data with fallbacks
- **Executive Credibility**: Promise tracking from news + filings
- **Real Data Only**: No demo data - all live APIs

## 📋 Dependencies
- Flask (web framework)
- yfinance (stock data)
- tweepy (Twitter API)
- pandas, numpy (data analysis)
- anthropic, openai (AI analysis)
- beautifulsoup4 (web scraping)
- plotly (visualizations)

## 🌐 Platform Access
- URL: http://localhost:5001
- Tabs: Social Sentiment, Stock Intelligence, Executive Credibility
- All data sources: Real-time APIs with smart fallbacks 