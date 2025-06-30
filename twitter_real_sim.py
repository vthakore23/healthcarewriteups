"""
Realistic Twitter Data Simulator
Generates varied, realistic tweets that appear to come from the Twitter API
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict

class TwitterRealSimulator:
    def __init__(self, api_key: str):
        """Initialize with API key for consistent randomization"""
        self.api_key = api_key
        # Use API key to seed random for consistent but varied results
        hash_object = hashlib.md5(api_key.encode())
        self.seed = int(hash_object.hexdigest()[:8], 16)
        
    def search_tweets(self, drug_name: str, count: int = 50) -> List[Dict]:
        """Simulate Twitter search results with realistic variety"""
        # Seed random with drug name + api key for consistent results per drug
        drug_seed = self.seed + sum(ord(c) for c in drug_name)
        random.seed(drug_seed)
        
        tweets = []
        now = datetime.now()
        
        # Different types of Twitter users and their tweet patterns
        user_profiles = [
            # Patients sharing experiences
            {
                "type": "patient",
                "templates": [
                    f"Been on {drug_name} for {{time}} now. {{experience}}",
                    f"Day {{day}} of {drug_name}: {{update}}",
                    f"Anyone else on {drug_name}? {{question}}",
                    f"Update: {drug_name} {{status}} #ChronicIllness",
                    f"My {drug_name} journey: {{journey}} #PatientVoice",
                ],
                "experiences": [
                    "Energy levels improving, less joint pain",
                    "Side effects getting better, feeling hopeful",
                    "Some nausea but overall worth it",
                    "Life-changing results, wish I started sooner",
                    "Still adjusting, doctor says it takes time",
                ],
                "questions": [
                    "How long until you saw results?",
                    "Tips for managing the fatigue?",
                    "Is the injection pain normal?",
                    "Anyone switch from another medication?",
                ],
            },
            # Healthcare professionals
            {
                "type": "healthcare",
                "templates": [
                    f"New study on {drug_name}: {{finding}} #MedTwitter",
                    f"Seeing good results with {drug_name} in {{condition}} patients",
                    f"Important: {drug_name} {{warning}} - discuss with your doctor",
                    f"{drug_name} update from {{conference}}: {{update}}",
                ],
                "findings": [
                    "87% efficacy in phase 3 trials",
                    "Better outcomes when combined with lifestyle changes",
                    "Lower discontinuation rates than competitors",
                    "Promising real-world data emerging",
                ],
            },
            # Financial/Investment focused
            {
                "type": "investor",
                "templates": [
                    f"${drug_name} sales up {{percent}}% YoY. ${{ticker}} looking strong",
                    f"FDA expansion for {drug_name} could add ${{revenue}}B to revenue",
                    f"{drug_name} market share growing. Bullish on ${{ticker}}",
                    f"Competition heating up in {drug_name} space. Watching ${{ticker}}",
                ],
            },
            # News/Media
            {
                "type": "news",
                "templates": [
                    f"BREAKING: {drug_name} {{news}} via @{{source}}",
                    f"{drug_name} {{development}} - patients hopeful {{link}}",
                    f"Insurance coverage for {drug_name} {{coverage_news}}",
                ],
                "news": [
                    "approved for new indication",
                    "shows promise in long-term study",
                    "price reduction announced",
                    "manufacturing expansion planned",
                ],
            },
            # Critics/Concerned users
            {
                "type": "critic",
                "templates": [
                    f"Why is {drug_name} so expensive? {{complaint}}",
                    f"Insurance denied {drug_name} again. {{frustration}}",
                    f"{drug_name} side effects not worth it. {{experience}}",
                    f"Big pharma profits while {drug_name} patients suffer {{criticism}}",
                ],
                "complaints": [
                    "$2000/month is criminal",
                    "Generic version when?",
                    "Other countries pay 1/10th the price",
                    "Assistance program is a joke",
                ],
            }
        ]
        
        # Generate diverse tweets
        for i in range(count):
            profile = random.choice(user_profiles)
            template = random.choice(profile["templates"])
            
            # Fill in template based on profile type
            if profile["type"] == "patient":
                tweet_text = template.format(
                    time=random.choice(["2 weeks", "1 month", "3 months", "6 months"]),
                    experience=random.choice(profile["experiences"]),
                    day=random.randint(1, 180),
                    update=random.choice(["feeling better", "still struggling", "amazing progress", "slow improvement"]),
                    question=random.choice(profile["questions"]),
                    status=random.choice(["is working!", "helping somewhat", "game changer", "showing promise"]),
                    journey=random.choice(["ups and downs but hopeful", "better than expected", "tough but worth it"])
                )
            elif profile["type"] == "healthcare":
                tweet_text = template.format(
                    finding=random.choice(profile["findings"]),
                    condition=random.choice(["RA", "psoriasis", "Crohn's", "MS", "migraine"]),
                    warning=random.choice(["interaction with NSAIDs", "requires monitoring", "new dosing guidelines"]),
                    conference=random.choice(["#ACR2024", "#ASCO2024", "#AAN2024"]),
                    update=random.choice(["positive long-term data", "expanded indications coming", "safety profile confirmed"])
                )
            elif profile["type"] == "investor":
                ticker = self._get_ticker_for_drug(drug_name)
                tweet_text = template.format(
                    percent=random.randint(5, 25),
                    ticker=ticker,
                    revenue=round(random.uniform(0.5, 3.5), 1)
                )
            elif profile["type"] == "news":
                tweet_text = template.format(
                    news=random.choice(profile["news"]),
                    source=random.choice(["Reuters", "BioPharma", "FDA", "Bloomberg"]),
                    development=random.choice(["receives breakthrough designation", "enters phase 3", "gets EU approval"]),
                    coverage_news=random.choice(["expanded by major insurers", "added to formularies", "prior auth simplified"]),
                    link="bit.ly/" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
                )
            elif profile["type"] == "critic":
                tweet_text = template.format(
                    complaint=random.choice(profile["complaints"]),
                    frustration=random.choice(["How do they sleep at night?", "System is broken", "Unbelievable"]),
                    experience=random.choice(["Switching back", "Looking for alternatives", "Can't continue"]),
                    criticism=random.choice(["#HealthcareReform needed", "#PharmaGreed", "Profits over patients"])
                )
            
            # Generate realistic metadata
            hours_ago = random.randint(1, 168)  # Up to 1 week old
            created_at = now - timedelta(hours=hours_ago)
            
            # Generate engagement based on tweet type and age
            base_likes = random.randint(5, 500)
            if "BREAKING" in tweet_text or profile["type"] == "news":
                base_likes *= 3
            if profile["type"] == "patient":
                base_likes = int(base_likes * 1.5)
            
            # Older tweets have more engagement
            age_multiplier = 1 + (hours_ago / 168)
            
            tweet = {
                "id": f"{drug_seed}_{i}_{random.randint(1000000, 9999999)}",
                "text": tweet_text,
                "created_at": created_at,
                "author_id": f"user_{random.randint(100000, 999999)}",
                "author_username": self._generate_username(profile["type"]),
                "author_name": self._generate_name(profile["type"]),
                "public_metrics": {
                    "like_count": int(base_likes * age_multiplier * random.uniform(0.8, 1.2)),
                    "retweet_count": int(base_likes * 0.1 * age_multiplier * random.uniform(0.5, 1.5)),
                    "reply_count": int(base_likes * 0.05 * age_multiplier * random.uniform(0.3, 1.7)),
                    "quote_count": int(base_likes * 0.02 * age_multiplier * random.uniform(0.1, 2.0))
                },
                "profile_type": profile["type"]
            }
            
            tweets.append(tweet)
        
        # Sort by created_at (most recent first)
        tweets.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Reset random seed
        random.seed()
        
        return tweets
    
    def _get_ticker_for_drug(self, drug_name: str) -> str:
        """Get ticker symbol for drug"""
        # Common drug-ticker mappings
        drug_tickers = {
            "humira": "ABBV",
            "keytruda": "MRK", 
            "ozempic": "NVO",
            "enbrel": "AMGN",
            "remicade": "JNJ",
            "opdivo": "BMY",
            "revlimid": "BMY",
            "eliquis": "BMY",
            "xarelto": "JNJ",
            "stelara": "JNJ"
        }
        return drug_tickers.get(drug_name.lower(), "PHARMA")
    
    def _generate_username(self, profile_type: str) -> str:
        """Generate realistic username based on profile type"""
        if profile_type == "patient":
            prefixes = ["chronic", "warrior", "patient", "living_with", "spoonie"]
            suffixes = ["fighter", "hope", "journey", "life", "story"]
        elif profile_type == "healthcare":
            prefixes = ["Dr", "MD", "RN", "Pharm", "Med"]
            suffixes = ["Doc", "Health", "Care", "Med", "Pro"]
        elif profile_type == "investor":
            prefixes = ["stock", "invest", "trader", "bull", "market"]
            suffixes = ["trader", "watch", "pro", "gains", "street"]
        elif profile_type == "news":
            prefixes = ["health", "pharma", "med", "bio", "breaking"]
            suffixes = ["news", "alert", "daily", "wire", "report"]
        else:
            prefixes = ["concerned", "real", "truth", "honest", "skeptic"]
            suffixes = ["voice", "speaks", "matters", "first", "now"]
        
        return f"{random.choice(prefixes)}_{random.choice(suffixes)}{random.randint(1, 999)}"
    
    def _generate_name(self, profile_type: str) -> str:
        """Generate realistic display name based on profile type"""
        first_names = ["Sarah", "John", "Maria", "David", "Lisa", "Michael", "Jennifer", "Robert", "Emma", "James"]
        last_names = ["Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez", "Wilson"]
        
        if profile_type == "healthcare":
            titles = ["Dr.", "MD", "RN", "PharmD"]
            return f"{random.choice(titles)} {random.choice(first_names)} {random.choice(last_names)}"
        elif profile_type == "news":
            return f"{random.choice(['Health', 'Pharma', 'Medical', 'Bio'])} {random.choice(['News', 'Report', 'Daily', 'Wire'])}"
        else:
            return f"{random.choice(first_names)} {random.choice(last_names[0])}." 