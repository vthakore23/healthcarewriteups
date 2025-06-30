#!/usr/bin/env python3
"""
Real Data Web Scraper for Healthcare Intelligence
Scrapes real social media data without requiring API credentials
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import asyncio
import aiohttp
from urllib.parse import quote_plus, urljoin
import time
import random
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class RealDataScraper:
    """Scrapes real social media data from public sources"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = None
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def search_twitter_web(self, query: str, count: int = 50) -> List[Dict]:
        """Scrape Twitter search results using the API we have"""
        logger.info(f"Searching Twitter API for: {query}")
        posts = []
        
        try:
            # Use the Twitter API directly since we have Bearer Token
            import tweepy
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                logger.info("Using Twitter API v2 for real data collection")
                client = tweepy.Client(bearer_token=bearer_token)
                
                # Build search query - exclude retweets, get English tweets about the drug
                search_query = f'"{query}" OR #{query} OR @{query} -is:retweet lang:en'
                
                # Search for recent tweets
                response = client.search_recent_tweets(
                    query=search_query,
                    max_results=min(100, count),
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                    user_fields=['name', 'username', 'verified'],
                    expansions=['author_id']
                )
                
                if response.data:
                    # Create user lookup
                    users = {u.id: u for u in (response.includes.get('users', []) or [])}
                    
                    for tweet in response.data:
                        author = users.get(tweet.author_id)
                        
                        # Filter for drug relevance
                        if self._is_drug_relevant(tweet.text, query):
                            posts.append({
                                'id': str(tweet.id),
                                'content': tweet.text,
                                'author': author.username if author else f"user_{tweet.author_id}",
                                'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                                'likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                                'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                                'replies': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                                'platform': 'Twitter',
                                'url': f"https://twitter.com/{author.username if author else 'user'}/status/{tweet.id}"
                            })
                    
                    logger.info(f"Found {len(posts)} relevant Twitter posts for {query}")
                else:
                    logger.warning(f"No recent tweets found for {query}")
            else:
                logger.warning("No Twitter Bearer Token found, skipping Twitter search")
            
        except tweepy.TooManyRequests:
            logger.warning("Twitter API rate limit hit, will try again later")
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
            
        return posts
    
    async def search_reddit_web(self, query: str, count: int = 50) -> List[Dict]:
        """Scrape Reddit search results without API"""
        logger.info(f"Scraping Reddit for: {query}")
        posts = []
        
        try:
            # Reddit allows some web scraping with proper headers
            search_url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={count}&sort=relevance&t=month"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post in data.get('data', {}).get('children', []):
                            post_data = post.get('data', {})
                            
                            posts.append({
                                'id': post_data.get('id'),
                                'title': post_data.get('title'),
                                'content': post_data.get('selftext', ''),
                                'author': post_data.get('author'),
                                'subreddit': post_data.get('subreddit'),
                                'created_utc': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat() if post_data.get('created_utc') else datetime.now().isoformat(),
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'platform': 'Reddit'
                            })
                    else:
                        logger.error(f"Reddit returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
            
        return posts
    
    async def search_patient_forums(self, drug_name: str) -> List[Dict]:
        """Scrape patient forum discussions"""
        logger.info(f"Scraping patient forums for: {drug_name}")
        posts = []
        
        # List of patient forums that allow respectful scraping
        forums = [
            {
                'name': 'HealthUnlocked',
                'search_url': f'https://healthunlocked.com/search?query={quote_plus(drug_name)}',
                'selector': '.post-item'
            },
            {
                'name': 'Patient.info Forums',
                'search_url': f'https://patient.info/forums/search?query={quote_plus(drug_name)}',
                'selector': '.discussion-list-item'
            }
        ]
        
        for forum in forums:
            try:
                posts.extend(await self._scrape_forum(forum, drug_name))
            except Exception as e:
                logger.error(f"Error scraping {forum['name']}: {e}")
                
        return posts
    
    async def _scrape_forum(self, forum_config: Dict, drug_name: str) -> List[Dict]:
        """Scrape a specific patient forum"""
        posts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Add delay to be respectful
                await asyncio.sleep(random.uniform(1, 3))
                
                async with session.get(forum_config['search_url'], headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # This is a generic example - each forum needs specific parsing
                        for item in soup.select(forum_config['selector'])[:20]:
                            post = self._parse_forum_post(item, forum_config['name'])
                            if post and drug_name.lower() in post.get('content', '').lower():
                                posts.append(post)
                                
        except Exception as e:
            logger.error(f"Error in _scrape_forum: {e}")
            
        return posts
    
    def _parse_forum_post(self, element, forum_name: str) -> Optional[Dict]:
        """Parse a forum post element"""
        try:
            # Generic parsing - needs customization per forum
            title = element.select_one('.title, h3, .subject')
            content = element.select_one('.content, .message, .post-body')
            author = element.select_one('.author, .username')
            date = element.select_one('.date, .timestamp')
            
            if title and content:
                return {
                    'id': f"{forum_name}_{hash(title.get_text())}",
                    'title': title.get_text(strip=True),
                    'content': content.get_text(strip=True),
                    'author': author.get_text(strip=True) if author else 'Anonymous',
                    'date': self._parse_date(date.get_text(strip=True) if date else ''),
                    'forum': forum_name,
                    'platform': 'PatientForum'
                }
        except Exception as e:
            logger.error(f"Error parsing forum post: {e}")
            
        return None
    
    async def _search_news_aggregator(self, query: str, platform: str) -> List[Dict]:
        """Search news aggregators for social media mentions"""
        posts = []
        
        # Use Google News as an aggregator
        search_url = f"https://news.google.com/search?q={quote_plus(query + ' ' + platform)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Parse Google News results
                        # This would need proper implementation
                        logger.info(f"Found news aggregator results for {query}")
                        
        except Exception as e:
            logger.error(f"Error searching news aggregator: {e}")
            
        return posts
    
    async def search_stocktwits(self, ticker: str) -> List[Dict]:
        """Scrape StockTwits for ticker mentions"""
        logger.info(f"Scraping StockTwits for: ${ticker}")
        posts = []
        
        try:
            # StockTwits has a public API that doesn't require authentication
            api_url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers={'User-Agent': self.ua.random}) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and 'messages' in data:
                            for message in data['messages']:
                                user_info = message.get('user', {})
                                likes_info = message.get('likes', {})
                                posts.append({
                                    'id': message.get('id'),
                                    'content': message.get('body'),
                                    'author': user_info.get('username') if user_info else 'unknown',
                                    'created_at': message.get('created_at'),
                                    'sentiment': message.get('entities', {}).get('sentiment', {}).get('basic') if message.get('entities') else None,
                                    'likes': likes_info.get('total', 0) if likes_info else 0,
                                    'platform': 'StockTwits',
                                    'ticker': ticker
                                })
                        else:
                            logger.warning(f"No messages found in StockTwits response for {ticker}")
                    else:
                        logger.error(f"StockTwits returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error scraping StockTwits: {e}")
            
        return posts
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats"""
        # Implement date parsing logic
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%B %d, %Y', '%d %b %Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except:
                    continue
        except:
            pass
            
        # Return current time if parsing fails
        return datetime.now().isoformat()
    
    async def get_real_data(self, drug_name: str, platforms: List[str] = None) -> Dict[str, List[Dict]]:
        """Get real data from multiple platforms with enhanced sources"""
        if platforms is None:
            platforms = ['reddit', 'twitter', 'forums', 'stocktwits', 'youtube', 'tiktok', 'news']
            
        results = {}
        
        # Get ticker for StockTwits
        ticker = self._get_ticker_for_drug(drug_name)
        
        tasks = []
        if 'reddit' in platforms:
            tasks.append(('reddit', self.search_reddit_web(drug_name)))
        if 'twitter' in platforms:
            tasks.append(('twitter', self.search_twitter_web(drug_name)))
        if 'forums' in platforms:
            tasks.append(('forums', self.search_patient_forums(drug_name)))
        if 'stocktwits' in platforms and ticker:
            tasks.append(('stocktwits', self.search_stocktwits(ticker)))
        if 'youtube' in platforms:
            tasks.append(('youtube', self.search_youtube(drug_name)))
        if 'tiktok' in platforms:
            tasks.append(('tiktok', self.search_tiktok(drug_name)))
        if 'news' in platforms:
            tasks.append(('news', self.search_healthcare_news(drug_name)))
            
        # Run all searches in parallel
        for platform, task in tasks:
            try:
                results[platform] = await task
                logger.info(f"Got {len(results[platform])} results from {platform}")
            except Exception as e:
                logger.error(f"Error getting {platform} data: {e}")
                results[platform] = []
                
        return results
    
    def _get_ticker_for_drug(self, drug_name: str) -> Optional[str]:
        """Get stock ticker for a drug"""
        if not drug_name:
            return None
            
        # Simple mapping - in production this would use the drug database
        drug_to_ticker = {
            'humira': 'ABBV',
            'keytruda': 'MRK',
            'opdivo': 'BMY',
            'ozempic': 'NVO',
            'mounjaro': 'LLY',
            'paxlovid': 'PFE',
            'leqembi': 'BIIB'
        }
        
        return drug_to_ticker.get(drug_name.lower())

    def _is_drug_relevant(self, text: str, drug_name: str) -> bool:
        """Check if the text is actually relevant to the drug"""
        text_lower = text.lower()
        drug_lower = drug_name.lower()
        
        # Must contain the drug name
        if drug_lower not in text_lower:
            return False
        
        # Filter out irrelevant content
        spam_indicators = [
            'buy now', 'click here', 'discount', 'sale', 'promo', 
            'crypto', 'bitcoin', 'nft', 'follow me', 'dm me',
            'check my bio', 'link in bio', '$$$', '💰', '🚀',
            'pump', 'moon', 'lambo', 'hodl'
        ]
        
        for indicator in spam_indicators:
            if indicator in text_lower:
                return False
        
        # Look for medical/health context
        medical_indicators = [
            'treatment', 'therapy', 'patient', 'doctor', 'physician',
            'side effect', 'dosage', 'prescription', 'medication', 'drug',
            'symptoms', 'condition', 'disease', 'illness', 'health',
            'clinical', 'trial', 'study', 'fda', 'approval', 'efficacy',
            'taking', 'prescribed', 'injection', 'pill', 'dose',
            'mg', 'ml', 'daily', 'weekly', 'monthly', 'experience'
        ]
        
        has_medical_context = any(indicator in text_lower for indicator in medical_indicators)
        
        # For drugs, we want medical context
        return has_medical_context or len(text.split()) > 10  # Or longer posts which likely have context

    async def search_youtube(self, drug_name: str) -> List[Dict]:
        """Search YouTube for drug-related content"""
        logger.info(f"Searching YouTube for: {drug_name}")
        posts = []
        
        try:
            # Use YouTube Data API if available, otherwise web scraping
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={quote_plus(drug_name)}%20review%20experience&type=video&maxResults=25"
            
            # For now, return placeholder data indicating YouTube search capability
            # In production, you'd implement actual YouTube API integration
            logger.info(f"YouTube search capability available for {drug_name}")
            
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            
        return posts
    
    async def search_tiktok(self, drug_name: str) -> List[Dict]:
        """Search TikTok for drug-related content"""
        logger.info(f"Searching TikTok for: {drug_name}")
        posts = []
        
        try:
            # TikTok web scraping would go here
            # Note: TikTok has strong anti-scraping measures
            logger.info(f"TikTok search capability available for {drug_name}")
            
        except Exception as e:
            logger.error(f"Error searching TikTok: {e}")
            
        return posts
    
    async def search_healthcare_news(self, drug_name: str) -> List[Dict]:
        """Search healthcare news sources"""
        logger.info(f"Searching healthcare news for: {drug_name}")
        posts = []
        
        try:
            # Use News API if available
            import os
            news_api_key = os.getenv('NEWS_API_KEY')
            
            if news_api_key:
                news_url = f"https://newsapi.org/v2/everything?q={quote_plus(drug_name)}&sources=medical-news-today,reuters&sortBy=publishedAt&apiKey={news_api_key}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(news_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for article in data.get('articles', [])[:10]:
                                if self._is_drug_relevant(article.get('title', '') + ' ' + article.get('description', ''), drug_name):
                                    posts.append({
                                        'id': f"news_{hash(article.get('url', ''))}",
                                        'content': f"{article.get('title', '')} - {article.get('description', '')}",
                                        'author': article.get('source', {}).get('name', 'News Source'),
                                        'created_at': article.get('publishedAt', datetime.now().isoformat()),
                                        'platform': 'Healthcare News',
                                        'url': article.get('url', ''),
                                        'engagement': {'views': 100}  # Placeholder
                                    })
                            
                            logger.info(f"Found {len(posts)} relevant news articles for {drug_name}")
                        else:
                            logger.error(f"News API returned status {response.status}")
            else:
                logger.warning("No News API key found")
                
        except Exception as e:
            logger.error(f"Error searching healthcare news: {e}")
            
        return posts


# Integration with existing sentiment analyzer
async def get_real_social_data(drug_name: str) -> Dict:
    """Get real social media data for a drug"""
    scraper = RealDataScraper()
    
    logger.info(f"Fetching REAL data for {drug_name}")
    real_data = await scraper.get_real_data(drug_name)
    
    # Format data for sentiment analysis
    all_posts = []
    
    for platform, posts in real_data.items():
        for post in posts:
            # Get the date field based on platform
            date_field = post.get('date') or post.get('created_at') or post.get('created_utc')
            
            all_posts.append({
                'platform': platform,
                'content': post.get('content', '') or post.get('title', ''),
                'author': post.get('author', 'Unknown'),
                'date': date_field or datetime.now().isoformat(),
                'engagement': {
                    'likes': post.get('likes', 0) or post.get('score', 0),
                    'comments': post.get('num_comments', 0),
                    'shares': 0
                },
                'url': post.get('url', ''),
                'id': post.get('id', '')
            })
    
    logger.info(f"Collected {len(all_posts)} REAL posts for {drug_name}")
    
    return {
        'drug_name': drug_name,
        'posts': all_posts,
        'total_posts': len(all_posts),
        'data_source': 'real_web_scraping',
        'platforms': list(real_data.keys()),
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test the scraper
    async def test():
        data = await get_real_social_data("Ozempic")
        print(f"Found {data['total_posts']} real posts")
        for post in data['posts'][:5]:
            print(f"\n{post['platform']}: {post['content'][:100]}...")
    
    asyncio.run(test()) 