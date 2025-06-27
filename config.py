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

# Summary Prompt Template
SUMMARY_PROMPT = """
Prompt for Healthcare-Related News

Prompt Objective:
Generate detailed, structured summaries for healthcare-related company news that capture critical details, provide an investor-focused narrative. Include all subsections, even if brief, to maintain consistency.

QUALITY REQUIREMENTS:
- Create accurate titles that reflect actual content (not misleading headlines)
- Clearly distinguish between different studies/trials with separate descriptions
- Be precise with study names, patient numbers, and timelines
- Reduce redundancy - consolidate similar points
- Lead with clear, factual statements about what actually happened

Here is the press release to summarize:

{article_text}

Structure:
Company Name: [Insert Company Name]
News Event: [Insert Type: Earnings, Data Release, Conference, Partnership, Leadership Change, etc.]
News Summary:
[Provide a concise paragraph (5 sentences) summarizing the key news, including critical figures, events, and implications. Focus on what makes the news significant for investors or the market, avoiding vague statements. This is important to cover the main key points.]
Standout Points:
[Highlight quantifiable data (e.g., efficacy, safety, sales) or unique aspects that could influence investor sentiment or valuation. Prioritize material details. Please make this the "meatiest" of the sections, not missing anything important.]
Additional Developments:
[Insert info on partnerships, acquisitions, collaborations, or strategic initiatives tied to the news.]

Try to be very specific and explain anything that needs explaining like mechanism or drug or what it's going after and why it's different. Keep to approximately 600 words.

Note: Ensure that all summaries follow this exact structure to maintain consistency across all news events.
"""

# Analysis Prompt Template
ANALYSIS_PROMPT = """
Based on the following news summary, provide additional analysis for this selected interesting event:

{summary}

Please provide a detailed analysis covering:

1. **Why this event is interesting**: Explain why you found this particular event noteworthy and significant for investors.

2. **Potential implications**: Discuss the longer-term implications of this event for the company. Think about what this may mean or impact the company whether good, bad, or indifferent. Consider:
   - Financial impact potential
   - Competitive positioning changes
   - Regulatory pathway implications
   - Market opportunity expansion/contraction

3. **Additional insights**: Include any additional research or insights gathered while digging deeper into this topic, such as:
   - Industry context and trends
   - Competitive landscape considerations
   - Technical/scientific background
   - Previous similar cases or precedents

Aim for 300-400 words of thoughtful, investment-focused analysis.
"""

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'healthcare_news.log') 