"""
Optimized AI-powered summary generator with parallel processing and real-time company research
"""
import openai
import anthropic
import logging
import re
from typing import List, Dict, Tuple, Optional
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import wraps
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def retry_on_rate_limit(max_retries=3, delay=1):
    """Decorator to retry on rate limit errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (openai.RateLimitError, anthropic.RateLimitError) as e:
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
                except Exception as e:
                    if "rate" in str(e).lower() and attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator


class CompanyResearcher:
    """Research current company information and financial data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def research_company(self, company_name: str, ticker: Optional[str] = None) -> Dict[str, str]:
        """Research comprehensive company information"""
        logger.info(f"Researching company: {company_name}")
        
        research_data = {
            'company_overview': self._get_company_overview(company_name, ticker),
            'financial_metrics': self._get_financial_data(company_name, ticker),
            'recent_news': self._get_recent_news(company_name),
            'pipeline_status': self._get_pipeline_info(company_name),
            'analyst_coverage': self._get_analyst_info(company_name, ticker)
        }
        
        return research_data
    
    def _get_company_overview(self, company_name: str, ticker: Optional[str]) -> str:
        """Get basic company information"""
        try:
            # Search for company information
            query = f"{company_name} biotech pharmaceutical company overview"
            if ticker:
                query += f" {ticker}"
            
            search_results = self._web_search(query, max_results=3)
            return f"Company Overview: {search_results[:500]}..." if search_results else "No overview data available"
        except Exception as e:
            logger.error(f"Error getting company overview: {e}")
            return "Company overview data unavailable"
    
    def _get_financial_data(self, company_name: str, ticker: Optional[str]) -> str:
        """Get current financial metrics"""
        try:
            query = f"{company_name} stock price market cap financial metrics"
            if ticker:
                query += f" {ticker} stock"
            
            search_results = self._web_search(query, max_results=2)
            return f"Financial Data: {search_results[:400]}..." if search_results else "No financial data available"
        except Exception as e:
            logger.error(f"Error getting financial data: {e}")
            return "Financial data unavailable"
    
    def _get_recent_news(self, company_name: str) -> str:
        """Get recent news and developments"""
        try:
            query = f"{company_name} news developments 2024 clinical trials FDA"
            search_results = self._web_search(query, max_results=3)
            return f"Recent News: {search_results[:500]}..." if search_results else "No recent news available"
        except Exception as e:
            logger.error(f"Error getting recent news: {e}")
            return "Recent news unavailable"
    
    def _get_pipeline_info(self, company_name: str) -> str:
        """Get pipeline and development information"""
        try:
            query = f"{company_name} pipeline drugs development clinical trials phases"
            search_results = self._web_search(query, max_results=2)
            return f"Pipeline Info: {search_results[:400]}..." if search_results else "No pipeline data available"
        except Exception as e:
            logger.error(f"Error getting pipeline info: {e}")
            return "Pipeline data unavailable"
    
    def _get_analyst_info(self, company_name: str, ticker: Optional[str]) -> str:
        """Get analyst coverage and ratings"""
        try:
            query = f"{company_name} analyst ratings price target coverage"
            if ticker:
                query += f" {ticker}"
            
            search_results = self._web_search(query, max_results=2)
            return f"Analyst Coverage: {search_results[:300]}..." if search_results else "No analyst data available"
        except Exception as e:
            logger.error(f"Error getting analyst info: {e}")
            return "Analyst data unavailable"
    
    def _web_search(self, query: str, max_results: int = 3) -> str:
        """Perform web search and extract relevant information"""
        try:
            # Enhanced web search with multiple approaches
            search_results = []
            
            # Try DuckDuckGo for better results without blocking
            duckduck_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            try:
                response = self.session.get(duckduck_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract search result snippets from DuckDuckGo
                    for result in soup.find_all('a', class_='result__snippet')[:max_results]:
                        text = result.get_text(strip=True)
                        if text and len(text) > 50:
                            search_results.append(text)
                    
                    # Also try result links text
                    if not search_results:
                        for result in soup.find_all('div', class_='result__snippet')[:max_results]:
                            text = result.get_text(strip=True)
                            if text and len(text) > 50:
                                search_results.append(text)
            except:
                pass
            
            # Fallback to basic Google search if DuckDuckGo doesn't work
            if not search_results:
                google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                try:
                    response = self.session.get(google_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Try different selectors for Google results
                        selectors = [
                            '.BNeawe',
                            '.VwiC3b',
                            '.aCOpRe',
                            '.s3v9rd',
                            '.st'
                        ]
                        
                        for selector in selectors:
                            if search_results:
                                break
                            for result in soup.select(selector)[:max_results]:
                                text = result.get_text(strip=True)
                                if text and len(text) > 50:
                                    search_results.append(text)
                except:
                    pass
            
            return ' | '.join(search_results) if search_results else "No search results found"
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return "Search data unavailable"


class OptimizedAISummaryGenerator:
    """Optimized generator with parallel processing, caching, and real-time company research"""
    
    def __init__(self, max_workers=3):
        self.ai_provider = self._determine_ai_provider()
        self.max_workers = max_workers
        self.cache_dir = os.path.join(config.CACHE_DIR, 'ai_summaries')
        self.company_researcher = CompanyResearcher()
        os.makedirs(self.cache_dir, exist_ok=True)
        
        if self.ai_provider == 'openai':
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        elif self.ai_provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            raise ValueError("No valid AI API key found")
    
    def _determine_ai_provider(self):
        """Determine which AI provider to use"""
        # Debug: Print what we actually have
        logger.info(f"Checking API keys - Anthropic: {'Yes' if config.ANTHROPIC_API_KEY else 'No'}, OpenAI: {'Yes' if config.OPENAI_API_KEY else 'No'}")
        logger.info(f"AI Model configured: {config.AI_MODEL}")
        
        if config.ANTHROPIC_API_KEY and 'claude' in config.AI_MODEL.lower():
            logger.info("Using Anthropic Claude")
            return 'anthropic'
        elif config.OPENAI_API_KEY and ('gpt' in config.AI_MODEL.lower() or not config.ANTHROPIC_API_KEY):
            logger.info("Using OpenAI GPT")
            return 'openai'
        elif config.ANTHROPIC_API_KEY:
            logger.info("Using Anthropic Claude (fallback)")
            return 'anthropic'
        
        logger.error(f"No valid API key found. Anthropic: {bool(config.ANTHROPIC_API_KEY)}, OpenAI: {bool(config.OPENAI_API_KEY)}")
        return None
    
    def generate_summaries_batch(self, articles: List) -> List[Dict]:
        """Generate summaries for multiple articles in parallel"""
        logger.info(f"Generating summaries for {len(articles)} articles in parallel...")
        summaries = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_article = {
                executor.submit(self._generate_summary_with_progress, article, idx, len(articles)): (article, idx)
                for idx, article in enumerate(articles)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_article):
                article, idx = future_to_article[future]
                try:
                    summary_text = future.result()
                    if summary_text:
                        summaries.append({
                            'title': article.title,
                            'url': article.url,
                            'summary': summary_text,
                            'company_name': article.company_name,
                            'article': article
                        })
                except Exception as e:
                    logger.error(f"Error generating summary for article {idx+1}: {e}")
        
        return summaries
    
    def _generate_summary_with_progress(self, article, idx, total):
        """Generate summary with progress logging"""
        logger.info(f"Processing article {idx+1}/{total}: {article.title[:50]}...")
        
        # Check cache first
        cached_summary = self._get_cached_summary(article.article_id)
        if cached_summary:
            logger.info(f"✓ Used cached summary for article {idx+1}/{total}")
            return cached_summary
        
        # Generate new summary
        summary = self.generate_summary(article)
        
        # Cache the result
        if summary:
            self._cache_summary(article.article_id, summary)
            logger.info(f"✓ Generated summary for article {idx+1}/{total}")
        else:
            logger.error(f"✗ Failed to generate summary for article {idx+1}/{total}")
        
        return summary
    
    def _get_cached_summary(self, article_id):
        """Retrieve cached summary if available"""
        cache_file = os.path.join(self.cache_dir, f"{article_id}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is recent (within 7 days)
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if (datetime.now() - cache_time).days < 7:
                        return data['summary']
            except Exception:
                pass
        return None
    
    def _cache_summary(self, article_id, summary):
        """Cache a summary"""
        cache_file = os.path.join(self.cache_dir, f"{article_id}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.debug(f"Failed to cache summary: {e}")
    
    @retry_on_rate_limit(max_retries=3, delay=2)
    def generate_summary(self, article):
        """Generate a structured summary for an article with retry logic"""
        # Truncate content to avoid token limits
        max_content_length = 6000
        content = article.content[:max_content_length]
        if len(article.content) > max_content_length:
            content += "\n\n[Content truncated for processing]"
        
        prompt = config.SUMMARY_PROMPT.format(article_text=content)
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert healthcare and biotech analyst creating structured summaries for investors."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                summary_text = response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3,
                    system="You are an expert healthcare and biotech analyst creating structured summaries for investors."
                )
                summary_text = response.content[0].text
            
            # Validate summary
            if self._validate_summary(summary_text):
                # Extract company name
                company_name = self._extract_company_name(summary_text)
                if company_name:
                    article.company_name = company_name
                return summary_text
            else:
                logger.warning("Summary validation failed, regenerating...")
                return self._regenerate_with_structure(article, summary_text)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def _validate_summary(self, summary_text):
        """Validate that summary matches the exact requirements for investment analysis"""
        required_sections = [
            "Company Name:",
            "News Event:", 
            "News Summary:",
            "Standout Points:",
            "Additional Developments:"
        ]
        
        # Check all required sections are present
        for section in required_sections:
            if section not in summary_text:
                logger.warning(f"Missing required section: {section}")
                return False
        
        # Check word count - target approximately 600 words
        word_count = len(summary_text.split())
        if word_count < config.MIN_WORD_COUNT or word_count > config.MAX_WORD_COUNT:
            logger.warning(f"Word count {word_count} outside target range {config.MIN_WORD_COUNT}-{config.MAX_WORD_COUNT}")
            return False
        
        # Check that "Standout Points" section is substantial (should be the "meatiest" section)
        standout_start = summary_text.find("Standout Points:")
        additional_start = summary_text.find("Additional Developments:")
        
        if standout_start != -1 and additional_start != -1:
            standout_section = summary_text[standout_start:additional_start]
            standout_word_count = len(standout_section.split())
            
            # Standout Points should be at least 30% of total word count (Chris's "meatiest" requirement)
            if standout_word_count < word_count * 0.3:
                logger.warning(f"Standout Points section too short ({standout_word_count} words, needs to be meatiest section)")
                return False
        
        return True
    
    @retry_on_rate_limit(max_retries=2, delay=1)
    def _regenerate_with_structure(self, article, initial_summary):
        """Regenerate summary with exact structure and requirements"""
        followup_prompt = f"""
        The following summary doesn't meet the exact requirements. Please reformat it to match the EXACT structure and requirements:
        
        REQUIRED STRUCTURE (approximately 600 words total):
        
        Company Name: [Insert Company Name with ticker if available]
        
        News Event: [Insert Type: Earnings, Data Release, Conference, Partnership, Leadership Change, etc.]
        
        News Summary:
        [Provide a concise paragraph (5 sentences) summarizing the key news, including critical figures, events, and implications. Focus on what makes the news significant for investors.]
        
        Standout Points:
        [THIS MUST BE THE "MEATIEST" SECTION with ALL quantifiable data including:
        - Exact percentages, patient numbers (n=X), statistical significance (p-values)
        - Financial figures: revenue, market size, costs, analyst estimates, milestones  
        - Dosing, administration routes, treatment regimens
        - Competitive benchmarking with specific data
        - Timeline data: study duration, enrollment periods, regulatory timelines
        - Primary/secondary endpoint results with confidence intervals
        - Safety profile details: adverse event rates, discontinuation rates
        - Mechanism of action explanations
        - Market differentiation factors]
        
        Additional Developments:
        [Insert info on partnerships, acquisitions, collaborations, or strategic initiatives tied to the news.]
        
        CRITICAL REQUIREMENTS:
        - Be very specific about mechanisms, drugs, targets, and why things are different
        - Make "Standout Points" the most detailed section with ALL quantifiable data
        - Target exactly 600 words total
        - Explain medical terminology for investment context
        
        Current summary to reformat:
        {initial_summary}
        
        Original article for reference:
        {article.content[:4000]}
        
        Ensure "Standout Points" is the longest, most detailed section with all the quantifiable data.
        """
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are creating structured healthcare news summaries for investment professionals. Follow the exact format and make 'Standout Points' the meatiest section."},
                        {"role": "user", "content": followup_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.2
                )
                return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": followup_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.2,
                    system="You are creating structured healthcare news summaries for investment professionals. Follow the exact format and make 'Standout Points' the meatiest section."
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error regenerating summary: {e}")
            return initial_summary
    
    def _extract_company_name(self, summary_text):
        """Extract company name from summary"""
        match = re.search(r'Company Name:\s*([^\n]+)', summary_text)
        if match:
            return match.group(1).strip()
        return None
    
    @retry_on_rate_limit(max_retries=2, delay=1)
    def generate_analysis(self, summary_text, article_title="", company_name=""):
        """Generate analysis focused on why this news is interesting and its implications"""
        
        # Extract company name from summary if not provided
        if not company_name:
            company_name = self._extract_company_name(summary_text)
        
        # Get targeted company context for this specific news with source citations
        company_context = ""
        research_sources = []
        
        if company_name and company_name.lower() not in ['unknown', 'not found', '']:
            logger.info(f"Gathering company context for news analysis: {company_name}")
            try:
                # Get company research with source tracking
                context_data = self._get_targeted_company_context_with_sources(company_name, summary_text, article_title)
                company_context = context_data.get('context', '')
                research_sources = context_data.get('sources', [])
            except Exception as e:
                logger.error(f"Error gathering company context for {company_name}: {e}")
                company_context = "Limited external research available for this analysis"
        
        # Create analysis prompt matching Chris's requirements
        enhanced_prompt = config.ANALYSIS_PROMPT.format(
            summary=summary_text,
            article_title=article_title,
            company_name=company_name
        )
        
        # Add external research context if available
        if company_context and research_sources:
            enhanced_prompt += f"\n\nEXTERNAL RESEARCH CONTEXT (cite these sources in your analysis):\n"
            enhanced_prompt += company_context
            enhanced_prompt += f"\n\nSOURCES FOR EXTERNAL RESEARCH:\n"
            for source in research_sources:
                enhanced_prompt += f"- {source}\n"
        
        enhanced_prompt += f"""

CRITICAL REQUIREMENTS FOR ANALYSIS:
- Focus on WHY this event is interesting and worth attention
- Discuss longer-term implications for the company (good, bad, or indifferent)
- Include additional research and insights beyond the press release
- CITE SOURCES for any external research or data not from the original article
- Use phrases like "According to industry data..." or "Market research shows..."
- Include direct quotes and figures when relevant
- Provide specific, quantifiable insights where possible
- Target 400-600 words of additional analysis

STRUCTURE YOUR RESPONSE AS:
1. Why This Event is Interesting
2. Potential Implications (longer term)
3. Additional Research & Insights (with proper source citations)
"""
        
        try:
            system_message = f"""You are providing additional analysis for investment professionals. They want to understand:

1. WHY this healthcare/biotech news event is interesting and noteworthy
2. What the IMPLICATIONS are for the company (thinking longer term)
3. ADDITIONAL RESEARCH and insights beyond the press release

CRITICAL: When you reference any data or information not from the original press release, you MUST cite the source clearly. Use phrases like:
- "According to [source]..."
- "Industry data from [source] shows..."
- "Market research indicates..."

Be specific about what makes this news stand out and why investors should pay attention."""

            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3
                )
                return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3,
                    system=system_message
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return None
    
    def _get_targeted_company_context_with_sources(self, company_name: str, summary_text: str, article_title: str) -> Dict[str, any]:
        """Get targeted company context with proper source tracking for investment analysis"""
        
        # Extract key topics from the news to focus company research
        news_keywords = self._extract_news_keywords(summary_text, article_title)
        
        # Build targeted search queries based on the news content
        context_parts = []
        sources = []
        
        try:
            # 1. Company's current position related to this news topic
            if news_keywords:
                position_query = f"{company_name} {' '.join(news_keywords[:3])} current status 2024"
                position_info = self.company_researcher._web_search(position_query, max_results=2)
                if position_info and len(position_info) > 50:
                    context_parts.append(f"Current Market Position: {position_info[:300]}")
                    sources.append(f"Web search for {company_name} current status in {news_keywords[0]}")
            
            # 2. Market size and competitive context
            if len(news_keywords) > 0:
                market_query = f"{news_keywords[0]} market size competitive landscape 2024"
                market_info = self.company_researcher._web_search(market_query, max_results=2)
                if market_info and len(market_info) > 50:
                    context_parts.append(f"Market Context: {market_info[:300]}")
                    sources.append(f"Market research on {news_keywords[0]} sector")
            
            # 3. Recent company developments
            recent_query = f"{company_name} recent news developments 2024"
            recent_info = self.company_researcher._web_search(recent_query, max_results=2)
            if recent_info and len(recent_info) > 50:
                context_parts.append(f"Recent Company Developments: {recent_info[:250]}")
                sources.append(f"Recent news search for {company_name}")
                
        except Exception as e:
            logger.error(f"Error gathering research context: {e}")
            context_parts.append(f"External research context limited due to data gathering constraints")
            sources.append("Limited external data available")
        
        return {
            'context': " | ".join(context_parts) if context_parts else f"Analyzing {company_name} in context of {news_keywords[0] if news_keywords else 'this news event'}",
            'sources': sources
        }
    
    def _extract_news_keywords(self, summary_text: str, article_title: str) -> List[str]:
        """Extract key topics from the news for focused company research"""
        
        # Combine title and summary for keyword extraction
        text = f"{article_title} {summary_text}".lower()
        
        # Healthcare/biotech specific keywords to look for
        important_keywords = [
            'clinical trial', 'phase 1', 'phase 2', 'phase 3', 'fda approval', 'patent', 
            'partnership', 'merger', 'acquisition', 'earnings', 'revenue', 'pipeline',
            'drug', 'therapy', 'treatment', 'biomarker', 'efficacy', 'safety',
            'regulatory', 'breakthrough', 'data', 'results', 'milestone',
            'collaboration', 'licensing', 'intellectual property', 'indication'
        ]
        
        found_keywords = []
        for keyword in important_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        # Also extract company-specific terms mentioned
        words = text.split()
        for i, word in enumerate(words):
            if word in ['ingrezza', 'kinect', 'nell-1', 'superficial']:  # Add more drug/product names as needed
                found_keywords.append(word)
        
        return found_keywords[:5]  # Return top 5 most relevant keywords
    
    def select_interesting_articles_smart(self, summaries: List[Dict]) -> List[int]:
        """Smart selection using content analysis instead of AI call"""
        if len(summaries) <= 2:
            return list(range(len(summaries)))
        
        # Score articles based on keywords and patterns
        scores = []
        for idx, summary in enumerate(summaries):
            score = self._score_article_importance(summary)
            scores.append((idx, score))
        
        # Sort by score and return top 2
        scores.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, _ in scores[:2]]
    
    def _score_article_importance(self, summary: Dict) -> float:
        """Score article importance based on content"""
        text = summary['summary'].lower()
        score = 0.0
        
        # High-value keywords
        high_value_keywords = [
            'fda approval', 'breakthrough', 'phase 3', 'positive results',
            'acquisition', 'merger', 'billion', 'million', 'partnership',
            'first-in-class', 'novel', 'significant', 'exceeded',
            'transformative', 'game-changing', 'approval', 'clearance'
        ]
        
        # Medium-value keywords
        medium_value_keywords = [
            'phase 2', 'trial', 'study', 'data', 'results', 'efficacy',
            'safety', 'endpoint', 'collaboration', 'agreement',
            'expansion', 'launch', 'milestone'
        ]
        
        # Count high-value keywords (3 points each)
        for keyword in high_value_keywords:
            score += text.count(keyword) * 3
        
        # Count medium-value keywords (1 point each)
        for keyword in medium_value_keywords:
            score += text.count(keyword)
        
        # Bonus for quantitative data
        import re
        numbers = re.findall(r'\d+\.?\d*%', text)
        score += len(numbers) * 2
        
        # Bonus for financial figures
        financial_matches = re.findall(r'\$\d+\.?\d*\s*(million|billion)', text)
        score += len(financial_matches) * 5
        
        return score 