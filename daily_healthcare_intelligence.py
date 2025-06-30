#!/usr/bin/env python3
"""
Daily Healthcare Intelligence System
Analyzes healthcare/biotech news from lifesciencereport.com/newsroom
Generates investment-grade summaries and analysis for decision makers
"""
import sys
import os
import logging
from datetime import datetime, date
from typing import List, Dict, Tuple
import schedule
import time
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import LifeScienceScraper, NewsArticle
from ai_generator import AISummaryGenerator
from email_sender import EmailSender
from stock_ticker_intelligence import HealthcareCompanyIntelligence
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DailyHealthcareIntelligence:
    """Main orchestrator for daily healthcare news analysis"""
    
    def __init__(self):
        self.scraper = LifeScienceScraper()
        self.ai_generator = AISummaryGenerator()
        self.email_sender = EmailSender()
        self.stock_intel = HealthcareCompanyIntelligence()
        self.todays_report_file = None
        
    def run_daily_analysis(self):
        """Execute the complete daily analysis workflow"""
        logger.info("="*80)
        logger.info(f"🚀 Starting Daily Healthcare Intelligence Analysis - {datetime.now()}")
        logger.info("="*80)
        
        try:
            # Step 1: Scrape today's news
            logger.info("\n📰 Step 1: Checking lifesciencereport.com/newsroom for new articles...")
            articles = self.scraper.get_todays_articles()
            
            if not articles:
                logger.info("No new articles found today. Checking will resume at next scheduled time.")
                self._save_no_news_report()
                return
            
            logger.info(f"✅ Found {len(articles)} new articles to analyze")
            
            # Step 2: Generate summaries for all articles
            logger.info("\n📝 Step 2: Generating investment-grade summaries (~600 words each)...")
            summaries = self._generate_summaries(articles)
            logger.info(f"✅ Generated {len(summaries)} structured summaries")
            
            # Step 3: Select most interesting articles for deeper analysis
            logger.info("\n🔍 Step 3: Selecting 1-2 most interesting events for additional analysis...")
            selected_indices = self.ai_generator.select_interesting_articles(summaries)
            selected_articles = [summaries[i] for i in selected_indices]
            logger.info(f"✅ Selected {len(selected_articles)} articles for deeper analysis")
            
            # Step 4: Generate additional analysis for selected articles
            logger.info("\n💡 Step 4: Generating additional investment analysis...")
            analyses = self._generate_analyses(selected_articles)
            logger.info(f"✅ Completed {len(analyses)} in-depth analyses")
            
            # Step 5: Enhance with stock ticker intelligence if available
            logger.info("\n📊 Step 5: Enriching with real-time stock intelligence...")
            enhanced_summaries = self._enhance_with_stock_data(summaries)
            
            # Step 6: Save report locally
            logger.info("\n💾 Step 6: Saving comprehensive report...")
            report_path = self._save_report(enhanced_summaries, analyses)
            logger.info(f"✅ Report saved to: {report_path}")
            
            # Step 7: Report delivery
            logger.info("\n📧 Step 7: Finalizing report delivery...")
            if config.EMAIL_ENABLED and self._send_report(enhanced_summaries, analyses):
                logger.info("✅ Report successfully sent via email")
            else:
                logger.info("📁 Report saved locally only (email disabled)")
            
            # Step 8: Log completion
            self._log_completion(len(articles), len(selected_articles))
            
        except Exception as e:
            logger.error(f"❌ Error in daily analysis: {e}", exc_info=True)
            self._send_error_notification(str(e))
    
    def _generate_summaries(self, articles: List[NewsArticle]) -> List[Dict]:
        """Generate structured summaries for all articles"""
        summaries = []
        
        for i, article in enumerate(articles):
            logger.info(f"Generating summary {i+1}/{len(articles)}: {article.title}")
            
            try:
                summary_text = self.ai_generator.generate_summary(article)
                
                if summary_text:
                    summaries.append({
                        'title': article.title,
                        'url': article.url,
                        'summary': summary_text,
                        'company_name': article.company_name,
                        'published_date': article.published_date,
                        'article_id': article.article_id
                    })
                    
                    # Log word count for quality assurance
                    word_count = len(summary_text.split())
                    logger.info(f"✓ Summary generated: {word_count} words")
                else:
                    logger.warning(f"Failed to generate summary for: {article.title}")
                    
            except Exception as e:
                logger.error(f"Error generating summary for article {i+1}: {e}")
                continue
        
        return summaries
    
    def _generate_analyses(self, selected_articles: List[Dict]) -> List[Dict]:
        """Generate in-depth analysis for selected articles"""
        analyses = []
        
        for article in selected_articles:
            logger.info(f"Generating in-depth analysis for: {article['title']}")
            
            try:
                analysis_text = self.ai_generator.generate_analysis(
                    summary_text=article['summary'],
                    article_title=article['title'],
                    company_name=article.get('company_name', '')
                )
                
                if analysis_text:
                    analyses.append({
                        'title': article['title'],
                        'url': article['url'],
                        'company_name': article.get('company_name', ''),
                        'analysis': analysis_text,
                        'original_summary': article['summary']
                    })
                    
                    # Log analysis quality metrics
                    word_count = len(analysis_text.split())
                    has_citations = any(phrase in analysis_text for phrase in 
                                      ["According to", "Industry data", "Market research", "shows that"])
                    
                    logger.info(f"✓ Analysis generated: {word_count} words, "
                              f"Citations: {'Yes' if has_citations else 'No'}")
                else:
                    logger.warning(f"Failed to generate analysis for: {article['title']}")
                    
            except Exception as e:
                logger.error(f"Error generating analysis: {e}")
                continue
        
        return analyses
    
    def _enhance_with_stock_data(self, summaries: List[Dict]) -> List[Dict]:
        """Enhance summaries with real-time stock ticker intelligence"""
        enhanced = []
        
        for summary in summaries:
            enhanced_summary = summary.copy()
            
            # Extract ticker from company name if available
            company_name = summary.get('company_name', '')
            if company_name:
                # Try to extract ticker from company name (e.g., "Moderna (MRNA)")
                import re
                ticker_match = re.search(r'\(([A-Z]+)\)', company_name)
                
                if ticker_match:
                    ticker = ticker_match.group(1)
                    logger.info(f"Fetching stock intelligence for {ticker}...")
                    
                    try:
                        stock_data = self.stock_intel.get_company_intelligence(ticker)
                        
                        if "error" not in stock_data:
                            enhanced_summary['stock_intelligence'] = {
                                'current_price': stock_data.get('current_price'),
                                'market_cap': stock_data.get('market_cap'),
                                'financial_health': stock_data.get('financial_health'),
                                'fda_status': stock_data.get('fda_submissions'),
                                'management_credibility': stock_data.get('management_credibility', {}).get('company_credibility_score')
                            }
                            logger.info(f"✓ Enhanced with stock data for {ticker}")
                    except Exception as e:
                        logger.warning(f"Could not fetch stock data for {ticker}: {e}")
            
            enhanced.append(enhanced_summary)
        
        return enhanced
    
    def _save_report(self, summaries: List[Dict], analyses: List[Dict]) -> str:
        """Save the complete report to disk"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create report data structure
        report_data = {
            'report_date': date_str,
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(summaries),
            'selected_for_analysis': len(analyses),
            'summaries': summaries,
            'analyses': analyses,
            'metadata': {
                'source': 'lifesciencereport.com/newsroom',
                'target_word_count': config.TARGET_WORD_COUNT,
                'ai_model': config.AI_MODEL
            }
        }
        
        # Save JSON version
        json_path = os.path.join(config.REPORTS_DIR, f'healthcare_intelligence_{timestamp}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Save human-readable text version
        text_path = os.path.join(config.REPORTS_DIR, f'healthcare_intelligence_{timestamp}.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(self._format_text_report(summaries, analyses))
        
        self.todays_report_file = json_path
        return json_path
    
    def _format_text_report(self, summaries: List[Dict], analyses: List[Dict]) -> str:
        """Format report as human-readable text"""
        report = []
        report.append("="*80)
        report.append(f"DAILY HEALTHCARE INTELLIGENCE REPORT - {datetime.now().strftime('%B %d, %Y')}")
        report.append("="*80)
        report.append(f"\nSource: lifesciencereport.com/newsroom")
        report.append(f"Articles Analyzed: {len(summaries)}")
        report.append(f"In-Depth Analyses: {len(analyses)}")
        report.append("\n" + "="*80)
        report.append("ARTICLE SUMMARIES (~600 words each)")
        report.append("="*80)
        
        for i, summary in enumerate(summaries, 1):
            report.append(f"\n{'='*80}")
            report.append(f"ARTICLE {i}: {summary['title']}")
            report.append(f"URL: {summary['url']}")
            report.append(f"{'='*80}\n")
            report.append(summary['summary'])
            
            # Add stock intelligence if available
            if 'stock_intelligence' in summary:
                stock = summary['stock_intelligence']
                report.append(f"\n📊 REAL-TIME STOCK INTELLIGENCE:")
                report.append(f"Current Price: ${stock.get('current_price', 'N/A')}")
                report.append(f"Market Cap: {stock.get('market_cap', 'N/A')}")
                if stock.get('management_credibility'):
                    report.append(f"Management Credibility Score: {stock['management_credibility']}%")
        
        if analyses:
            report.append("\n\n" + "="*80)
            report.append("IN-DEPTH INVESTMENT ANALYSIS")
            report.append("="*80)
            
            for analysis in analyses:
                report.append(f"\n{'='*80}")
                report.append(f"DETAILED ANALYSIS: {analysis['title']}")
                if analysis.get('company_name'):
                    report.append(f"Company: {analysis['company_name']}")
                report.append(f"{'='*80}\n")
                report.append(analysis['analysis'])
        
        report.append(f"\n\n{'='*80}")
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        report.append("="*80)
        
        return '\n'.join(report)
    
    def _send_report(self, summaries: List[Dict], analyses: List[Dict]) -> bool:
        """Send the report via email"""
        try:
            # Only send if email is enabled
            if not config.EMAIL_ENABLED:
                logger.info("Email disabled in config - skipping email send")
                return False
                
            return self.email_sender.send_report(summaries, analyses)
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _save_no_news_report(self):
        """Save a report indicating no news was found"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(config.REPORTS_DIR, f'no_news_{timestamp}.txt')
        
        with open(report_path, 'w') as f:
            f.write(f"No new healthcare/biotech news found on {datetime.now().strftime('%B %d, %Y')}\n")
            f.write(f"Checked at: {datetime.now().strftime('%H:%M:%S ET')}\n")
            f.write("Next check will occur at the next scheduled time.\n")
    
    def _log_completion(self, total_articles: int, analyzed_articles: int):
        """Log completion statistics"""
        logger.info("\n" + "="*80)
        logger.info("✅ DAILY ANALYSIS COMPLETE")
        logger.info(f"Total articles processed: {total_articles}")
        logger.info(f"Articles selected for deep analysis: {analyzed_articles}")
        logger.info(f"Report location: {self.todays_report_file}")
        logger.info("="*80 + "\n")
    
    def _send_error_notification(self, error_message: str):
        """Send error notification if critical failure occurs"""
        logger.error(f"Critical error in daily analysis: {error_message}")
        # Could implement email notification here if needed


def run_scheduled():
    """Run the analysis on schedule"""
    intelligence = DailyHealthcareIntelligence()
    
    # Schedule runs at specified times
    for check_time in config.CHECK_TIMES:
        schedule.every().day.at(check_time.strftime("%H:%M")).do(intelligence.run_daily_analysis)
    
    logger.info(f"📅 Scheduled daily analysis at: {', '.join(t.strftime('%H:%M') for t in config.CHECK_TIMES)} ET")
    logger.info("🏃 Healthcare Intelligence System is running. Press Ctrl+C to stop.")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds


def run_once():
    """Run the analysis immediately (for testing or manual execution)"""
    intelligence = DailyHealthcareIntelligence()
    intelligence.run_daily_analysis()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Daily Healthcare Intelligence System',
        epilog='Analyzes healthcare/biotech news and generates investment-grade reports'
    )
    parser.add_argument('--once', action='store_true', 
                       help='Run analysis once immediately instead of on schedule')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with limited articles')
    
    args = parser.parse_args()
    
    if args.once:
        logger.info("Running one-time analysis...")
        run_once()
    else:
        try:
            run_scheduled()
        except KeyboardInterrupt:
            logger.info("\n🛑 Healthcare Intelligence System stopped by user")
            sys.exit(0) 