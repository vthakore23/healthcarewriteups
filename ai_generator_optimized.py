"""
Optimized AI-powered summary generator with parallel processing
"""
import openai
import anthropic
import logging
import re
from typing import List, Dict, Tuple
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import wraps
import json
import os
from datetime import datetime

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


class OptimizedAISummaryGenerator:
    """Optimized generator with parallel processing and caching"""
    
    def __init__(self, max_workers=3):
        self.ai_provider = self._determine_ai_provider()
        self.max_workers = max_workers
        self.cache_dir = os.path.join(config.CACHE_DIR, 'ai_summaries')
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
        if config.ANTHROPIC_API_KEY and 'claude' in config.AI_MODEL.lower():
            return 'anthropic'
        elif config.OPENAI_API_KEY:
            return 'openai'
        elif config.ANTHROPIC_API_KEY:
            return 'anthropic'
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
        """Validate that summary has required structure"""
        required_sections = [
            "Company Name:",
            "News Event:",
            "News Summary:",
            "Standout Points:",
            "Additional Developments:"
        ]
        
        for section in required_sections:
            if section not in summary_text:
                return False
        
        # Check word count
        word_count = len(summary_text.split())
        if word_count < config.MIN_WORD_COUNT:
            return False
        
        return True
    
    @retry_on_rate_limit(max_retries=2, delay=1)
    def _regenerate_with_structure(self, article, initial_summary):
        """Regenerate summary with explicit structure"""
        followup_prompt = f"""
        Please reformat the following summary to include ALL required sections:
        
        Company Name: [Insert Company Name]
        News Event: [Insert Type: Earnings, Data Release, Conference, Partnership, Leadership Change, etc.]
        News Summary:
        [5 sentences summarizing the key news]
        Standout Points:
        [Bullet points of quantifiable data]
        Additional Developments:
        [Partnerships, acquisitions, strategic initiatives]
        
        Current summary to reformat:
        {initial_summary}
        
        Original article:
        {article.content[:4000]}
        
        Make sure to include all sections and aim for 600 words total.
        """
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert healthcare analyst. Format the summary exactly as requested."},
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
                    system="You are an expert healthcare analyst. Format the summary exactly as requested."
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
    def generate_analysis(self, summary_text):
        """Generate additional analysis for interesting articles"""
        prompt = config.ANALYSIS_PROMPT.format(summary=summary_text)
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a senior healthcare investment analyst providing strategic insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.4
                )
                return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.4,
                    system="You are a senior healthcare investment analyst providing strategic insights."
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return None
    
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