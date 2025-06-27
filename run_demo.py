#!/usr/bin/env python3
"""
Demo script to run the automation with limited articles for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import HealthcareNewsAutomation
import logging

# Configure logging to show progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Monkey patch the scraper to limit articles
def limited_get_todays_articles(self):
    """Get only first 3 articles for demo"""
    logger.info("Demo mode: Fetching only 3 articles...")
    original_method = type(self)._original_get_todays_articles
    all_articles = original_method(self)
    
    # Return only first 3 articles
    if len(all_articles) > 3:
        logger.info(f"Found {len(all_articles)} articles, limiting to 3 for demo")
        return all_articles[:3]
    return all_articles

if __name__ == "__main__":
    logger.info("Starting Healthcare News Automation Demo...")
    
    automation = HealthcareNewsAutomation()
    
    # Store original method and patch it
    automation.scraper._original_get_todays_articles = automation.scraper.get_todays_articles
    automation.scraper.get_todays_articles = limited_get_todays_articles.__get__(automation.scraper)
    
    # Run the task
    automation.run_daily_task(send_email=False)
    
    logger.info("\nDemo complete! Check the reports/ folder for the generated HTML report.") 