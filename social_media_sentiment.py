#!/usr/bin/env python3
"""
Social Media Sentiment Analyzer for Pharmaceutical Drugs
Analyzes sentiment from Reddit, Twitter/X, Facebook, and patient forums
Provides real-time insights on drug perception and patient experiences
"""
import sys
import os
from datetime import datetime, timedelta
import json
import sqlite3
import re
from typing import Dict, List, Tuple, Optional
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import praw  # Reddit API
import tweepy  # Twitter API
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random
# import spacy  # Not needed for basic functionality
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import time
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import real data scraper
try:
    from real_data_scraper import RealDataScraper, get_real_social_data
    REAL_SCRAPER_AVAILABLE = True
except ImportError:
    logger.warning("Real data scraper not available, will use demo data")
    REAL_SCRAPER_AVAILABLE = False

# Load spaCy model for medical entity recognition
# try:
#     nlp = spacy.load("en_core_web_sm")
# except:
#     logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
#     nlp = None
nlp = None  # Not using spacy for now


class SentimentCategory(Enum):
    """Categories of sentiment analysis"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class PostType(Enum):
    """Types of social media posts"""
    PATIENT_EXPERIENCE = "patient_experience"
    SIDE_EFFECT_REPORT = "side_effect_report"
    EFFICACY_DISCUSSION = "efficacy_discussion"
    COST_CONCERN = "cost_concern"
    COMPARISON = "comparison"
    QUESTION = "question"
    NEWS_SHARING = "news_sharing"
    GENERAL = "general"


@dataclass
class DrugMention:
    """Represents a drug mention in social media"""
    mention_id: str
    platform: str
    drug_name: str
    drug_aliases: List[str]
    company: str
    ticker: str
    post_id: str
    post_url: str
    post_date: datetime
    author: str
    content: str
    sentiment_score: float
    sentiment_category: SentimentCategory
    post_type: PostType
    side_effects_mentioned: List[str]
    efficacy_mentioned: bool
    comparison_drugs: List[str]
    engagement_metrics: Dict[str, int]  # likes, comments, shares
    extracted_insights: Dict[str, any]


class DrugDatabase:
    """Database of drugs and their associated companies"""
    
    def __init__(self, db_path: str = "drug_company_mapping.db"):
        self.db_path = db_path
        self._init_database()
        self._load_drug_mappings()
    
    def _init_database(self):
        """Initialize drug-company mapping database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create drug mapping table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drug_mappings (
                drug_name TEXT PRIMARY KEY,
                generic_name TEXT,
                brand_names TEXT,  -- JSON list
                company TEXT NOT NULL,
                ticker TEXT,
                indications TEXT,  -- JSON list
                approval_date TEXT,
                drug_class TEXT,
                aliases TEXT,  -- JSON list of common misspellings/variations
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create company drugs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_drugs (
                ticker TEXT,
                company_name TEXT,
                drug_name TEXT,
                status TEXT,  -- approved, clinical, discontinued
                PRIMARY KEY (ticker, drug_name)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_drug_mappings(self):
        """Load common drug mappings"""
        # Major drugs and their companies
        drug_data = [
            # Moderna drugs
            ("Spikevax", "COVID-19 vaccine mRNA-1273", ["Moderna COVID vaccine"], "Moderna", "MRNA", ["COVID-19"], "2020-12-18", "Vaccine"),
            ("mRNA-4157", "Personalized cancer vaccine", ["V940", "Moderna cancer vaccine"], "Moderna", "MRNA", ["Melanoma"], "Clinical", "Vaccine"),
            
            # Pfizer drugs
            ("Comirnaty", "COVID-19 vaccine BNT162b2", ["Pfizer COVID vaccine", "BioNTech vaccine"], "Pfizer", "PFE", ["COVID-19"], "2020-12-11", "Vaccine"),
            ("Paxlovid", "Nirmatrelvir/ritonavir", ["Pfizer COVID pill"], "Pfizer", "PFE", ["COVID-19"], "2021-12-22", "Antiviral"),
            ("Eliquis", "Apixaban", [], "Pfizer/BMS", "PFE", ["Atrial fibrillation"], "2012-12-28", "Anticoagulant"),
            
            # J&J drugs
            ("Stelara", "Ustekinumab", [], "Johnson & Johnson", "JNJ", ["Psoriasis", "Crohn's"], "2009-09-25", "Immunosuppressant"),
            ("Darzalex", "Daratumumab", [], "Johnson & Johnson", "JNJ", ["Multiple myeloma"], "2015-11-16", "Monoclonal antibody"),
            
            # Gilead drugs
            ("Veklury", "Remdesivir", ["Gilead COVID drug"], "Gilead", "GILD", ["COVID-19"], "2020-10-22", "Antiviral"),
            ("Biktarvy", "B/F/TAF", [], "Gilead", "GILD", ["HIV"], "2018-02-07", "Antiretroviral"),
            ("Trodelvy", "Sacituzumab govitecan", [], "Gilead", "GILD", ["Breast cancer"], "2020-04-22", "ADC"),
            
            # Biogen drugs
            ("Leqembi", "Lecanemab", ["Eisai Alzheimer's drug"], "Biogen/Eisai", "BIIB", ["Alzheimer's"], "2023-01-06", "Monoclonal antibody"),
            ("Spinraza", "Nusinersen", [], "Biogen", "BIIB", ["SMA"], "2016-12-23", "Antisense oligonucleotide"),
            
            # Common drugs with variations
            ("Humira", "Adalimumab", ["Abbvie arthritis"], "AbbVie", "ABBV", ["RA", "Psoriasis"], "2002-12-31", "TNF inhibitor"),
            ("Keytruda", "Pembrolizumab", ["Merck cancer drug"], "Merck", "MRK", ["Various cancers"], "2014-09-04", "PD-1 inhibitor"),
            ("Opdivo", "Nivolumab", ["BMS cancer drug"], "Bristol Myers Squibb", "BMY", ["Various cancers"], "2014-12-22", "PD-1 inhibitor"),
            
            # Additional common drugs
            ("Ozempic", "Semaglutide", ["Novo Nordisk diabetes"], "Novo Nordisk", "NVO", ["Type 2 Diabetes", "Weight Loss"], "2017-12-05", "GLP-1 agonist"),
            ("Mounjaro", "Tirzepatide", ["Lilly diabetes"], "Eli Lilly", "LLY", ["Type 2 Diabetes", "Obesity"], "2022-05-13", "GLP-1/GIP agonist"),
            ("Wegovy", "Semaglutide", ["Novo weight loss"], "Novo Nordisk", "NVO", ["Weight Loss"], "2021-06-04", "GLP-1 agonist"),
            ("Enbrel", "Etanercept", ["Amgen arthritis"], "Amgen", "AMGN", ["RA", "Psoriasis"], "1998-11-02", "TNF inhibitor"),
            ("Remicade", "Infliximab", ["J&J arthritis"], "Johnson & Johnson", "JNJ", ["RA", "Crohn's"], "1998-08-24", "TNF inhibitor"),
            ("Dupixent", "Dupilumab", ["Sanofi eczema"], "Sanofi/Regeneron", "SNY", ["Eczema", "Asthma"], "2017-03-28", "IL-4/IL-13 inhibitor"),
            ("Repatha", "Evolocumab", ["Amgen cholesterol"], "Amgen", "AMGN", ["High Cholesterol"], "2015-08-27", "PCSK9 inhibitor"),
            ("Skyrizi", "Risankizumab", ["Abbvie psoriasis"], "AbbVie", "ABBV", ["Psoriasis"], "2019-04-23", "IL-23 inhibitor"),
            ("Cosentyx", "Secukinumab", ["Novartis psoriasis"], "Novartis", "NVS", ["Psoriasis", "AS"], "2015-01-21", "IL-17A inhibitor"),
            ("Taltz", "Ixekizumab", ["Lilly psoriasis"], "Eli Lilly", "LLY", ["Psoriasis"], "2016-03-22", "IL-17A inhibitor"),
            ("Entresto", "Sacubitril/valsartan", ["Novartis heart"], "Novartis", "NVS", ["Heart Failure"], "2015-07-07", "ARNI"),
            ("Jardiance", "Empagliflozin", ["Lilly diabetes"], "Eli Lilly/BI", "LLY", ["Type 2 Diabetes", "Heart Failure"], "2014-08-01", "SGLT2 inhibitor"),
            ("Farxiga", "Dapagliflozin", ["AZ diabetes"], "AstraZeneca", "AZN", ["Type 2 Diabetes", "Heart Failure"], "2014-01-08", "SGLT2 inhibitor"),
            ("Rinvoq", "Upadacitinib", ["Abbvie arthritis"], "AbbVie", "ABBV", ["RA", "UC"], "2019-08-16", "JAK inhibitor"),
            ("Xeljanz", "Tofacitinib", ["Pfizer arthritis"], "Pfizer", "PFE", ["RA", "UC"], "2012-11-06", "JAK inhibitor"),
            ("Ocrevus", "Ocrelizumab", ["Roche MS"], "Roche", "RHHBY", ["Multiple Sclerosis"], "2017-03-28", "Anti-CD20"),
            ("Tecfidera", "Dimethyl fumarate", ["Biogen MS"], "Biogen", "BIIB", ["Multiple Sclerosis"], "2013-03-27", "Immunomodulator"),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for drug in drug_data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO drug_mappings 
                    (drug_name, generic_name, brand_names, company, ticker, 
                     indications, approval_date, drug_class, aliases)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    drug[0], drug[1], json.dumps(drug[2]), drug[3], drug[4],
                    json.dumps(drug[5]), drug[6], drug[7],
                    json.dumps(self._generate_aliases(drug[0], drug[1]))
                ))
                
                # Also update company_drugs table
                cursor.execute("""
                    INSERT OR REPLACE INTO company_drugs
                    (ticker, company_name, drug_name, status)
                    VALUES (?, ?, ?, ?)
                """, (drug[4], drug[3], drug[0], "approved" if drug[6] != "Clinical" else "clinical"))
                
            except Exception as e:
                logger.error(f"Error inserting drug {drug[0]}: {e}")
        
        conn.commit()
        conn.close()
    
    def _generate_aliases(self, brand_name: str, generic_name: str) -> List[str]:
        """Generate common variations and misspellings of drug names"""
        aliases = []
        
        # Add lowercase versions
        aliases.append(brand_name.lower())
        aliases.append(generic_name.lower())
        
        # Common misspellings
        if "mab" in generic_name:
            aliases.append(generic_name.replace("mab", ""))
        
        # Remove spaces and hyphens
        aliases.append(brand_name.replace(" ", "").replace("-", ""))
        
        return list(set(aliases))
    
    def find_drug(self, text: str) -> List[Tuple[str, str, str]]:
        """Find drug mentions in text, return (drug_name, company, ticker)"""
        found_drugs = []
        text_lower = text.lower()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search for drug names
        cursor.execute("SELECT drug_name, company, ticker, aliases FROM drug_mappings")
        
        for drug_name, company, ticker, aliases_json in cursor.fetchall():
            # Check main drug name
            if drug_name.lower() in text_lower:
                found_drugs.append((drug_name, company, ticker))
                continue
            
            # Check aliases
            if aliases_json:
                aliases = json.loads(aliases_json)
                for alias in aliases:
                    if alias in text_lower:
                        found_drugs.append((drug_name, company, ticker))
                        break
        
        conn.close()
        
        # If no drugs found in database, return generic entry for the search term
        if not found_drugs and text.strip():
            # Clean up the drug name
            drug_name = text.strip().title()
            found_drugs.append((drug_name, "Unknown Company", "N/A"))
        
        return list(set(found_drugs))  # Remove duplicates
    
    def get_company_drugs(self, ticker: str) -> List[Dict]:
        """Get all drugs for a company by ticker"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.drug_name, d.generic_name, d.indications, d.drug_class, cd.status
            FROM drug_mappings d
            JOIN company_drugs cd ON d.drug_name = cd.drug_name
            WHERE cd.ticker = ?
            ORDER BY cd.status, d.drug_name
        """, (ticker.upper(),))
        
        drugs = []
        for row in cursor.fetchall():
            drugs.append({
                'drug_name': row[0],
                'generic_name': row[1],
                'indications': json.loads(row[2]) if row[2] else [],
                'drug_class': row[3],
                'status': row[4]
            })
        
        conn.close()
        return drugs


class SocialMediaSentimentAnalyzer:
    """Main analyzer for social media drug sentiment"""
    
    def __init__(self):
        self.drug_db = DrugDatabase()
        self.vader = SentimentIntensityAnalyzer()
        
        # Import API configuration
        try:
            import api_config
            self.config = api_config
        except ImportError:
            logger.warning("api_config.py not found, using demo mode")
            self.config = None
        
        self._init_sentiment_db()
        self._init_reddit_client()
        self._init_twitter_client()
        self.medical_terms = self._load_medical_terms()
    
    def _init_sentiment_db(self):
        """Initialize sentiment analysis database"""
        self.sentiment_db = "social_media_sentiment.db"
        conn = sqlite3.connect(self.sentiment_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drug_mentions (
                mention_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                drug_name TEXT NOT NULL,
                company TEXT,
                ticker TEXT,
                post_id TEXT,
                post_url TEXT,
                post_date DATETIME,
                author TEXT,
                content TEXT,
                sentiment_score REAL,
                sentiment_category TEXT,
                post_type TEXT,
                side_effects TEXT,  -- JSON list
                efficacy_mentioned BOOLEAN,
                comparison_drugs TEXT,  -- JSON list
                engagement_metrics TEXT,  -- JSON dict
                extracted_insights TEXT,  -- JSON dict
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_summary (
                drug_name TEXT,
                ticker TEXT,
                platform TEXT,
                date DATE,
                total_mentions INTEGER,
                avg_sentiment REAL,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                top_side_effects TEXT,  -- JSON list
                top_topics TEXT,  -- JSON list
                PRIMARY KEY (drug_name, platform, date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_reddit_client(self):
        """Initialize Reddit API client"""
        try:
            # Check if we have API config
            if self.config and not self.config.USE_DEMO_MODE:
                if self.config.REDDIT_CLIENT_ID and self.config.REDDIT_CLIENT_SECRET:
                    self.reddit = praw.Reddit(
                        client_id=self.config.REDDIT_CLIENT_ID,
                        client_secret=self.config.REDDIT_CLIENT_SECRET,
                        user_agent=self.config.REDDIT_USER_AGENT
                    )
                    logger.info("Reddit API client initialized with credentials")
                else:
                    logger.error("Reddit API credentials missing! Please add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env file")
                    logger.error("See SETUP_REAL_APIS.md for instructions on getting Reddit API credentials")
                    self.reddit = None
            else:
                logger.info("Using demo mode for Reddit")
                self.reddit = None
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            self.reddit = None
    
    def _init_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            # Check if we have API config
            if self.config and not self.config.USE_DEMO_MODE:
                if self.config.TWITTER_BEARER_TOKEN:
                    self.twitter = tweepy.Client(bearer_token=self.config.TWITTER_BEARER_TOKEN)
                    logger.info("Twitter API v2 client initialized with Bearer Token")
                elif self.config.TWITTER_API_KEY and self.config.TWITTER_API_SECRET:
                    # Try to initialize with API v1.1 credentials
                    try:
                        auth = tweepy.OAuth1UserHandler(
                            self.config.TWITTER_API_KEY,
                            self.config.TWITTER_API_SECRET,
                            self.config.TWITTER_ACCESS_TOKEN,
                            self.config.TWITTER_ACCESS_SECRET
                        )
                        api = tweepy.API(auth, wait_on_rate_limit=True)
                        # Test the connection
                        api.verify_credentials()
                        self.twitter = api
                        logger.info("Twitter API v1.1 client initialized with API Key/Secret")
                    except Exception as e:
                        logger.warning(f"Twitter API v1.1 setup failed: {e}")
                        logger.info(f"Twitter API key detected: {self.config.TWITTER_API_KEY[:10]}...")
                        logger.info("Using enhanced Twitter demo mode with API key")
                        self.twitter = "api_key_present"  # Marker for API key presence
                elif self.config.TWITTER_API_KEY:
                    # Only have API key, use demo mode but mark as having credentials
                    logger.info(f"Twitter API key detected: {self.config.TWITTER_API_KEY[:10]}...")
                    logger.warning("Missing TWITTER_BEARER_TOKEN or TWITTER_API_SECRET for full API access")
                    logger.info("Using enhanced Twitter demo mode with API key")
                    self.twitter = "api_key_present"  # Marker for API key presence
                else:
                    logger.error("Twitter API credentials missing! Please add TWITTER_BEARER_TOKEN or TWITTER_API_KEY to .env file")
                    logger.error("See SETUP_REAL_APIS.md for instructions on getting Twitter API credentials")
                    self.twitter = None
            else:
                logger.info("Using demo mode for Twitter")
                self.twitter = None
        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
            self.twitter = None
    
    def _parse_post_date(self, date_value) -> datetime:
        """Parse various date formats from social media posts"""
        if isinstance(date_value, datetime):
            return date_value
            
        if isinstance(date_value, str):
            # Handle ISO format with 'Z' timezone
            if date_value.endswith('Z'):
                date_value = date_value[:-1] + '+00:00'
            
            # Try parsing as ISO format
            try:
                return datetime.fromisoformat(date_value)
            except ValueError:
                pass
            
            # Try other common formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%a %b %d %H:%M:%S %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
        
        # If all parsing fails, return current time
        logger.warning(f"Could not parse date: {date_value}")
        return datetime.now()
    
    def _load_medical_terms(self) -> Dict[str, List[str]]:
        """Load medical terminology for better extraction"""
        return {
            'side_effects': [
                'nausea', 'headache', 'dizziness', 'fatigue', 'rash', 'diarrhea',
                'constipation', 'insomnia', 'anxiety', 'depression', 'weight gain',
                'weight loss', 'hair loss', 'joint pain', 'muscle pain', 'fever',
                'chills', 'injection site reaction', 'allergic reaction', 'swelling',
                'bruising', 'bleeding', 'liver', 'kidney', 'heart', 'blood pressure'
            ],
            'efficacy_terms': [
                'working', 'effective', 'helped', 'improved', 'better', 'worse',
                'no change', 'cured', 'remission', 'responding', 'failed', 'stopped working'
            ],
            'comparison_terms': [
                'compared to', 'versus', 'vs', 'better than', 'worse than',
                'switched from', 'switching to', 'instead of'
            ]
        }
    
    async def analyze_drug_sentiment(self, drug_name: str) -> Dict:
        """Analyze sentiment for a specific drug across all platforms"""
        logger.info(f"Analyzing sentiment for {drug_name}")
        
        # Always use real scraping when available
        if REAL_SCRAPER_AVAILABLE:
            return await self.analyze_drug_sentiment_with_posts(drug_name)
        
        # Get drug info
        drug_info = self.drug_db.find_drug(drug_name)
        if drug_info:
            drug_name, company, ticker = drug_info[0]
        else:
            # Handle unknown drugs
            drug_name = drug_name.strip().title()
            company = "Unknown Company"
            ticker = "N/A"
        
        # Collect data from all platforms
        all_mentions = []
        
        # Reddit analysis
        reddit_mentions = await self._analyze_reddit(drug_name)
        all_mentions.extend(reddit_mentions)
        
        # Twitter analysis
        twitter_mentions = await self._analyze_twitter(drug_name)
        all_mentions.extend(twitter_mentions)
        
        # Patient forums
        forum_mentions = await self._analyze_patient_forums(drug_name)
        all_mentions.extend(forum_mentions)
        
        # StockTwits
        stocktwits_mentions = await self._analyze_stocktwits(ticker)
        all_mentions.extend(stocktwits_mentions)
        
        # Aggregate results
        analysis = self._aggregate_sentiment_analysis(all_mentions, drug_name, company, ticker)
        
        # Save to database
        self._save_mentions(all_mentions)
        self._update_summary(drug_name, ticker, analysis)
        
        return analysis
    
    async def analyze_drug_sentiment_with_posts(self, drug_name: str) -> Dict:
        """Analyze sentiment with actual posts (excluding Reddit)"""
        logger.info(f"Analyzing sentiment with posts for {drug_name}")
        
        # Check if we should use real scraping
        use_real_scraping = REAL_SCRAPER_AVAILABLE  # Always use real scraping when available
        
        if use_real_scraping:
            logger.info(f"Using REAL WEB SCRAPING for {drug_name}")
            try:
                # Use real data scraper
                real_data = await get_real_social_data(drug_name)
                
                # Convert to DrugMention format
                all_mentions = []
                drug_info = self.drug_db.find_drug(drug_name)
                company = drug_info[0][1] if drug_info else "Unknown Company"
                ticker = drug_info[0][2] if drug_info else "N/A"
                
                for post in real_data['posts']:
                    # Skip if no content
                    if not post.get('content'):
                        continue
                    
                    # Filter for drug relevance (enhanced filtering)
                    if not self._is_post_relevant_to_drug(post['content'], drug_name):
                        continue
                        
                    # Analyze sentiment
                    sentiment_score, sentiment_category = self._analyze_sentiment(post['content'])
                    
                    # Create mention
                    mention = DrugMention(
                        mention_id=f"{post['platform']}_{post.get('id', hash(post['content']))}",
                        platform=post['platform'],
                        drug_name=drug_name,
                        drug_aliases=[],
                        company=company,
                        ticker=ticker,
                        post_id=str(post.get('id', '')),
                        post_url=post.get('url', ''),
                        post_date=self._parse_post_date(post['date']),
                        author=post['author'],
                        content=post['content'],
                        sentiment_score=sentiment_score,
                        sentiment_category=sentiment_category,
                        post_type=self._classify_post_type(post['content']),
                        side_effects_mentioned=self._extract_side_effects(post['content']),
                        efficacy_mentioned=self._check_efficacy_mention(post['content']),
                        comparison_drugs=self._extract_drug_comparisons(post['content']),
                        engagement_metrics=post.get('engagement', {}),
                        extracted_insights={'source': 'real_web_scraping'}
                    )
                    all_mentions.append(mention)
                
                logger.info(f"Retrieved {len(all_mentions)} REAL mentions from web scraping")
                
                # Aggregate and return results
                analysis = self._aggregate_sentiment_analysis(all_mentions, drug_name, company, ticker)
                analysis['data_source'] = 'real_web_scraping'
                
                # Add recent posts with proper JSON serialization
                analysis['recent_posts'] = []
                for mention in all_mentions[:10]:
                    post_data = asdict(mention)
                    # Convert enum values to strings for JSON serialization
                    if 'sentiment_category' in post_data:
                        post_data['sentiment_category'] = post_data['sentiment_category'].value if hasattr(post_data['sentiment_category'], 'value') else str(post_data['sentiment_category'])
                    if 'post_type' in post_data:
                        post_data['post_type'] = post_data['post_type'].value if hasattr(post_data['post_type'], 'value') else str(post_data['post_type'])
                    # Convert datetime to string
                    if 'post_date' in post_data and hasattr(post_data['post_date'], 'isoformat'):
                        post_data['post_date'] = post_data['post_date'].isoformat()
                    analysis['recent_posts'].append(post_data)
                
                return analysis
                
            except Exception as e:
                logger.error(f"Error using real web scraping: {e}")
                logger.info("Falling back to demo data")
                # Fall through to existing logic
        
        # Original logic continues here...
        # Get drug info
        drug_info = self.drug_db.find_drug(drug_name)
        if drug_info:
            drug_name, company, ticker = drug_info[0]
        else:
            # Handle unknown drugs
            drug_name = drug_name.strip().title()
            company = "Unknown Company"
            ticker = "N/A"
        
        # Collect data from all platforms EXCEPT Reddit
        all_mentions = []
        
        # Twitter analysis
        twitter_mentions = await self._analyze_twitter(drug_name)
        all_mentions.extend(twitter_mentions)
        
        # Patient forums
        forum_mentions = await self._analyze_patient_forums(drug_name)
        all_mentions.extend(forum_mentions)
        
        # StockTwits
        if ticker != "N/A":
            stocktwits_mentions = await self._analyze_stocktwits(ticker)
            all_mentions.extend(stocktwits_mentions)
        
        # Aggregate results with posts
        analysis = self._aggregate_sentiment_analysis(all_mentions, drug_name, company, ticker)
        
        # Add recent posts to the analysis
        analysis['recent_posts'] = []
        for mention in all_mentions[:10]:  # Get 10 most recent
            post_data = asdict(mention)
            # Convert enum values to strings
            post_data['sentiment_category'] = post_data['sentiment_category'].value
            post_data['post_type'] = post_data['post_type'].value
            # Convert datetime to string
            if 'post_date' in post_data and hasattr(post_data['post_date'], 'isoformat'):
                post_data['post_date'] = post_data['post_date'].isoformat()
            analysis['recent_posts'].append(post_data)
        
        # Save to database
        self._save_mentions(all_mentions)
        self._update_summary(drug_name, ticker, analysis)
        
        return analysis
    
    async def analyze_company_drugs(self, ticker: str) -> Dict:
        """Analyze sentiment for all drugs from a company"""
        logger.info(f"Analyzing sentiment for all drugs from {ticker}")
        
        # Get all drugs for the company
        drugs = self.drug_db.get_company_drugs(ticker)
        if not drugs:
            return {"error": f"No drugs found for ticker {ticker}"}
        
        # Analyze each drug
        company_analysis = {
            "ticker": ticker,
            "drugs_analyzed": len(drugs),
            "drug_sentiments": {},
            "overall_sentiment": 0,
            "top_concerns": [],
            "top_positives": [],
            "analysis_date": datetime.now().isoformat()
        }
        
        for drug in drugs:
            drug_analysis = await self.analyze_drug_sentiment(drug['drug_name'])
            company_analysis["drug_sentiments"][drug['drug_name']] = drug_analysis
        
        # Calculate overall company sentiment
        sentiments = []
        all_concerns = []
        all_positives = []
        
        for drug_name, analysis in company_analysis["drug_sentiments"].items():
            if 'average_sentiment' in analysis:
                sentiments.append(analysis['average_sentiment'])
                all_concerns.extend(analysis.get('top_concerns', []))
                all_positives.extend(analysis.get('top_positives', []))
        
        if sentiments:
            company_analysis["overall_sentiment"] = np.mean(sentiments)
            
        # Get top concerns and positives
        concern_counter = Counter(all_concerns)
        positive_counter = Counter(all_positives)
        
        company_analysis["top_concerns"] = [item for item, _ in concern_counter.most_common(5)]
        company_analysis["top_positives"] = [item for item, _ in positive_counter.most_common(5)]
        
        return company_analysis
    
    async def _analyze_reddit(self, drug_name: str) -> List[DrugMention]:
        """Analyze Reddit posts and comments mentioning the drug"""
        mentions = []
        
        # Check if we have real Reddit credentials
        if self.reddit and self.config and not self.config.USE_DEMO_MODE:
            logger.info(f"Using REAL Reddit API for {drug_name}")
            try:
                # Search across multiple relevant subreddits
                all_subreddits = []
                for category in self.config.REDDIT_SUBREDDITS.values():
                    all_subreddits.extend(category)
                
                # Remove duplicates and create subreddit string
                subreddits = list(set(all_subreddits))
                subreddit_str = '+'.join(subreddits[:50])  # Reddit limits to 50 subreddits
                
                # Get subreddit object
                subreddit = self.reddit.subreddit(subreddit_str)
                
                # Search for drug mentions in posts (last month)
                search_query = f'"{drug_name}"'
                logger.info(f"Searching Reddit for: {search_query}")
                
                post_count = 0
                for submission in subreddit.search(search_query, time_filter='month', limit=100):
                    mention = self._analyze_reddit_post(submission, drug_name)
                    if mention:
                        mentions.append(mention)
                        post_count += 1
                    
                    # Also analyze top comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:10]:  # Top 10 comments
                        comment_mention = self._analyze_reddit_comment(
                            comment, drug_name, submission.url
                        )
                        if comment_mention:
                            mentions.append(comment_mention)
                
                logger.info(f"Retrieved {len(mentions)} REAL Reddit mentions for {drug_name} ({post_count} posts)")
                
                # If we found very few mentions, also search in general medicine subreddit
                if len(mentions) < 10:
                    logger.info(f"Found only {len(mentions)} mentions, searching r/medicine specifically")
                    medicine_sub = self.reddit.subreddit('medicine')
                    for submission in medicine_sub.search(drug_name, time_filter='year', limit=25):
                        mention = self._analyze_reddit_post(submission, drug_name)
                        if mention:
                            mentions.append(mention)
                            
            except Exception as e:
                logger.error(f"Reddit API error: {e}")
                logger.error("Falling back to demo data")
                return self._get_demo_reddit_data(drug_name)
        
        else:
            # No Reddit credentials or in demo mode
            if not self.reddit:
                logger.warning(f"No Reddit credentials - using DEMO data for {drug_name}")
                logger.warning("To get real Reddit data, add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to your .env file")
            else:
                logger.info(f"Demo mode enabled - using DEMO data for {drug_name}")
            return self._get_demo_reddit_data(drug_name)
        
        return mentions
    
    def _analyze_reddit_post(self, submission, drug_name: str) -> Optional[DrugMention]:
        """Analyze a Reddit submission"""
        try:
            content = f"{submission.title} {submission.selftext}"
            
            # Skip if too short
            if len(content.split()) < 10:
                return None
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self._analyze_sentiment(content)
            
            # Extract insights
            post_type = self._classify_post_type(content)
            side_effects = self._extract_side_effects(content)
            efficacy = self._check_efficacy_mention(content)
            comparisons = self._extract_drug_comparisons(content)
            
            # Get drug info
            drug_info = self.drug_db.find_drug(drug_name)
            company = drug_info[0][1] if drug_info else ""
            ticker = drug_info[0][2] if drug_info else ""
            
            mention = DrugMention(
                mention_id=f"reddit_{submission.id}",
                platform="Reddit",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=submission.id,
                post_url=f"https://reddit.com{submission.permalink}",
                post_date=datetime.fromtimestamp(submission.created_utc),
                author=str(submission.author) if submission.author else "deleted",
                content=content[:1000],  # Truncate for storage
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=post_type,
                side_effects_mentioned=side_effects,
                efficacy_mentioned=efficacy,
                comparison_drugs=comparisons,
                engagement_metrics={
                    "score": submission.score,
                    "comments": submission.num_comments,
                    "upvote_ratio": submission.upvote_ratio
                },
                extracted_insights={}
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit post: {e}")
            return None
    
    def _analyze_reddit_comment(self, comment, drug_name: str, post_url: str) -> Optional[DrugMention]:
        """Analyze a Reddit comment"""
        try:
            content = comment.body
            
            # Skip if too short or deleted
            if len(content.split()) < 5 or content == "[deleted]":
                return None
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self._analyze_sentiment(content)
            
            # Extract insights
            post_type = self._classify_post_type(content)
            side_effects = self._extract_side_effects(content)
            efficacy = self._check_efficacy_mention(content)
            comparisons = self._extract_drug_comparisons(content)
            
            # Get drug info
            drug_info = self.drug_db.find_drug(drug_name)
            company = drug_info[0][1] if drug_info else ""
            ticker = drug_info[0][2] if drug_info else ""
            
            mention = DrugMention(
                mention_id=f"reddit_comment_{comment.id}",
                platform="Reddit",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=comment.id,
                post_url=post_url,
                post_date=datetime.fromtimestamp(comment.created_utc),
                author=str(comment.author) if comment.author else "deleted",
                content=content[:500],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=post_type,
                side_effects_mentioned=side_effects,
                efficacy_mentioned=efficacy,
                comparison_drugs=comparisons,
                engagement_metrics={
                    "score": comment.score
                },
                extracted_insights={}
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit comment: {e}")
            return None
    
    def _get_demo_reddit_data(self, drug_name: str) -> List[DrugMention]:
        """Generate demo Reddit data for testing"""
        demo_posts = [
            {
                "content": f"I've been on {drug_name} for 3 months now and it's been life-changing. My symptoms have improved dramatically and the side effects are minimal.",
                "score": 156,
                "comments": 23,
                "date": datetime.now() - timedelta(days=2)
            },
            {
                "content": f"Started {drug_name} last week. Experiencing some nausea and headaches but hoping they'll subside. Anyone else have these side effects?",
                "score": 89,
                "comments": 45,
                "date": datetime.now() - timedelta(days=5)
            },
            {
                "content": f"Switched from Humira to {drug_name} and it's working much better for me. Less injection site reactions and better symptom control.",
                "score": 234,
                "comments": 67,
                "date": datetime.now() - timedelta(days=10)
            }
        ]
        
        mentions = []
        drug_info = self.drug_db.find_drug(drug_name)
        company = drug_info[0][1] if drug_info else "Unknown"
        ticker = drug_info[0][2] if drug_info else "N/A"
        
        for i, post in enumerate(demo_posts):
            sentiment_score, sentiment_category = self._analyze_sentiment(post["content"])
            
            mention = DrugMention(
                mention_id=f"reddit_demo_{i}",
                platform="Reddit",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=f"demo_{i}",
                post_url=f"https://reddit.com/r/demo/comments/demo{i}",
                post_date=post["date"],
                author=f"demo_user_{i}",
                content=post["content"],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=self._classify_post_type(post["content"]),
                side_effects_mentioned=self._extract_side_effects(post["content"]),
                efficacy_mentioned=self._check_efficacy_mention(post["content"]),
                comparison_drugs=self._extract_drug_comparisons(post["content"]),
                engagement_metrics={
                    "score": post["score"],
                    "comments": post["comments"],
                    "upvote_ratio": 0.85
                },
                extracted_insights={}
            )
            mentions.append(mention)
        
        return mentions
    
    async def _analyze_twitter(self, drug_name: str) -> List[DrugMention]:
        """Analyze Twitter/X posts mentioning the drug"""
        mentions = []
        
        # Check if we have real Twitter credentials
        if self.config and self.config.TWITTER_BEARER_TOKEN and not self.config.USE_DEMO_MODE:
            # Real Twitter API v2 implementation
            logger.info(f"Using REAL Twitter API for {drug_name}")
            try:
                # Initialize Twitter client if not already done
                if not isinstance(self.twitter, tweepy.Client):
                    self.twitter = tweepy.Client(bearer_token=self.config.TWITTER_BEARER_TOKEN)
                
                # Build search query - exclude retweets and get recent English tweets
                query = f'"{drug_name}" -is:retweet lang:en'
                
                # Search for recent tweets (last 7 days for free tier)
                tweets = self.twitter.search_recent_tweets(
                    query=query,
                    max_results=100,  # Max allowed per request
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'entities'],
                    user_fields=['name', 'username', 'verified', 'description'],
                    expansions=['author_id']
                )
                
                if tweets.data:
                    # Create user lookup
                    users = {u.id: u for u in (tweets.includes.get('users', []) or [])}
                    
                    for tweet in tweets.data:
                        # Get author info
                        author = users.get(tweet.author_id, None)
                        author_username = author.username if author else f"user_{tweet.author_id}"
                        
                        mention = self._analyze_tweet_v2(tweet, drug_name, author_username)
                        if mention:
                            mentions.append(mention)
                    
                    logger.info(f"Retrieved {len(mentions)} REAL Twitter mentions for {drug_name}")
                else:
                    logger.warning(f"No tweets found for {drug_name}")
                            
            except tweepy.TooManyRequests:
                logger.error("Twitter API rate limit exceeded. Please wait 15 minutes.")
                return self._get_demo_twitter_data(drug_name)
            except tweepy.Unauthorized:
                logger.error("Twitter API authentication failed. Check your Bearer Token.")
                return self._get_demo_twitter_data(drug_name)
            except Exception as e:
                logger.error(f"Twitter API error: {e}")
                logger.error("Falling back to demo data")
                return self._get_demo_twitter_data(drug_name)
        
        elif self.twitter == "api_key_present":
            # API key present but no bearer token - can't make real calls
            logger.warning(f"Twitter API key found but Bearer Token missing - using DEMO data for {drug_name}")
            logger.warning("To get real Twitter data, add TWITTER_BEARER_TOKEN to your .env file")
            logger.warning("See SETUP_REAL_APIS.md for instructions")
            return self._get_demo_twitter_data(drug_name)
        else:
            # No Twitter credentials at all
            logger.info(f"No Twitter credentials - using DEMO data for {drug_name}")
            return self._get_demo_twitter_data(drug_name)
        
        return mentions
    
    def _analyze_simulated_tweet(self, tweet_data: Dict, drug_name: str) -> Optional[DrugMention]:
        """Analyze a simulated tweet from Twitter simulator"""
        try:
            content = tweet_data["text"]
            
            # Skip spam/joke posts
            if self._is_joke_or_spam(content):
                return None
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self._analyze_sentiment(content)
            
            # Extract insights
            post_type = self._classify_post_type(content)
            side_effects = self._extract_side_effects(content)
            efficacy = self._check_efficacy_mention(content)
            comparisons = self._extract_drug_comparisons(content)
            
            # Get drug info
            drug_info = self.drug_db.find_drug(drug_name)
            company = drug_info[0][1] if drug_info else ""
            ticker = drug_info[0][2] if drug_info else ""
            
            mention = DrugMention(
                mention_id=f"twitter_{tweet_data['id']}",
                platform="Twitter",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=tweet_data['id'],
                post_url=f"https://twitter.com/{tweet_data['author_username']}/status/{tweet_data['id']}",
                post_date=tweet_data['created_at'],
                author=f"@{tweet_data['author_username']}",
                content=content,
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=post_type,
                side_effects_mentioned=side_effects,
                efficacy_mentioned=efficacy,
                comparison_drugs=comparisons,
                engagement_metrics=tweet_data['public_metrics'],
                extracted_insights={"profile_type": tweet_data.get("profile_type", "unknown")}
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing simulated tweet: {e}")
            return None
    
    def _analyze_tweet(self, tweet, drug_name: str) -> Optional[DrugMention]:
        """Analyze a single tweet"""
        try:
            content = tweet.text
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self._analyze_sentiment(content)
            
            # Extract insights
            post_type = self._classify_post_type(content)
            side_effects = self._extract_side_effects(content)
            efficacy = self._check_efficacy_mention(content)
            comparisons = self._extract_drug_comparisons(content)
            
            # Get drug info
            drug_info = self.drug_db.find_drug(drug_name)
            company = drug_info[0][1] if drug_info else ""
            ticker = drug_info[0][2] if drug_info else ""
            
            mention = DrugMention(
                mention_id=f"twitter_{tweet.id}",
                platform="Twitter",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=str(tweet.id),
                post_url=f"https://twitter.com/user/status/{tweet.id}",
                post_date=tweet.created_at,
                author=tweet.author_id,
                content=content,
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=post_type,
                side_effects_mentioned=side_effects,
                efficacy_mentioned=efficacy,
                comparison_drugs=comparisons,
                engagement_metrics=tweet.public_metrics,
                extracted_insights={}
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing tweet: {e}")
            return None
    
    def _analyze_tweet_v2(self, tweet, drug_name: str, author_username: str) -> Optional[DrugMention]:
        """Analyze a tweet from Twitter API v2 with enhanced data"""
        try:
            content = tweet.text
            
            # Skip spam/joke posts
            if self._is_joke_or_spam(content):
                return None
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self._analyze_sentiment(content)
            
            # Extract insights
            post_type = self._classify_post_type(content)
            side_effects = self._extract_side_effects(content)
            efficacy = self._check_efficacy_mention(content)
            comparisons = self._extract_drug_comparisons(content)
            
            # Get drug info
            drug_info = self.drug_db.find_drug(drug_name)
            company = drug_info[0][1] if drug_info else ""
            ticker = drug_info[0][2] if drug_info else ""
            
            # Get engagement metrics
            metrics = tweet.public_metrics or {}
            engagement = {
                "like_count": metrics.get('like_count', 0),
                "retweet_count": metrics.get('retweet_count', 0),
                "reply_count": metrics.get('reply_count', 0),
                "quote_count": metrics.get('quote_count', 0),
                "impression_count": metrics.get('impression_count', 0)
            }
            
            # Extract additional insights from context annotations
            insights = {}
            if hasattr(tweet, 'context_annotations'):
                # Extract domain and entity information
                domains = []
                entities = []
                for annotation in (tweet.context_annotations or []):
                    if 'domain' in annotation:
                        domains.append(annotation['domain'].get('name', ''))
                    if 'entity' in annotation:
                        entities.append(annotation['entity'].get('name', ''))
                insights['domains'] = list(set(domains))
                insights['entities'] = list(set(entities))
            
            mention = DrugMention(
                mention_id=f"twitter_{tweet.id}",
                platform="Twitter",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=str(tweet.id),
                post_url=f"https://twitter.com/{author_username}/status/{tweet.id}",
                post_date=tweet.created_at,
                author=f"@{author_username}",
                content=content,
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=post_type,
                side_effects_mentioned=side_effects,
                efficacy_mentioned=efficacy,
                comparison_drugs=comparisons,
                engagement_metrics=engagement,
                extracted_insights=insights
            )
            
            return mention
            
        except Exception as e:
            logger.error(f"Error analyzing tweet v2: {e}")
            return None
    
    def _get_demo_twitter_data(self, drug_name: str) -> List[DrugMention]:
        """Generate realistic demo Twitter data using enhanced generator"""
        try:
            from enhanced_demo_data import demo_generator
        except ImportError:
            logger.warning("Enhanced demo generator not available, using basic demo data")
            # Fallback to simple demo data
            return self._get_basic_demo_twitter_data(drug_name)
        
        # Generate varied posts for this drug
        demo_posts = demo_generator.generate_posts(drug_name, "Twitter", count=30)
        
        mentions = []
        drug_info = self.drug_db.find_drug(drug_name)
        company = drug_info[0][1] if drug_info else "Unknown"
        ticker = drug_info[0][2] if drug_info else "N/A"
        
        for post in demo_posts:
            # Skip spam/joke posts
            if demo_generator._is_spam(post["content"]):
                continue
                
            sentiment_score, sentiment_category = self._analyze_sentiment(post["content"])
            
            mention = DrugMention(
                mention_id=f"twitter_{post['post_id']}",
                platform="Twitter",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=post['post_id'],
                post_url=f"https://twitter.com/{post['author']}/status/{post['post_id']}",
                post_date=post["date"],
                author=post["author"],
                content=post["content"],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=self._classify_post_type(post["content"]),
                side_effects_mentioned=self._extract_side_effects(post["content"]),
                efficacy_mentioned=self._check_efficacy_mention(post["content"]),
                comparison_drugs=self._extract_drug_comparisons(post["content"]),
                engagement_metrics={
                    "like_count": post["engagement"]["likes"],
                    "retweet_count": post["engagement"]["retweets"],
                    "reply_count": post["engagement"]["replies"],
                    "quote_count": random.randint(0, 10)
                },
                extracted_insights={}
            )
            mentions.append(mention)
        
        return mentions
    
    def _get_basic_demo_twitter_data(self, drug_name: str) -> List[DrugMention]:
        """Basic fallback demo data"""
        demo_tweets = [
            {
                "content": f"Day 30 on {drug_name} - Energy levels up, joint pain down. Finally feeling like myself again! #ChronicIllness",
                "likes": 342,
                "retweets": 45,
                "date": datetime.now() - timedelta(hours=6)
            },
            {
                "content": f"Insurance denied {drug_name} again. $2000/month out of pocket is impossible. Why is healthcare like this? 😔",
                "likes": 1205,
                "retweets": 456,
                "date": datetime.now() - timedelta(days=1)
            }
        ]
        
        mentions = []
        drug_info = self.drug_db.find_drug(drug_name)
        company = drug_info[0][1] if drug_info else "Unknown"
        ticker = drug_info[0][2] if drug_info else "N/A"
        
        for i, tweet in enumerate(demo_tweets):
            sentiment_score, sentiment_category = self._analyze_sentiment(tweet["content"])
            
            mention = DrugMention(
                mention_id=f"twitter_demo_{i}",
                platform="Twitter",
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=f"demo_tweet_{i}",
                post_url=f"https://twitter.com/demo/status/demo{i}",
                post_date=tweet["date"],
                author=f"demo_twitter_user_{i}",
                content=tweet["content"],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=self._classify_post_type(tweet["content"]),
                side_effects_mentioned=self._extract_side_effects(tweet["content"]),
                efficacy_mentioned=self._check_efficacy_mention(tweet["content"]),
                comparison_drugs=self._extract_drug_comparisons(tweet["content"]),
                engagement_metrics={
                    "like_count": tweet["likes"],
                    "retweet_count": tweet["retweets"],
                    "reply_count": 23,
                    "quote_count": 5
                },
                extracted_insights={}
            )
            mentions.append(mention)
        
        return mentions
    
    async def _analyze_patient_forums(self, drug_name: str) -> List[DrugMention]:
        """Analyze patient forum posts (placeholder for actual scraping)"""
        # This would scrape forums like PatientsLikeMe, HealthUnlocked, etc.
        # For now, return demo data
        return self._get_demo_forum_data(drug_name)
    
    def _get_demo_forum_data(self, drug_name: str) -> List[DrugMention]:
        """Generate realistic demo patient forum data using enhanced generator"""
        try:
            from enhanced_demo_data import demo_generator
        except ImportError:
            logger.warning("Enhanced demo generator not available, using basic demo data")
            # Fallback to simple demo data
            return self._get_basic_demo_forum_data(drug_name)
        
        # Generate varied posts for this drug
        demo_posts = demo_generator.generate_posts(drug_name, "PatientForum", count=20)
        
        mentions = []
        drug_info = self.drug_db.find_drug(drug_name)
        company = drug_info[0][1] if drug_info else "Unknown"
        ticker = drug_info[0][2] if drug_info else "N/A"
        
        forums = ["PatientsLikeMe", "HealthUnlocked", "DailyStrength", "Inspire"]
        
        for post in demo_posts:
            # Skip spam/joke posts
            if demo_generator._is_spam(post["content"]):
                continue
                
            sentiment_score, sentiment_category = self._analyze_sentiment(post["content"])
            forum_name = random.choice(forums)
            
            mention = DrugMention(
                mention_id=f"forum_{post['post_id']}",
                platform=forum_name,
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=post['post_id'],
                post_url=f"https://{forum_name.lower()}.com/post/{post['post_id']}",
                post_date=post["date"],
                author=post["author"],
                content=post["content"],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=self._classify_post_type(post["content"]),
                side_effects_mentioned=self._extract_side_effects(post["content"]),
                efficacy_mentioned=self._check_efficacy_mention(post["content"]),
                comparison_drugs=self._extract_drug_comparisons(post["content"]),
                engagement_metrics=post["engagement"],
                extracted_insights={}
            )
            mentions.append(mention)
        
        return mentions
    
    def _get_basic_demo_forum_data(self, drug_name: str) -> List[DrugMention]:
        """Basic fallback demo forum data"""
        demo_posts = [
            {
                "content": f"I've been on {drug_name} for 6 months. Started at 50mg, now at 100mg. The fatigue was rough the first month but has improved. My condition is much better controlled now.",
                "forum": "PatientsLikeMe",
                "date": datetime.now() - timedelta(days=3)
            }
        ]
        
        mentions = []
        drug_info = self.drug_db.find_drug(drug_name)
        company = drug_info[0][1] if drug_info else "Unknown"
        ticker = drug_info[0][2] if drug_info else "N/A"
        
        for i, post in enumerate(demo_posts):
            sentiment_score, sentiment_category = self._analyze_sentiment(post["content"])
            
            mention = DrugMention(
                mention_id=f"forum_demo_{i}",
                platform=post["forum"],
                drug_name=drug_name,
                drug_aliases=[],
                company=company,
                ticker=ticker,
                post_id=f"forum_post_{i}",
                post_url=f"https://forum.example.com/post/{i}",
                post_date=post["date"],
                author=f"PatientUser{i}",
                content=post["content"],
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                post_type=PostType.PATIENT_EXPERIENCE,
                side_effects_mentioned=self._extract_side_effects(post["content"]),
                efficacy_mentioned=True,
                comparison_drugs=[],
                engagement_metrics={"views": 234, "replies": 12},
                extracted_insights={}
            )
            mentions.append(mention)
        
        return mentions
    
    async def _analyze_stocktwits(self, ticker: str) -> List[DrugMention]:
        """Analyze StockTwits sentiment for biotech stocks"""
        if not ticker or ticker == "N/A":
            return []
            
        # Find drugs for this ticker
        company_drugs = self.drug_db.get_company_drugs(ticker)
        if not company_drugs:
            return []
            
        # For demo mode, generate StockTwits data
        return self._get_demo_stocktwits_data(ticker, company_drugs)
    
    def _get_demo_stocktwits_data(self, ticker: str, company_drugs: List[Dict]) -> List[DrugMention]:
        """Generate realistic demo StockTwits data"""
        try:
            from enhanced_demo_data import demo_generator
        except ImportError:
            return []
        
        mentions = []
        
        # Generate posts for main drugs from this company
        for drug_data in company_drugs[:3]:  # Top 3 drugs
            drug_name = drug_data['drug_name']
            demo_posts = demo_generator.generate_posts(drug_name, "StockTwits", count=10)
            
            for post in demo_posts:
                if demo_generator._is_spam(post["content"]):
                    continue
                    
                sentiment_score, sentiment_category = self._analyze_sentiment(post["content"])
                
                mention = DrugMention(
                    mention_id=f"stocktwits_{post['post_id']}",
                    platform="StockTwits",
                    drug_name=drug_name,
                    drug_aliases=[],
                    company=ticker,
                    ticker=ticker,
                    post_id=post['post_id'],
                    post_url=f"https://stocktwits.com/symbol/{ticker}/message/{post['post_id']}",
                    post_date=post["date"],
                    author=post["author"],
                    content=post["content"],
                    sentiment_score=sentiment_score,
                    sentiment_category=sentiment_category,
                    post_type=self._classify_post_type(post["content"]),
                    side_effects_mentioned=[],  # StockTwits rarely discusses side effects
                    efficacy_mentioned=self._check_efficacy_mention(post["content"]),
                    comparison_drugs=self._extract_drug_comparisons(post["content"]),
                    engagement_metrics=post["engagement"],
                    extracted_insights={}
                )
                mentions.append(mention)
        
        return mentions
    
    def _analyze_sentiment(self, text: str) -> Tuple[float, SentimentCategory]:
        """Analyze sentiment of text using VADER and TextBlob with relevance filtering"""
        # Check if text is relevant and not spam/joke
        if self._is_joke_or_spam(text):
            # Return neutral sentiment for spam/jokes
            return 0.0, SentimentCategory.NEUTRAL
        
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob sentiment
        try:
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
        except:
            textblob_polarity = 0.0
        
        # Combine scores with medical context weighting
        combined_score = self._apply_medical_context_weighting(
            vader_compound, textblob_polarity, text
        )
        
        # Categorize
        if combined_score >= 0.5:
            category = SentimentCategory.VERY_POSITIVE
        elif combined_score >= 0.1:
            category = SentimentCategory.POSITIVE
        elif combined_score >= -0.1:
            category = SentimentCategory.NEUTRAL
        elif combined_score >= -0.5:
            category = SentimentCategory.NEGATIVE
        else:
            category = SentimentCategory.VERY_NEGATIVE
        
        return combined_score, category
    
    def _is_joke_or_spam(self, text: str) -> bool:
        """Detect joke posts, spam, or irrelevant content"""
        text_lower = text.lower()
        
        # Joke indicators
        joke_patterns = [
            r'\blol\b', r'\blmao\b', r'\brofl\b', r'\blmfao\b',
            r'😂{3,}',  # Three or more laughing emojis
            r'jk\b', r'just kidding', r'joke\b',
            r'trust me bro', r'source: trust me',
            r'big pharma', r'illuminati', r'conspiracy',
            r'moon', r'lambo', r'diamond hands', r'hodl',  # Crypto/meme stock language
            r'yolo', r'wsb', r'tendies'
        ]
        
        for pattern in joke_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Spam patterns
        spam_patterns = [
            r'click here', r'buy now', r'limited time',
            r'viagra', r'cialis', r'casino', r'bitcoin',
            r'weight loss', r'miracle cure', r'doctors hate',
            r'one weird trick', r'hot singles'
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Too many emojis (likely not serious)
        emoji_count = len(re.findall(r'[😀-🙏]', text))
        if emoji_count > 5:
            return True
        
        # All caps (likely ranting/not serious)
        if len(text) > 20 and text.isupper():
            return True
        
        return False
    
    def _apply_medical_context_weighting(self, vader_score: float, 
                                       textblob_score: float, text: str) -> float:
        """Apply medical context weighting to sentiment scores"""
        # Start with average
        base_score = (vader_score + textblob_score) / 2
        
        text_lower = text.lower()
        
        # Boost positive sentiment for medical improvements
        positive_medical_terms = [
            'remission', 'cleared', 'cured', 'life-changing', 'life changing',
            'pain free', 'pain-free', 'symptom free', 'no side effects',
            'working great', 'finally works', 'miracle drug', 'saved my life'
        ]
        
        for term in positive_medical_terms:
            if term in text_lower:
                base_score = min(base_score + 0.2, 1.0)
                break
        
        # Boost negative sentiment for serious issues
        negative_medical_terms = [
            'hospitalized', 'emergency', 'allergic reaction', 'liver damage',
            'kidney failure', 'stopped working', 'doesnt work', "doesn't work",
            'made it worse', 'severe side effects', 'life threatening'
        ]
        
        for term in negative_medical_terms:
            if term in text_lower:
                base_score = max(base_score - 0.2, -1.0)
                break
        
        # Moderate adjustment for cost concerns
        if any(term in text_lower for term in ['expensive', 'cant afford', "can't afford", 'insurance denied']):
            base_score = max(base_score - 0.1, -1.0)
        
        return base_score
    
    def _classify_post_type(self, text: str) -> PostType:
        """Classify the type of post"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['side effect', 'reaction', 'rash', 'nausea']):
            return PostType.SIDE_EFFECT_REPORT
        elif any(term in text_lower for term in ['working', 'helped', 'improved', 'effective']):
            return PostType.EFFICACY_DISCUSSION
        elif any(term in text_lower for term in ['cost', 'insurance', 'price', 'afford']):
            return PostType.COST_CONCERN
        elif any(term in text_lower for term in ['compared to', 'vs', 'switched']):
            return PostType.COMPARISON
        elif '?' in text:
            return PostType.QUESTION
        elif any(term in text_lower for term in ['study', 'trial', 'fda', 'approval']):
            return PostType.NEWS_SHARING
        elif any(term in text_lower for term in ['experience', 'journey', 'story']):
            return PostType.PATIENT_EXPERIENCE
        else:
            return PostType.GENERAL
    
    def _extract_side_effects(self, text: str) -> List[str]:
        """Extract mentioned side effects"""
        found_effects = []
        text_lower = text.lower()
        
        for effect in self.medical_terms['side_effects']:
            if effect in text_lower:
                found_effects.append(effect)
        
        return found_effects
    
    def _check_efficacy_mention(self, text: str) -> bool:
        """Check if efficacy is mentioned"""
        text_lower = text.lower()
        return any(term in text_lower for term in self.medical_terms['efficacy_terms'])
    
    def _extract_drug_comparisons(self, text: str) -> List[str]:
        """Extract other drugs mentioned for comparison"""
        # This would use NER to find other drug names
        # For now, simple pattern matching
        comparison_drugs = []
        
        # Look for common drugs
        common_drugs = ["humira", "enbrel", "remicade", "stelara", "cosentyx", "taltz"]
        text_lower = text.lower()
        
        for drug in common_drugs:
            if drug in text_lower and drug not in comparison_drugs:
                comparison_drugs.append(drug.capitalize())
        
        return comparison_drugs
    
    def _aggregate_sentiment_analysis(self, mentions: List[DrugMention], 
                                    drug_name: str, company: str, ticker: str) -> Dict:
        """Aggregate all mentions into comprehensive analysis"""
        if not mentions:
            return {
                "drug_name": drug_name,
                "company": company,
                "ticker": ticker,
                "error": "No mentions found",
                "total_mentions": 0
            }
        
        # Calculate aggregate metrics
        sentiments = [m.sentiment_score for m in mentions]
        avg_sentiment = np.mean(sentiments)
        
        # Count by category
        category_counts = Counter(m.sentiment_category for m in mentions)
        
        # Platform breakdown
        platform_counts = Counter(m.platform for m in mentions)
        
        # Extract all side effects
        all_side_effects = []
        for m in mentions:
            all_side_effects.extend(m.side_effects_mentioned)
        side_effect_counts = Counter(all_side_effects)
        
        # Post type breakdown - use string values for Counter
        post_type_counts = Counter(m.post_type.value for m in mentions)
        
        # Efficacy mentions
        efficacy_positive = sum(1 for m in mentions 
                              if m.efficacy_mentioned and m.sentiment_category in 
                              [SentimentCategory.POSITIVE, SentimentCategory.VERY_POSITIVE])
        
        # Extract key insights
        positive_mentions = [m for m in mentions 
                           if m.sentiment_category in [SentimentCategory.POSITIVE, 
                                                      SentimentCategory.VERY_POSITIVE]]
        negative_mentions = [m for m in mentions 
                           if m.sentiment_category in [SentimentCategory.NEGATIVE, 
                                                      SentimentCategory.VERY_NEGATIVE]]
        
        # Get top concerns and positives
        concerns = self._extract_concerns(negative_mentions)
        positives = self._extract_positives(positive_mentions)
        
        # Investment signals
        investment_signal = self._generate_investment_signal(
            avg_sentiment, category_counts, side_effect_counts, efficacy_positive, len(mentions)
        )
        
        return {
            "drug_name": drug_name,
            "company": company,
            "ticker": ticker,
            "analysis_date": datetime.now().isoformat(),
            "total_mentions": len(mentions),
            "platforms_analyzed": dict(platform_counts),
            "average_sentiment": round(avg_sentiment, 3),
            "sentiment_distribution": {
                "very_positive": category_counts.get(SentimentCategory.VERY_POSITIVE, 0),
                "positive": category_counts.get(SentimentCategory.POSITIVE, 0),
                "neutral": category_counts.get(SentimentCategory.NEUTRAL, 0),
                "negative": category_counts.get(SentimentCategory.NEGATIVE, 0),
                "very_negative": category_counts.get(SentimentCategory.VERY_NEGATIVE, 0)
            },
            "post_types": dict(post_type_counts),
            "top_side_effects": dict(side_effect_counts.most_common(10)),
            "efficacy_sentiment": {
                "positive_mentions": efficacy_positive,
                "total_efficacy_mentions": sum(1 for m in mentions if m.efficacy_mentioned),
                "percentage_positive": round(efficacy_positive / len(mentions) * 100, 1)
            },
            "top_concerns": concerns[:5],
            "top_positives": positives[:5],
            "sample_positive_posts": [
                {
                    "platform": m.platform,
                    "content": m.content[:200] + "...",
                    "engagement": m.engagement_metrics
                } for m in positive_mentions[:3]
            ],
            "sample_negative_posts": [
                {
                    "platform": m.platform,
                    "content": m.content[:200] + "...",
                    "engagement": m.engagement_metrics
                } for m in negative_mentions[:3]
            ],
            "investment_signal": investment_signal
        }
    
    def _extract_concerns(self, negative_mentions: List[DrugMention]) -> List[str]:
        """Extract main concerns from negative posts"""
        concerns = []
        
        for mention in negative_mentions:
            if mention.side_effects_mentioned:
                concerns.extend([f"Side effect: {effect}" for effect in mention.side_effects_mentioned])
            
            # Look for specific concern patterns
            text_lower = mention.content.lower()
            if "doesn't work" in text_lower or "stopped working" in text_lower:
                concerns.append("Efficacy concerns")
            if "insurance" in text_lower or "cost" in text_lower or "expensive" in text_lower:
                concerns.append("Cost/insurance issues")
            if "worse" in text_lower or "horrible" in text_lower:
                concerns.append("Severe negative experience")
        
        return list(set(concerns))
    
    def _extract_positives(self, positive_mentions: List[DrugMention]) -> List[str]:
        """Extract positive themes from posts"""
        positives = []
        
        for mention in positive_mentions:
            text_lower = mention.content.lower()
            
            if "life changing" in text_lower or "life-changing" in text_lower:
                positives.append("Life-changing results")
            if "finally" in text_lower and "work" in text_lower:
                positives.append("Effective where others failed")
            if "no side effects" in text_lower or "minimal side effects" in text_lower:
                positives.append("Well tolerated")
            if "improvement" in text_lower or "improved" in text_lower:
                positives.append("Significant improvement")
            if "remission" in text_lower:
                positives.append("Achieved remission")
        
        return list(set(positives))
    
    def _generate_investment_signal(self, avg_sentiment: float, 
                                  category_counts: Counter,
                                  side_effects: Counter,
                                  efficacy_positive: int,
                                  total_mentions: int) -> Dict:
        """Generate investment-relevant signals from sentiment data"""
        signal = {
            "overall_signal": "NEUTRAL",
            "confidence": "LOW",
            "key_factors": [],
            "risks": [],
            "opportunities": []
        }
        
        # Determine overall signal
        positive_ratio = (category_counts.get(SentimentCategory.VERY_POSITIVE, 0) + 
                         category_counts.get(SentimentCategory.POSITIVE, 0)) / total_mentions
        
        if avg_sentiment > 0.3 and positive_ratio > 0.6:
            signal["overall_signal"] = "POSITIVE"
            signal["opportunities"].append("Strong positive patient sentiment")
        elif avg_sentiment < -0.3 and positive_ratio < 0.3:
            signal["overall_signal"] = "NEGATIVE"
            signal["risks"].append("Significant negative patient feedback")
        
        # Confidence based on mention volume
        if total_mentions > 50:
            signal["confidence"] = "HIGH"
        elif total_mentions > 20:
            signal["confidence"] = "MEDIUM"
        
        # Key factors
        if efficacy_positive / total_mentions > 0.5:
            signal["key_factors"].append("High efficacy satisfaction")
        
        if len(side_effects) > 0 and max(side_effects.values()) / total_mentions > 0.3:
            signal["risks"].append("Frequent side effect complaints")
        
        # Cost concerns
        cost_mentions = sum(1 for m in category_counts 
                          if m == PostType.COST_CONCERN)
        if cost_mentions / total_mentions > 0.2:
            signal["risks"].append("Significant cost/access concerns")
        
        return signal
    
    def _save_mentions(self, mentions: List[DrugMention]):
        """Save mentions to database"""
        conn = sqlite3.connect(self.sentiment_db)
        cursor = conn.cursor()
        
        for mention in mentions:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO drug_mentions
                    (mention_id, platform, drug_name, company, ticker, post_id,
                     post_url, post_date, author, content, sentiment_score,
                     sentiment_category, post_type, side_effects, efficacy_mentioned,
                     comparison_drugs, engagement_metrics, extracted_insights)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mention.mention_id, mention.platform, mention.drug_name,
                    mention.company, mention.ticker, mention.post_id,
                    mention.post_url, mention.post_date, mention.author,
                    mention.content, mention.sentiment_score,
                    mention.sentiment_category.value, mention.post_type.value,
                    json.dumps(mention.side_effects_mentioned),
                    mention.efficacy_mentioned,
                    json.dumps(mention.comparison_drugs),
                    json.dumps(mention.engagement_metrics),
                    json.dumps(mention.extracted_insights)
                ))
            except Exception as e:
                logger.error(f"Error saving mention: {e}")
        
        conn.commit()
        conn.close()
    
    def _update_summary(self, drug_name: str, ticker: str, analysis: Dict):
        """Update summary statistics in database"""
        if "error" in analysis:
            return
            
        conn = sqlite3.connect(self.sentiment_db)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        for platform, count in analysis["platforms_analyzed"].items():
            cursor.execute("""
                INSERT OR REPLACE INTO sentiment_summary
                (drug_name, ticker, platform, date, total_mentions, avg_sentiment,
                 positive_count, negative_count, neutral_count, top_side_effects, top_topics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                drug_name, ticker, platform, today, count,
                analysis["average_sentiment"],
                analysis["sentiment_distribution"]["positive"] + 
                analysis["sentiment_distribution"]["very_positive"],
                analysis["sentiment_distribution"]["negative"] + 
                analysis["sentiment_distribution"]["very_negative"],
                analysis["sentiment_distribution"]["neutral"],
                json.dumps(list(analysis["top_side_effects"].keys())[:5]),
                json.dumps(analysis["top_concerns"][:5] + analysis["top_positives"][:5])
            ))
        
        conn.commit()
        conn.close()
    
    def _is_post_relevant_to_drug(self, content: str, drug_name: str) -> bool:
        """Enhanced filtering to ensure posts are actually about the drug"""
        content_lower = content.lower()
        drug_lower = drug_name.lower()
        
        # Must contain the drug name
        if drug_lower not in content_lower:
            return False
        
        # Filter out spam/promotional content
        spam_keywords = [
            'buy now', 'click here', 'discount', 'sale', 'promo code',
            'affiliate', 'sponsored', 'ad', 'advertisement',
            'crypto', 'bitcoin', 'nft', 'trading', 'investment opportunity',
            'follow for follow', 'dm me', 'check bio', 'link in bio',
            '$$$', 'easy money', 'get rich', 'work from home'
        ]
        
        for keyword in spam_keywords:
            if keyword in content_lower:
                return False
        
        # Look for medical/health context indicators
        medical_context = [
            # Treatment experience
            'taking', 'prescribed', 'doctor', 'physician', 'nurse',
            'treatment', 'therapy', 'medication', 'medicine', 'drug',
            
            # Medical terms
            'side effect', 'adverse', 'reaction', 'dosage', 'dose',
            'mg', 'ml', 'injection', 'pill', 'tablet', 'capsule',
            'daily', 'weekly', 'monthly', 'twice a day', 'once a day',
            
            # Patient experience
            'patient', 'symptoms', 'condition', 'diagnosis', 'disease',
            'illness', 'health', 'medical', 'clinical', 'hospital',
            'clinic', 'appointment', 'visit', 'consultation',
            
            # Treatment outcomes
            'working', 'effective', 'helped', 'improved', 'better',
            'worse', 'no change', 'stopped working', 'response',
            'remission', 'flare', 'relapse', 'progression',
            
            # FDA/Regulatory
            'fda', 'approval', 'clinical trial', 'study', 'research',
            'phase', 'efficacy', 'safety', 'label', 'indication'
        ]
        
        # Check for medical context
        medical_score = sum(1 for term in medical_context if term in content_lower)
        
        # Require at least 1 medical context term, or longer posts (likely more context)
        return medical_score >= 1 or len(content.split()) >= 15
    
    def _extract_drug_context(self, content: str, drug_name: str) -> Dict[str, any]:
        """Extract additional context about how the drug is mentioned"""
        content_lower = content.lower()
        drug_lower = drug_name.lower()
        
        context = {
            'mention_type': 'general',
            'treatment_phase': None,
            'outcome_mentioned': False,
            'side_effects_context': False,
            'comparison_context': False
        }
        
        # Determine mention type
        if any(term in content_lower for term in ['starting', 'began', 'first dose', 'day 1']):
            context['mention_type'] = 'treatment_start'
        elif any(term in content_lower for term in ['stopping', 'discontinued', 'quit', 'switched']):
            context['mention_type'] = 'treatment_end'
        elif any(term in content_lower for term in ['week', 'month', 'year', 'day']):
            context['mention_type'] = 'ongoing_treatment'
        
        # Look for treatment outcomes
        positive_outcomes = ['better', 'improved', 'working', 'effective', 'helped', 'great', 'amazing']
        negative_outcomes = ['worse', 'not working', 'failed', 'terrible', 'awful', 'side effects']
        
        if any(term in content_lower for term in positive_outcomes):
            context['outcome_mentioned'] = 'positive'
        elif any(term in content_lower for term in negative_outcomes):
            context['outcome_mentioned'] = 'negative'
        
        # Check for side effects discussion
        side_effect_terms = ['side effect', 'adverse', 'reaction', 'nausea', 'headache', 'fatigue']
        context['side_effects_context'] = any(term in content_lower for term in side_effect_terms)
        
        # Check for drug comparisons
        comparison_terms = ['versus', 'vs', 'compared to', 'instead of', 'switched from', 'better than']
        context['comparison_context'] = any(term in content_lower for term in comparison_terms)
        
        return context


# Test function
async def test_sentiment_analyzer():
    """Test the sentiment analyzer with a drug"""
    analyzer = SocialMediaSentimentAnalyzer()
    
    # Test with Moderna's COVID vaccine
    print("Testing sentiment analysis for Spikevax (Moderna COVID vaccine)...")
    results = await analyzer.analyze_drug_sentiment("Spikevax")
    
    print(f"\nResults: {json.dumps(results, indent=2)}")
    
    # Test company analysis
    print("\n\nTesting company-wide sentiment for MRNA...")
    company_results = await analyzer.analyze_company_drugs("MRNA")
    
    print(f"\nCompany Results Summary:")
    print(f"Overall Sentiment: {company_results.get('overall_sentiment', 'N/A')}")
    print(f"Drugs Analyzed: {company_results.get('drugs_analyzed', 0)}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_sentiment_analyzer()) 