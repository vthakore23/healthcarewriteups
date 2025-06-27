"""
Web scraper for lifesciencereport.com newsroom
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
import json
import os
from urllib.parse import urljoin, urlparse
import time
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


class LifeScienceScraper:
    """Scraper for lifesciencereport.com"""
    
    def __init__(self):
        self.base_url = config.BASE_URL
        self.headers = {
            'User-Agent': config.USER_AGENT
        }
        self.cache_file = os.path.join(config.CACHE_DIR, 'scraped_articles.json')
        self._ensure_directories()
        self.scraped_articles = self._load_cache()
    
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
    
    def _get_selenium_driver(self):
        """Create and return a Selenium WebDriver instance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={config.USER_AGENT}")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def get_todays_articles(self):
        """Get all articles published today"""
        logger.info(f"Fetching articles from {self.base_url}")
        today = date.today()
        articles = []
        
        try:
            # First try with requests
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            articles = self._parse_newsroom_page(response.text)
            
            # If no articles found, try with Selenium
            if not articles:
                logger.info("No articles found with requests, trying Selenium...")
                articles = self._get_articles_with_selenium()
            
        except Exception as e:
            logger.error(f"Error fetching newsroom page: {e}")
            # Fallback to Selenium
            try:
                articles = self._get_articles_with_selenium()
            except Exception as e2:
                logger.error(f"Selenium also failed: {e2}")
                return []
        
        # Filter for today's articles that haven't been scraped
        todays_articles = []
        for article in articles:
            if article.published_date and article.published_date.date() == today:
                if article.article_id not in self.scraped_articles:
                    todays_articles.append(article)
                    self.scraped_articles.add(article.article_id)
        
        self._save_cache()
        logger.info(f"Found {len(todays_articles)} new articles from today")
        return todays_articles
    
    def _get_articles_with_selenium(self):
        """Use Selenium to get articles (for JavaScript-rendered content)"""
        driver = self._get_selenium_driver()
        articles = []
        
        try:
            driver.get(self.base_url)
            # Wait for articles to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "article"))
            )
            
            # Get page source and parse
            page_source = driver.page_source
            articles = self._parse_newsroom_page(page_source)
            
        finally:
            driver.quit()
        
        return articles
    
    def _parse_newsroom_page(self, html_content):
        """Parse the newsroom page to extract article links"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Try different selectors that might contain articles
        article_selectors = [
            'article',
            '.article',
            '.news-item',
            '.post',
            '.entry',
            'div[class*="article"]',
            'div[class*="news"]',
            'div[class*="post"]',
            'a[href*="/news/"]',
            'a[href*="/article/"]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                for elem in elements:
                    article = self._extract_article_info(elem)
                    if article:
                        articles.append(article)
                break
        
        # If no articles found with selectors, try finding all links
        if not articles:
            links = soup.find_all('a', href=True)
            for link in links:
                if any(keyword in link['href'].lower() for keyword in ['news', 'article', 'press-release']):
                    article = self._extract_article_from_link(link)
                    if article:
                        articles.append(article)
        
        return articles
    
    def _extract_article_info(self, element):
        """Extract article information from an element"""
        try:
            # Try to find link
            link = element.find('a', href=True) if element.name != 'a' else element
            if not link:
                return None
            
            url = urljoin(self.base_url, link['href'])
            
            # Try to find title
            title = link.get_text(strip=True)
            if not title:
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
            
            # Try to find date
            date_elem = element.find(['time', 'span', 'div'], class_=lambda x: x and 'date' in x.lower())
            published_date = self._parse_date(date_elem.get_text(strip=True) if date_elem else None)
            
            # Fetch full article content
            article_content = self._fetch_article_content(url)
            
            if article_content:
                return NewsArticle(
                    title=title or "Untitled",
                    url=url,
                    content=article_content,
                    published_date=published_date or datetime.now()
                )
        except Exception as e:
            logger.error(f"Error extracting article info: {e}")
        
        return None
    
    def _extract_article_from_link(self, link):
        """Extract article from a simple link element"""
        try:
            url = urljoin(self.base_url, link['href'])
            title = link.get_text(strip=True)
            
            article_content = self._fetch_article_content(url)
            if article_content:
                return NewsArticle(
                    title=title or "Untitled",
                    url=url,
                    content=article_content,
                    published_date=datetime.now()
                )
        except Exception as e:
            logger.error(f"Error extracting article from link: {e}")
        
        return None
    
    def _fetch_article_content(self, url):
        """Fetch the full content of an article"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
                'div[class*="content"]',
                'div[class*="article"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    return content_elem.get_text(separator='\n', strip=True)
            
            # Fallback: get body text
            body = soup.find('body')
            if body:
                return body.get_text(separator='\n', strip=True)
            
        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {e}")
        
        return None
    
    def _parse_date(self, date_string):
        """Parse date from string"""
        if not date_string:
            return None
        
        date_formats = [
            '%Y-%m-%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%B %d',
            '%b %d'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                # If year is missing, assume current year
                if parsed_date.year == 1900:
                    parsed_date = parsed_date.replace(year=datetime.now().year)
                return parsed_date
            except:
                continue
        
        # Check if it's "today" or similar
        if 'today' in date_string.lower():
            return datetime.now()
        
        return None 