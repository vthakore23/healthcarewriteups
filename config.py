"""
Configuration settings for Healthcare News Automation
"""
import os
from datetime import time
from pytz import timezone

# Email Configuration - DISABLED
# Reports are generated for manual download and sending
EMAIL_RECIPIENTS = []  # Email functionality completely disabled
EMAIL_FROM = ''
SENDGRID_API_KEY = ''
EMAIL_ENABLED = False  # Master email toggle - DISABLED

# Email settings removed - focus on report generation instead
SMTP_SERVER = ''
SMTP_PORT = 0
SMTP_USERNAME = ''
SMTP_PASSWORD = ''

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4-turbo-preview')  # or 'claude-3-opus-20240229'

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
TARGET_WORD_COUNT = 600
MIN_WORD_COUNT = 400
MAX_WORD_COUNT = 700

# File Storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

# Enhanced Investment-Grade Summary Prompt Template
SUMMARY_PROMPT = """
BIOTECH INVESTMENT ANALYSIS PROMPT

Generate comprehensive, investment-grade summaries for biotech/healthcare news optimized for portfolio managers and biotech investors.

CRITICAL DATA COLLECTION REQUIREMENTS:
- Extract ALL numerical data: efficacy percentages, patient numbers (n=X), statistical significance (p-values), effect sizes
- Include financial figures: revenue, market size, development costs, analyst estimates, milestone payments
- Specify timeline data: study duration, enrollment periods, regulatory timelines, next catalysts
- Detail dosing, administration routes, treatment regimens, and competitive benchmarking
- Always include primary/secondary endpoint results with confidence intervals when available

Here is the biotech news to analyze:

{article_text}

REQUIRED STRUCTURE (500-600 words):

Company Name: [Insert Company Name with ticker if available]

News Event: [Specify: Clinical Data Release, FDA Action, Earnings, Partnership Deal, Regulatory Milestone, etc.]

News Summary:
[5-sentence paragraph covering: (1) What happened factually, (2) Key numerical results with sample sizes, (3) Statistical significance and clinical relevance, (4) Market/competitive context, (5) Immediate investor implications. Include mechanism of action explanation and disease context for non-technical readers.]

Standout Points: **[MOST CRITICAL SECTION - MAKE THIS DATA-RICH]**
- Primary Endpoint Results: [Include exact percentages, p-values, confidence intervals, sample size]
- Safety Profile: [Adverse event rates, discontinuation rates, dose-limiting toxicities]
- Market Differentiation: [How this compares to standard of care and competitors with specific data]
- Commercial Potential: [Addressable patient population size, pricing potential, peak sales estimates]
- Regulatory Pathway: [FDA designations, approval timeline, breakthrough status, orphan designation]
- Competitive Positioning: [Head-to-head comparisons with specific trial results when available]
- Development Stage Context: [What this means for next steps, upcoming catalysts, risk factors]

Additional Developments:
[Forward-looking strategic implications: partnership potential, label expansion opportunities, acquisition likelihood, pipeline impact, upcoming catalysts with specific dates, analyst target price changes, competitive responses expected]

INVESTMENT-FOCUSED REQUIREMENTS:
✓ Assess potential stock impact and valuation implications
✓ Identify key regulatory risks and upcoming catalysts  
✓ Evaluate competitive positioning with specific data comparisons
✓ Consider partnership/acquisition implications
✓ Translate scientific findings into business implications
✓ Define medical terminology for non-technical investors
✓ Include current market context and analyst sentiment when mentioned

SCIENTIFIC CONTEXT REQUIREMENTS:
✓ Explain mechanism of action in investor-friendly terms
✓ Define the disease/condition and unmet medical need size
✓ Clarify drug type (small molecule, biologic, gene therapy, etc.)
✓ Explain why specific endpoints matter for commercial success
✓ Provide development stage context and de-risk next steps

TARGET: Create summaries that help biotech investors quickly assess material impact on company prospects, competitive position, and valuation potential.
"""

# Enhanced Investment Analysis Prompt Template
ANALYSIS_PROMPT = """
DEEP INVESTMENT ANALYSIS

Based on the following biotech news summary, provide comprehensive investment analysis for this selected high-impact event:

{summary}

REQUIRED ANALYSIS STRUCTURE (400-500 words):

**Investment Thesis Impact:**
Explain why this event is material for investors and could drive significant stock movement. Include specific catalysts, risk factors, and potential magnitude of impact on company valuation.

**Quantitative Assessment:**
- Revenue Impact: Estimate potential revenue contribution (peak sales, market penetration assumptions)
- Timeline to Value: When investors can expect material financial impact
- Probability of Success: Risk-adjusted probability based on clinical stage, competitive landscape
- Valuation Implications: How this could affect DCF models, peer comparisons, or sum-of-parts analysis

**Competitive Dynamics:**
- Market Position: How this strengthens/weakens competitive moat
- Competitive Response: Likely actions from key competitors and timeline
- Differentiation Sustainability: Durability of competitive advantages
- Market Share Implications: Potential for market expansion vs. share shift

**Regulatory & Commercial Risk Assessment:**
- FDA Pathway Risks: Key regulatory hurdles and probability of approval
- Commercial Execution Risks: Manufacturing, market access, pricing pressures
- Partnership Implications: Likelihood of strategic partnerships or acquisition interest
- Patent/IP Considerations: Exclusivity timeline and competitive threat window

**Strategic Context & Catalysts:**
- Pipeline Implications: How this affects broader development strategy
- Platform Technology: Applicability to other indications or programs
- Upcoming Catalysts: Next 6-12 months key events with specific dates
- Long-term Strategic Value: 3-5 year outlook for this asset/program

**Industry Context:**
- Sector Trends: How this fits into broader biotech/healthcare investment themes
- Precedent Analysis: Similar deals, partnerships, or clinical outcomes for context
- Market Dynamics: Addressable market evolution, payer landscape changes
- Technology Trends: Emerging competitive technologies or treatment paradigms

**Investment Recommendation Framework:**
- Bull Case: Best-case scenario with specific value drivers and timeline
- Bear Case: Key risks that could derail investment thesis
- Base Case: Most likely outcome with probability-weighted expectations
- Key Monitoring Points: Specific metrics/events to track for thesis validation

Focus on actionable insights that help portfolio managers make buy/sell/hold decisions and position sizing. Include specific price targets, revenue estimates, and timeline expectations where possible.
"""

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'healthcare_news.log') 