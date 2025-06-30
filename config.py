"""
Configuration settings for Healthcare News Automation
"""
import os
from datetime import time
from pytz import timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration - DISABLED
EMAIL_RECIPIENTS = []  # Email functionality disabled
EMAIL_FROM = ''
SENDGRID_API_KEY = ''
EMAIL_ENABLED = False  # Reports saved locally only

# SMTP settings as fallback if SendGrid not available
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')  # or 'claude-3-opus-20240229'

# Web Scraping Configuration
BASE_URL = 'https://lifesciencereport.com/newsroom'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'

# Schedule Configuration (Eastern Time)
TIMEZONE = timezone('US/Eastern')
CHECK_TIMES = [
    time(7, 1),   # 7:01 AM
    time(8, 0),   # 8:00 AM
    time(9, 0),   # 9:00 AM
]

# Summary Configuration
TARGET_WORD_COUNT = 600  # Target approximately 600 words per summary
MIN_WORD_COUNT = 550     # Minimum acceptable word count
MAX_WORD_COUNT = 650     # Maximum word count

# File Storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

# Healthcare News Summary Prompt Structure - EXACT EMAIL FORMAT
SUMMARY_PROMPT = """
You are analyzing healthcare/biotech news for investment professionals. Create a structured 600-word analysis following the EXACT format specified.

CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:
- Use the precise structure below with exact section headers
- Target 600 words total (550-650 acceptable range)
- Make "Standout Points" the MEATIEST section (40-50% of total words)
- Include ALL quantifiable data in Standout Points
- Write exactly 5 sentences in News Summary
- Be specific about mechanisms, drugs, targets, and differentiation

Here is the biotech/healthcare news to analyze:

{article_text}

REQUIRED STRUCTURE (EXACT FORMAT):

Company Name: [Company name with ticker if available - keep this line brief]

News Event: [Single clear category: Data Release, Partnership, FDA Action, M&A, Financial, Pipeline Update, etc.]

News Summary:
[Write EXACTLY 5 sentences covering: (1) key development announcement, (2) specific figures/data from the news, (3) business implications, (4) timeline or next steps, (5) overall significance. Each sentence must be substantial and informative with specific details.]

Standout Points:
[THIS IS THE MEATIEST SECTION - Include ALL quantifiable data and detailed analysis:
• FINANCIAL METRICS: Exact dollar amounts, percentages, market size estimates, milestone payments, revenue figures
• CLINICAL DATA: Patient numbers (n=X), response rates, p-values, confidence intervals, survival data, safety profiles
• OPERATIONAL DETAILS: Trial sizes, enrollment timelines, dosing regimens, administration routes, study duration
• SCIENTIFIC SPECIFICS: Mechanism of action, molecular targets, competitive advantages, differentiation factors  
• REGULATORY INFO: FDA pathway details, submission timelines, breakthrough designations, approval probability factors
• MARKET CONTEXT: Competitive landscape positioning, addressable market size, treatment standard comparisons
Use bullet points and organize by category. This section should contain the most detailed, investment-relevant information.]

Additional Developments:
[Related partnerships, collaborations, strategic initiatives, regulatory updates, or broader market context beyond the main news event. Include forward-looking strategic implications.]

CRITICAL REQUIREMENTS:
- EXACTLY 600 words total (550-650 range acceptable)
- "Standout Points" must be the longest, most detailed section
- Include EVERY number, percentage, dollar amount, and timeline from the article
- Explain scientific terms in investment context
- Use bullet points in Standout Points for clarity
- Each section must provide unique, non-repetitive information
- Focus on investment decision-making relevance
"""

# Analysis Prompt for Additional Investment Analysis Section
ANALYSIS_PROMPT = """
You are providing additional analysis on why this healthcare/biotech news event is interesting and its implications for investors.

ARTICLE TITLE: {article_title}
COMPANY: {company_name}
NEWS SUMMARY: {summary}

Provide additional analysis focusing on:

1. WHY YOU FIND THIS EVENT INTERESTING
- What makes this news stand out from typical industry developments?
- Why should investors pay attention to this specific event?
- What unique aspects make this particularly noteworthy?

2. POTENTIAL IMPLICATIONS (Think longer term)
- What this may mean or impact the company (good, bad, or indifferent)
- How this positions the company competitively
- Regulatory pathway implications
- Market opportunity sizing and addressability
- Partnership/acquisition potential
- Platform technology implications

3. ADDITIONAL RESEARCH & INSIGHTS
- Context from comparable companies or precedent transactions
- Competitive landscape analysis
- Market dynamics that make this relevant
- Technical or scientific background that adds context

CRITICAL REQUIREMENTS:
- Cite sources for any external research beyond the original article
- Include direct quotes and figures when relevant
- Provide specific, quantifiable insights where possible
- Focus on investment relevance and materiality
- Explain complex mechanisms/science in investor-friendly terms
- Consider both near-term catalysts and long-term strategic value

RESEARCH SOURCING:
- When referencing data not in the original article, clearly indicate the source
- Use phrases like "According to [source]..." or "Industry data shows..."
- Distinguish between facts from the press release vs. external research

Target length: 400-600 words of additional analysis beyond the original summary.
"""

# Company Research Prompt Template
COMPANY_RESEARCH_PROMPT = """
REAL-TIME COMPANY INTELLIGENCE RESEARCH

Company: {company_name}
Ticker: {ticker}

Provide comprehensive, up-to-date intelligence on this healthcare/biotech company:

**CURRENT FINANCIAL STATUS**
- Stock price and recent performance (1M, 3M, 6M, 1Y)
- Market cap, enterprise value, and key ratios
- Cash position and runway analysis
- Recent earnings highlights and guidance
- Analyst consensus ratings and price targets

**PIPELINE & DEVELOPMENT STATUS**  
- Key programs by development phase
- Recent clinical trial updates and data readouts
- Regulatory milestones and FDA interactions
- Partnership and collaboration updates
- Patent/IP status and competitive positioning

**RECENT NEWS & CATALYSTS**
- Major announcements in past 30 days
- Upcoming investor events and conferences
- Management presentations and guidance updates
- Competitor actions affecting market position
- Industry trends impacting the company

**INVESTMENT SENTIMENT**
- Institutional ownership changes
- Recent insider trading activity
- Wall Street analyst commentary
- Social media and retail investor sentiment
- Short interest and options activity

Prioritize information from the last 30 days and focus on factors that could impact investment decisions.
"""

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'healthcare_news.log')

# Financial API Keys (for stock ticker intelligence)
# Get free API keys from:
# - Financial Modeling Prep: https://financialmodelingprep.com/developer/docs/
# - Alpha Vantage: https://www.alphavantage.co/support/#api-key
# - News API: https://newsapi.org/register
FMP_API_KEY = os.getenv('FMP_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '') 