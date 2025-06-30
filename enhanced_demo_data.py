"""
Enhanced Demo Data Generator for Social Media Sentiment Analysis
Generates realistic, varied social media posts for different drugs
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict
import hashlib

class EnhancedDemoDataGenerator:
    def __init__(self):
        # Drug-specific post templates
        self.drug_templates = {
            "humira": {
                "positive": [
                    "Been on Humira for 3 months now. Psoriasis is 90% cleared! The injections aren't bad at all.",
                    "Humira gave me my life back. From wheelchair to hiking trails in 6 months. #RAWarrior",
                    "Insurance finally approved Humira! Starting next week. Fingers crossed 🤞",
                    "Year 2 on Humira - still in remission. Some fatigue but manageable. Worth it!",
                    "Just did my Humira injection. Pro tip: let it warm to room temp first, hurts way less!"
                ],
                "negative": [
                    "Humira worked great for 2 years then stopped. Now trying Enbrel. So frustrated.",
                    "The injection site reactions from Humira are getting worse. Red welts for days.",
                    "Can't afford Humira anymore. $5k/month even with insurance. What are my options?",
                    "Humira suppressed my immune system too much. Constant infections. Had to stop.",
                    "Anyone else get terrible headaches on Humira? Day 3 after injection is brutal."
                ],
                "neutral": [
                    "Starting Humira next month. What should I expect? Any tips?",
                    "Does anyone take Humira for UC instead of Crohn's? How's it working?",
                    "Humira citrate-free vs regular - is there really a difference in pain?",
                    "How long did Humira take to work for you? Week 4 and not seeing much change.",
                    "Traveling with Humira - how do you keep it cold? Flying to Europe next month."
                ]
            },
            "keytruda": {
                "positive": [
                    "Keytruda shrunk my tumors by 70%! Scans show incredible progress. #CancerWarrior",
                    "6 months on Keytruda - cancer stable, side effects minimal. Living my life!",
                    "My oncologist called Keytruda a game-changer for my type of cancer. Feeling hopeful.",
                    "Keytruda infusion #12 done. Energy returning, appetite back. Beating the odds!",
                    "Melanoma GONE after Keytruda treatment! 2 years cancer-free! Never give up hope!"
                ],
                "negative": [
                    "Keytruda gave me severe colitis. In hospital for a week. Treatment on hold.",
                    "The fatigue from Keytruda is unreal. Can barely get out of bed some days.",
                    "Keytruda caused thyroid issues. Now on lifetime hormone replacement. Trade-offs...",
                    "Insurance denied Keytruda. $12k per infusion. How is this legal?",
                    "Keytruda stopped working after 8 months. Tumor growing again. Devastated."
                ],
                "neutral": [
                    "First Keytruda infusion tomorrow. What side effects did you experience?",
                    "How often do you get Keytruda infusions? Every 3 weeks seems frequent.",
                    "Anyone combine Keytruda with chemo? My onc is suggesting it.",
                    "Keytruda vs Opdivo - anyone tried both? Which worked better?",
                    "Getting Keytruda for lung cancer. Success stories appreciated 🙏"
                ]
            },
            "ozempic": {
                "positive": [
                    "Down 45 lbs on Ozempic! A1C from 9.2 to 5.8. This drug is life-changing!",
                    "Ozempic killed my food noise. First time in years I'm not constantly hungry.",
                    "6 months on Ozempic: lost weight, blood sugar perfect, feel amazing!",
                    "Ozempic helped me avoid insulin. So grateful. The nausea passed after week 3.",
                    "My diabetes is finally under control with Ozempic. Energy through the roof!"
                ],
                "negative": [
                    "Ozempic nausea is unbearable. Can't keep anything down. Losing too much weight.",
                    "Severe constipation from Ozempic. Nothing helps. Considering stopping.",
                    "Ozempic shortage again! Pharmacy has no idea when it'll be back. So frustrated.",
                    "The sulfur burps from Ozempic are disgusting. Anyone find a solution?",
                    "Gained all the weight back after stopping Ozempic. Feel like a failure."
                ],
                "neutral": [
                    "Just prescribed Ozempic. Do you inject in stomach or thigh? Which is better?",
                    "How long does Ozempic pen last in fridge? Instructions are confusing.",
                    "Ozempic vs Mounjaro for weight loss? Insurance covers both.",
                    "When do Ozempic side effects typically improve? Week 2 is rough.",
                    "Can you drink alcohol on Ozempic? Have a wedding next month."
                ]
            },
            "enbrel": {
                "positive": [
                    "Enbrel cleared my psoriasis in 8 weeks! 15 years of suffering - finally relief!",
                    "RA pain gone thanks to Enbrel. Can play with grandkids again. Worth every penny.",
                    "3 years on Enbrel - still working great. No major infections. Lucky!",
                    "Switched from Humira to Enbrel - way less injection pain. Happy I switched!",
                    "Enbrel + methotrexate combo = remission! First time pain-free in a decade."
                ],
                "negative": [
                    "Enbrel stopped working after 18 months. So disappointed. Now what?",
                    "Injection site reactions getting worse with Enbrel. Huge red patches.",
                    "Got shingles on Enbrel. Immune system too suppressed. Be careful!",
                    "Enbrel copay went from $50 to $500. Can't afford it anymore. Devastated.",
                    "Severe fatigue on Enbrel. Doctor says it's not the drug but I know my body."
                ]
            },
            "remicade": {
                "positive": [
                    "Remicade infusions gave me my life back! Crohn's in complete remission.",
                    "Just had infusion #50! Remicade still working after 6 years. So grateful.",
                    "Remicade stopped my joint damage. X-rays show no progression! #RAWarrior",
                    "The infusion center staff make Remicade days almost enjoyable. Great people!",
                    "Remicade worked when nothing else did. Fistulas finally healing!"
                ],
                "negative": [
                    "Allergic reaction to Remicade during infusion. Scary experience. Switching drugs.",
                    "Remicade causing liver issues. Enzymes elevated. May need to stop.",
                    "8 hour infusions are brutal. Remicade works but the time commitment is hard.",
                    "Insurance fighting every Remicade infusion. Constant prior auth battles.",
                    "Remicade antibodies developed. No longer working. Starting Stelara next."
                ]
            }
        }
        
        # Generic templates for drugs not specifically defined
        self.generic_templates = {
            "positive": [
                "This medication changed my life! Symptoms 80% better after 3 months.",
                "Finally found something that works. Side effects minimal. Feeling hopeful!",
                "6 months in - still working great. Quality of life so much better.",
                "Doctor was right about this drug. Wish I'd started sooner!",
                "The improvement has been gradual but steady. Definitely recommend trying it."
            ],
            "negative": [
                "Severe side effects forced me to stop. Looking for alternatives.",
                "Worked for a while then stopped. So frustrating when that happens.",
                "The cost is insane even with insurance. Healthcare system is broken.",
                "Too many side effects to list. Cure worse than disease in my case.",
                "3 months trial - no improvement. Moving on to next option."
            ],
            "neutral": [
                "Just started this medication. How long before you saw results?",
                "Anyone else taking this? Would love to hear your experience.",
                "Doctor recommended this but reviews are mixed. Thoughts?",
                "Day 10 on this drug. Some improvement but also new side effects.",
                "Comparing this to similar medications. Which worked best for you?"
            ]
        }
        
        # Platform-specific characteristics
        self.platform_styles = {
            "Twitter": {
                "max_length": 280,
                "hashtags": ["#ChronicIllness", "#Spoonie", "#PatientVoice", "#HealthcareTwitter"],
                "style": "concise"
            },
            "StockTwits": {
                "max_length": 1000,
                "tickers": True,
                "style": "investment-focused"
            },
            "PatientForum": {
                "max_length": 2000,
                "style": "detailed"
            }
        }
        
        # Side effects database
        self.side_effects = {
            "common": ["fatigue", "nausea", "headache", "dizziness", "insomnia"],
            "gi": ["diarrhea", "constipation", "stomach pain", "loss of appetite"],
            "skin": ["rash", "injection site reaction", "itching", "bruising"],
            "serious": ["infection", "liver problems", "blood disorders", "allergic reaction"]
        }
        
        # Joke/spam patterns to filter out
        self.spam_patterns = [
            "bitcoin", "crypto", "viagra", "casino", "win money",
            "click here", "limited time", "act now", "free trial"
        ]
        
    def generate_posts(self, drug_name: str, platform: str, count: int = 20) -> List[Dict]:
        """Generate realistic posts for a specific drug and platform"""
        posts = []
        drug_lower = drug_name.lower()
        
        # Get templates for this drug
        if drug_lower in self.drug_templates:
            templates = self.drug_templates[drug_lower]
        else:
            templates = self.generic_templates
        
        # Generate mix of positive, negative, and neutral posts
        sentiment_distribution = {
            "positive": int(count * 0.4),
            "negative": int(count * 0.3),
            "neutral": int(count * 0.3)
        }
        
        for sentiment, num_posts in sentiment_distribution.items():
            for i in range(num_posts):
                post = self._generate_single_post(
                    drug_name, platform, sentiment, templates.get(sentiment, [])
                )
                if post and not self._is_spam(post["content"]):
                    posts.append(post)
        
        # Add some investment-focused posts for StockTwits
        if platform == "StockTwits" and drug_lower in ["keytruda", "humira", "ozempic"]:
            posts.extend(self._generate_investment_posts(drug_name, 5))
        
        # Randomize order and timestamps
        random.shuffle(posts)
        posts = self._assign_realistic_timestamps(posts)
        
        return posts[:count]  # Return exactly the requested count
    
    def _generate_single_post(self, drug_name: str, platform: str, 
                             sentiment: str, templates: List[str]) -> Dict:
        """Generate a single post"""
        if not templates:
            return None
            
        # Select random template
        template = random.choice(templates)
        content = template.replace("{drug}", drug_name)
        
        # Add platform-specific elements
        if platform == "Twitter":
            content = self._add_twitter_elements(content)
        elif platform == "StockTwits":
            content = self._add_stocktwits_elements(content, drug_name)
        
        # Generate unique post ID
        post_id = hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:12]
        
        # Generate engagement metrics
        engagement = self._generate_engagement_metrics(sentiment, platform)
        
        return {
            "post_id": post_id,
            "platform": platform,
            "content": content,
            "sentiment": sentiment,
            "engagement": engagement,
            "author": self._generate_author(platform),
            "date": None  # Will be set by _assign_realistic_timestamps
        }
    
    def _add_twitter_elements(self, content: str) -> str:
        """Add Twitter-specific elements like hashtags"""
        if len(content) < 250 and random.random() > 0.5:
            hashtag = random.choice(self.platform_styles["Twitter"]["hashtags"])
            content += f" {hashtag}"
        return content[:280]  # Enforce Twitter length limit
    
    def _add_stocktwits_elements(self, content: str, drug_name: str) -> str:
        """Add StockTwits-specific elements"""
        tickers = {
            "humira": "$ABBV",
            "keytruda": "$MRK", 
            "ozempic": "$NVO",
            "enbrel": "$AMGN",
            "remicade": "$JNJ"
        }
        
        ticker = tickers.get(drug_name.lower(), "$PHARMA")
        if ticker not in content:
            content = f"{ticker} {content}"
        return content
    
    def _generate_investment_posts(self, drug_name: str, count: int) -> List[Dict]:
        """Generate investment-focused posts for StockTwits"""
        templates = [
            f"{{ticker}} Strong prescription growth for {drug_name}. Earnings beat likely.",
            f"{{ticker}} {drug_name} sales up 15% YoY. Bullish on continued growth.",
            f"Hearing good things about {drug_name} from doctors. {{ticker}} to the moon!",
            f"{{ticker}} {drug_name} patent cliff not until 2028. Lots of runway left.",
            f"Competition heating up for {drug_name}. {{ticker}} may see pressure."
        ]
        
        posts = []
        for i in range(count):
            template = random.choice(templates)
            content = self._add_stocktwits_elements(template, drug_name)
            
            posts.append({
                "post_id": hashlib.md5(f"{content}{i}".encode()).hexdigest()[:12],
                "platform": "StockTwits",
                "content": content,
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "engagement": self._generate_engagement_metrics("neutral", "StockTwits"),
                "author": f"trader_{random.randint(100, 999)}",
                "date": None
            })
        
        return posts
    
    def _generate_engagement_metrics(self, sentiment: str, platform: str) -> Dict:
        """Generate realistic engagement metrics based on sentiment and platform"""
        if platform == "Twitter":
            base_likes = random.randint(5, 200)
            if sentiment == "negative":
                base_likes = int(base_likes * 1.5)  # Negative posts often get more engagement
                
            return {
                "likes": base_likes,
                "retweets": random.randint(0, base_likes // 3),
                "replies": random.randint(1, base_likes // 5)
            }
            
        elif platform == "StockTwits":
            return {
                "likes": random.randint(2, 50),
                "reshares": random.randint(0, 10)
            }
            
        else:  # Patient forums
            return {
                "views": random.randint(50, 500),
                "replies": random.randint(2, 20),
                "helpful": random.randint(1, 15)
            }
    
    def _generate_author(self, platform: str) -> str:
        """Generate realistic author names for each platform"""
        if platform == "Twitter":
            prefixes = ["patient", "chronic", "health", "warrior", "fighter", "survivor"]
            return f"@{random.choice(prefixes)}_{random.randint(100, 9999)}"
        elif platform == "StockTwits":
            prefixes = ["trader", "investor", "bull", "bear", "bio"]
            return f"{random.choice(prefixes)}_{random.randint(100, 999)}"
        else:
            return f"PatientUser{random.randint(1000, 9999)}"
    
    def _assign_realistic_timestamps(self, posts: List[Dict]) -> List[Dict]:
        """Assign realistic timestamps to posts"""
        now = datetime.now()
        
        for i, post in enumerate(posts):
            # Distribute posts over the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            post["date"] = now - timedelta(
                days=days_ago, 
                hours=hours_ago, 
                minutes=minutes_ago
            )
        
        # Sort by date (most recent first)
        posts.sort(key=lambda x: x["date"], reverse=True)
        return posts
    
    def _is_spam(self, content: str) -> bool:
        """Filter out spam/joke posts"""
        content_lower = content.lower()
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if pattern in content_lower:
                return True
        
        # Check for joke patterns
        joke_patterns = [
            "lol", "lmao", "😂" * 3,  # Excessive laughing emojis
            "yolo", "moon", "lambo",  # Crypto/meme stock language
            "trust me bro"
        ]
        
        for pattern in joke_patterns:
            if pattern in content_lower:
                return True
        
        # Filter out posts that are too short or too generic
        if len(content) < 20:
            return True
            
        return False
    
    def filter_relevant_posts(self, posts: List[Dict], drug_name: str) -> List[Dict]:
        """Filter posts to ensure relevance to the drug"""
        relevant_posts = []
        drug_lower = drug_name.lower()
        
        for post in posts:
            content_lower = post["content"].lower()
            
            # Must mention the drug or a related term
            drug_related_terms = [
                drug_lower,
                drug_lower.replace(" ", ""),  # Handle spaces
                drug_lower[:5] if len(drug_lower) > 5 else drug_lower  # Partial matches
            ]
            
            if any(term in content_lower for term in drug_related_terms):
                relevant_posts.append(post)
        
        return relevant_posts

# Create global instance
demo_generator = EnhancedDemoDataGenerator() 