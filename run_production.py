#!/usr/bin/env python3
"""
Production script for Healthcare News Automation
Runs exactly as Chris specified in his requirements
"""
import sys
import os
from datetime import datetime
import logging

# Setup logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('healthcare_news.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Run the daily healthcare news analysis:
    1. Check lifesciencereport.com/newsroom for new articles
    2. Generate 600-word summaries for each article
    3. Select 1-2 most interesting events for additional analysis
    4. Email results to the specified recipients
    """
    
    print("=" * 60)
    print("🏥 HEALTHCARE NEWS AUTOMATION - PRODUCTION MODE")
    print("   Daily Analysis for Healthcare Team")
    print("=" * 60)
    
    try:
        # Import here to ensure all dependencies are available
        from main_optimized import OptimizedHealthcareNewsAutomation
        
        # Initialize the automation system
        logger.info("Initializing Healthcare News Automation for daily analysis...")
        automation = OptimizedHealthcareNewsAutomation()
        
        # Run the complete daily workflow:
        # - Scrape today's articles from lifesciencereport.com/newsroom
        # - Generate structured summaries (600 words each)
        # - Select interesting articles for additional analysis
        # - Email to Chris & Jim
        logger.info("Starting daily news analysis workflow...")
        automation.run_daily_task(send_email=True)
        
        logger.info("✅ Daily healthcare news analysis completed successfully!")
        print("\n🎉 Analysis complete! Reports generated and ready for download.")
        
    except Exception as e:
        logger.error(f"❌ Error in daily analysis: {e}", exc_info=True)
        print(f"\n💥 Error occurred: {e}")
        print("Check healthcare_news.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 