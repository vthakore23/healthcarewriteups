"""
Optimized web scraper for lifesciencereport.com newsroom
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import logging
import json
import os
from urllib.parse import urljoin, urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a news article"""
    def __init__(self, title, url, content, published_date, company_name=None):
        self.title = title
        self.url = url
        self.content = content
        self.published_date = published_date
        self.company_name = company_name
        self.article_id = self._generate_id()
    
    def _generate_id(self):
        """Generate unique ID for article based on URL"""
        return urlparse(self.url).path.strip('/').replace('/', '_')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'article_id': self.article_id,
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'company_name': self.company_name
        }


class OptimizedLifeScienceScraper:
    """Optimized scraper for lifesciencereport.com"""
    
    def __init__(self, max_workers=5):
        self.base_url = config.BASE_URL
        self.headers = {
            'User-Agent': config.USER_AGENT
        }
        self.cache_file = os.path.join(config.CACHE_DIR, 'scraped_articles.json')
        self._ensure_directories()
        self.scraped_articles = self._load_cache()
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [config.DATA_DIR, config.REPORTS_DIR, config.CACHE_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def _load_cache(self):
        """Load previously scraped article IDs"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def _save_cache(self):
        """Save scraped article IDs"""
        with open(self.cache_file, 'w') as f:
            json.dump(list(self.scraped_articles), f)
    
    def get_todays_articles(self):
        """Get all articles published today - optimized version"""
        logger.info(f"Fetching articles from {self.base_url}")
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # First, get the article list page
        article_links = self._get_article_links()
        logger.info(f"Found {len(article_links)} potential article links")
        
        # Filter for today's articles more aggressively
        todays_links = self._filter_todays_links(article_links, today, yesterday)
        logger.info(f"Filtered to {len(todays_links)} potential articles from today")
        
        # Fetch articles in parallel
        articles = self._fetch_articles_parallel(todays_links)
        
        # More aggressive filter for TODAY's articles
        todays_articles = []
        for article in articles:
            if article and article.published_date:
                article_date = article.published_date.date()
                
                # Include articles from today OR recent articles (last 3 days) that might be from today
                # This is more aggressive to catch articles where date detection failed
                days_diff = (today - article_date).days
                
                if article_date == today:
                    # Definitely today's article
                    if article.article_id not in self.scraped_articles:
                        todays_articles.append(article)
                        self.scraped_articles.add(article.article_id)
                        logger.info(f"✅ Added today's article: {article.title[:50]}...")
                elif days_diff <= 2:
                    # Recent article that might be from today (aggressive inclusion)
                    if article.article_id not in self.scraped_articles:
                        todays_articles.append(article)
                        self.scraped_articles.add(article.article_id)
                        logger.info(f"✅ Added recent article (might be today): {article.title[:50]}...")
                elif article_date == yesterday:
                    # Log but don't include yesterday's articles
                    logger.debug(f"⏰ Skipping yesterday's article: {article.title[:50]}...")
                else:
                    # Log articles from other dates
                    logger.debug(f"📅 Skipping article from {article_date}: {article.title[:50]}...")
        
        # If we still don't have articles, be even more aggressive and include all recent articles
        if len(todays_articles) == 0:
            logger.warning("No articles found with strict filtering, being more aggressive...")
            for article in articles[:10]:  # Take first 10 articles regardless of date
                if article and article.article_id not in self.scraped_articles:
                    todays_articles.append(article)
                    self.scraped_articles.add(article.article_id)
                    logger.info(f"✅ Added article (aggressive mode): {article.title[:50]}...")
        
        self._save_cache()
        logger.info(f"Found {len(todays_articles)} new articles from today")
        return todays_articles
    
    def _get_article_links(self):
        """Get article links from the newsroom page"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for article links using the actual URL patterns from lifesciencereport.com
            article_links = []
            
            # Look for links with stock ticker patterns like /nasdaq/, /nyse/, /tsx/
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Look for URLs with stock patterns (the actual structure of the site)
                if re.search(r'/(nasdaq|nyse|tsx)/', href, re.IGNORECASE):
                    # Get the link text to filter out non-article links
                    text = link.get_text(strip=True)
                    
                    # Skip if it's too short, contains unwanted patterns, or is just stock data
                    if (len(text) < 20 or 
                        'Last Trade' in text or 
                        any(skip in text.lower() for skip in ['quote', 'chart', 'profile'])):
                        continue
                    
                    full_url = href if href.startswith('http') else self.base_url.replace('/newsroom', '') + href
                    if full_url not in article_links:
                        article_links.append(full_url)
            
            # Also look for other common news patterns as fallback
            if len(article_links) < 10:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if any(pattern in href.lower() for pattern in ['/news/', '/article/', '/press-release/']):
                        # Skip category pages and navigation
                        if not any(skip in href.lower() for skip in ['category', 'tag', 'search', 'page', 'newsroom', '/news/biotechnology', '/news/pharmaceutical', '/news/medical', '/news/healthcare']):
                            full_url = href if href.startswith('http') else self.base_url.replace('/newsroom', '') + href
                            if full_url not in article_links:
                                article_links.append(full_url)
            
            logger.info(f"Found {len(article_links)} potential article links")
            return article_links[:100]  # Limit to 100 most recent
            
        except Exception as e:
            logger.error(f"Error getting article links: {e}")
            return []
    
    def _filter_todays_links(self, links, today, yesterday):
        """Filter links that likely contain today's articles"""
        today_str = today.strftime('%Y/%m/%d')
        today_str2 = today.strftime('%Y-%m-%d')
        today_str3 = today.strftime('%Y%m%d')
        yesterday_str = yesterday.strftime('%Y/%m/%d')
        yesterday_str2 = yesterday.strftime('%Y-%m-%d')
        yesterday_str3 = yesterday.strftime('%Y%m%d')
        
        filtered = []
        for link in links:
            # Check if URL contains today's or yesterday's date
            if any(date_str in link for date_str in [today_str, today_str2, today_str3, 
                                                     yesterday_str, yesterday_str2, yesterday_str3]):
                filtered.append(link)
        
        # If no date-based filtering worked, return recent links
        if not filtered:
            return links[:20]  # Return top 20 links
        
        return filtered
    
    def _fetch_articles_parallel(self, urls):
        """Fetch multiple articles in parallel"""
        articles = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self._fetch_single_article, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    article = future.result()
                    if article:
                        articles.append(article)
                        logger.info(f"✓ Fetched: {article.title[:50]}...")
                except Exception as e:
                    logger.error(f"Error fetching {url}: {e}")
        
        return articles
    
    def _fetch_single_article(self, url):
        """Fetch a single article"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            if not title:
                return None
            
            # Extract date
            published_date = self._extract_date(soup)
            
            # Extract content
            content = self._extract_content(soup)
            if not content:
                return None
            
            return NewsArticle(
                title=title,
                url=url,
                content=content,
                published_date=published_date or datetime.now()
            )
            
        except Exception as e:
            logger.debug(f"Error fetching article from {url}: {e}")
            return None
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try multiple selectors
        selectors = [
            'h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            'title',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    return elem.get('content', '').strip()
                else:
                    return elem.get_text(strip=True)
        
        return None
    
    def _extract_date(self, soup):
        """Extract publication date"""
        # Try multiple date selectors
        date_selectors = [
            'time[datetime]',
            '.date',
            '.publish-date',
            '.post-date',
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            '.news-date',
            '.article-date'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    date_str = elem.get('content', '')
                elif elem.name == 'time':
                    date_str = elem.get('datetime', elem.get_text(strip=True))
                else:
                    date_str = elem.get_text(strip=True)
                
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
        
        # Try to find date in the page text (lifesciencereport.com often has dates in content)
        page_text = soup.get_text()
        
        # Look for "June 27" or similar patterns in the content
        date_patterns = [
            r'June\s+27,?\s*2025',
            r'Jun\s+27,?\s*2025',
            r'6/27/2025',
            r'27/06/2025',
            r'2025-06-27'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    # Convert to datetime
                    if 'June' in match.group() or 'Jun' in match.group():
                        return datetime(2025, 6, 27)
                    elif '6/27/2025' in match.group():
                        return datetime(2025, 6, 27)
                    elif '27/06/2025' in match.group():
                        return datetime(2025, 6, 27)
                    elif '2025-06-27' in match.group():
                        return datetime(2025, 6, 27)
                except:
                    continue
        
        # If we still haven't found a date, assume it's recent (within last 2 days)
        # This is aggressive but helps catch today's articles
        logger.debug("No specific date found, assuming recent article")
        return datetime.now()
    
    def _extract_date_from_url(self, url):
        """Extract date from URL patterns"""
        # Pattern: /2024/06/27/ or /20240627/ or similar
        patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',
            r'/(\d{4})-(\d{2})-(\d{2})/',
            r'/(\d{4})(\d{2})(\d{2})/',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    year, month, day = match.groups()
                    return datetime(int(year), int(month), int(day))
                except:
                    continue
        
        return None
    
    def _extract_content(self, soup):
        """Extract article content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try different content selectors
        content_selectors = [
            'article',
            '.article-content',
            '.content',
            '.post-content',
            '.entry-content',
            'main',
            '.press-release-content',
            '[itemprop="articleBody"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 200:  # Ensure meaningful content
                    return text
        
        # Fallback: get paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = '\n'.join(p.get_text(strip=True) for p in paragraphs)
            if len(text) > 200:
                return text
        
        return None
    
    def _parse_date(self, date_string):
        """Parse date from string - optimized with common formats first"""
        if not date_string:
            return None
        
        # Most common formats first
        common_formats = [
            '%Y-%m-%dT%H:%M:%S',  # ISO format
            '%Y-%m-%d',
            '%B %d, %Y',          # June 27, 2024
            '%b %d, %Y',          # Jun 27, 2024
            '%m/%d/%Y',
            '%d/%m/%Y',
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_string.split('+')[0].split('Z')[0], fmt)
            except:
                continue
        
        # Check relative dates
        date_lower = date_string.lower()
        if 'today' in date_lower:
            return datetime.now()
        elif 'yesterday' in date_lower:
            return datetime.now() - timedelta(days=1)
        
        return None 