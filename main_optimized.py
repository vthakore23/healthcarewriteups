"""
Optimized main script for Healthcare News Automation
"""
import logging
import sys
import os
from datetime import datetime
import json
import schedule
import time
import argparse
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Import our modules
import config
from scraper_optimized import OptimizedLifeScienceScraper
from ai_generator_optimized import OptimizedAISummaryGenerator
from email_sender import EmailSender

# Setup logging with better formatting
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class OptimizedHealthcareNewsAutomation:
    """Optimized automation class with better performance"""
    
    def __init__(self):
        logger.info("🚀 Initializing Healthcare News Automation...")
        self.scraper = OptimizedLifeScienceScraper(max_workers=5)
        self.ai_generator = OptimizedAISummaryGenerator(max_workers=3)
        self.email_sender = EmailSender()
        logger.info("✅ Initialization complete")
    
    def run_daily_task(self, send_email=True, limit_articles=None):
        """Execute the daily news processing task with optimizations"""
        start_time = time.time()
        logger.info("=" * 60)
        logger.info("📰 STARTING DAILY HEALTHCARE NEWS TASK")
        logger.info("=" * 60)
        
        try:
            # 1. Scrape today's articles
            logger.info("\n📥 STEP 1: Fetching today's articles...")
            articles = self.scraper.get_todays_articles()
            
            if not articles:
                logger.info("❌ No new articles found for today")
                self._send_no_articles_notification()
                return
            
            # Apply limit if specified
            if limit_articles and len(articles) > limit_articles:
                logger.info(f"🔧 Limiting to {limit_articles} articles for processing")
                articles = articles[:limit_articles]
            
            logger.info(f"✅ Found {len(articles)} new articles to process")
            
            # 2. Generate summaries in parallel
            logger.info(f"\n🤖 STEP 2: Generating AI summaries (parallel processing)...")
            summaries = self.ai_generator.generate_summaries_batch(articles)
            
            if not summaries:
                logger.error("❌ No summaries were generated")
                return
            
            logger.info(f"✅ Generated {len(summaries)} summaries")
            
            # 3. Select interesting articles (using smart selection)
            logger.info(f"\n🎯 STEP 3: Selecting most interesting articles...")
            interesting_indices = self.ai_generator.select_interesting_articles_smart(summaries)
            logger.info(f"✅ Selected {len(interesting_indices)} articles for deep analysis")
            
            # 4. Generate additional analysis for interesting articles
            logger.info(f"\n🔍 STEP 4: Generating comprehensive in-depth analysis with real-time company research...")
            analyses = []
            for i, idx in enumerate(interesting_indices):
                if idx < len(summaries):
                    article_title = summaries[idx]['title']
                    company_name = summaries[idx].get('company_name', '')
                    logger.info(f"   📊 Analyzing article {i+1}/{len(interesting_indices)}: {article_title[:60]}...")
                    logger.info(f"   🔬 Company: {company_name}")
                    
                    # Generate news-specific analysis focused on why this news matters for this company
                    analysis_text = self.ai_generator.generate_analysis(
                        summary_text=summaries[idx]['summary'],
                        article_title=article_title,
                        company_name=company_name
                    )
                    
                    if analysis_text:
                        analyses.append({
                            'title': article_title,
                            'url': summaries[idx]['url'],
                            'summary': summaries[idx]['summary'],
                            'analysis': analysis_text,
                            'company_name': company_name
                        })
                        logger.info(f"   ✅ News-specific analysis complete")
            
            # 5. Save report locally
            logger.info(f"\n💾 STEP 5: Saving reports...")
            report_paths = self._save_reports(summaries, analyses)
            
            # 6. Send email report (if enabled)
            if send_email:
                logger.info(f"\n📧 STEP 6: Sending email report...")
                success = self.email_sender.send_report(summaries, analyses)
                
                if success:
                    logger.info("✅ Email report sent successfully")
                else:
                    logger.error("❌ Failed to send email report")
            else:
                logger.info(f"\n📧 STEP 6: Email sending disabled")
                logger.info(f"📄 Reports saved to:")
                for path in report_paths:
                    logger.info(f"   - {path}")
            
            # Summary statistics
            elapsed_time = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info("📊 TASK COMPLETE - SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✅ Articles processed: {len(articles)}")
            logger.info(f"✅ Summaries generated: {len(summaries)}")
            logger.info(f"✅ Deep analyses: {len(analyses)}")
            logger.info(f"⏱️  Total time: {elapsed_time:.1f} seconds")
            logger.info(f"⚡ Average time per article: {elapsed_time/len(articles):.1f} seconds")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error in daily task: {e}", exc_info=True)
            self._send_error_notification(str(e))
    
    def _save_reports(self, summaries, analyses):
        """Save reports and return file paths"""
        paths = []
        
        # Save JSON report
        json_path = self._save_json_report(summaries, analyses)
        if json_path:
            paths.append(json_path)
        
        # Save HTML report
        html_path = self._save_html_report(summaries, analyses)
        if html_path:
            paths.append(html_path)
        
        return paths
    
    def _save_json_report(self, summaries, analyses):
        """Save report to JSON file"""
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_file = os.path.join(config.REPORTS_DIR, f'report_{date_str}.json')
            
            # Convert articles to dict for JSON serialization
            summaries_json = []
            for s in summaries:
                summary_dict = s.copy()
                if 'article' in summary_dict:
                    summary_dict['article'] = summary_dict['article'].to_dict()
                summaries_json.append(summary_dict)
            
            report_data = {
                'date': date_str,
                'timestamp': datetime.now().isoformat(),
                'summaries': summaries_json,
                'analyses': analyses,
                'statistics': {
                    'total_articles': len(summaries),
                    'analyzed_articles': len(analyses)
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"✅ JSON report saved: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON report: {e}")
            return None
    
    def _save_html_report(self, summaries, analyses):
        """Save HTML report to local file"""
        try:
            date = datetime.now()
            date_str = date.strftime('%Y-%m-%d')
            html_file = os.path.join(config.REPORTS_DIR, f'report_{date_str}.html')
            
            # Generate HTML content using the email sender's method
            html_content = self.email_sender._generate_html_content(summaries, analyses, date)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML report saved: {html_file}")
            return html_file
            
        except Exception as e:
            logger.error(f"❌ Error saving HTML report: {e}")
            return None
    
    def _send_no_articles_notification(self):
        """Send notification when no articles are found"""
        try:
            subject = "Healthcare News Automation - No Articles Found"
            content = f"""
            <h2>No New Articles Found</h2>
            <p>The automated news check at {datetime.now().strftime('%Y-%m-%d %H:%M')} found no new articles to process.</p>
            <p>This could mean:</p>
            <ul>
                <li>No new articles were published today</li>
                <li>The website structure may have changed</li>
                <li>There may be a connectivity issue</li>
            </ul>
            <p>Please check the logs for more details.</p>
            """
            
            # Send notification if email is configured
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = config.EMAIL_FROM
                msg['To'] = ', '.join(config.EMAIL_RECIPIENTS)
                msg.attach(MIMEText(content, 'html'))
                
                with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(msg)
                    
        except Exception as e:
            logger.error(f"Failed to send no-articles notification: {e}")
    
    def _send_error_notification(self, error_message):
        """Send error notification email"""
        try:
            subject = "Healthcare News Automation - Error Report"
            content = f"""
            <h2>Error in Healthcare News Automation</h2>
            <p>The following error occurred during the daily news processing:</p>
            <pre>{error_message}</pre>
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Please check the logs for more details.</p>
            """
            
            # Simple error email
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = config.EMAIL_FROM
                msg['To'] = ', '.join(config.EMAIL_RECIPIENTS)
                msg.attach(MIMEText(content, 'html'))
                
                with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(msg)
                    
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def schedule_daily_runs(self):
        """Schedule daily runs at specified times"""
        for check_time in config.CHECK_TIMES:
            schedule.every().day.at(check_time.strftime("%H:%M")).do(self.run_daily_task)
            logger.info(f"📅 Scheduled daily run at {check_time.strftime('%H:%M')} {config.TIMEZONE}")
        
        logger.info("⏰ Scheduler started. Waiting for scheduled times...")
        logger.info("   Press Ctrl+C to stop")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Healthcare News Automation - Optimized Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --local-only          # Run without sending emails
  %(prog)s --run-now             # Run with email sending
  %(prog)s --demo                # Run demo with 3 articles
  %(prog)s --schedule            # Run on schedule
  %(prog)s --test-email          # Test email configuration
        """
    )
    
    parser.add_argument('--run-now', action='store_true', help='Run the task immediately with emails')
    parser.add_argument('--local-only', action='store_true', help='Generate reports locally without sending emails')
    parser.add_argument('--demo', action='store_true', help='Run demo mode (3 articles only)')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    parser.add_argument('--test-email', action='store_true', help='Send a test email')
    parser.add_argument('--limit', type=int, help='Limit number of articles to process')
    
    args = parser.parse_args()
    
    # Show banner
    print("\n" + "="*60)
    print("   HEALTHCARE NEWS AUTOMATION - OPTIMIZED VERSION")
    print("="*60 + "\n")
    
    automation = OptimizedHealthcareNewsAutomation()
    
    if args.test_email:
        logger.info("📧 Sending test email...")
        test_summaries = [{
            'title': 'Test Article - Healthcare News Automation',
            'url': 'https://example.com',
            'summary': '''Company Name: Test Pharmaceuticals Inc.
News Event: System Test
News Summary:
This is a test summary to verify that the Healthcare News Automation system is properly configured and able to send email reports. The system successfully initialized all components including the web scraper, AI generator, and email sender. All API connections have been verified and are functioning correctly. The system is ready to process healthcare and biotech news articles. This test confirms that email delivery is working as expected.
Standout Points:
- Email configuration verified
- API connections established
- System components initialized
- Ready for production use
Additional Developments:
The automated system will run at scheduled times to fetch and analyze healthcare news, providing structured summaries and strategic insights for investment decisions.'''
        }]
        test_analyses = []
        success = automation.email_sender.send_report(test_summaries, test_analyses)
        if success:
            logger.info("✅ Test email sent successfully")
        else:
            logger.error("❌ Failed to send test email")
    
    elif args.demo:
        logger.info("🎯 Running in demo mode (3 articles)...")
        automation.run_daily_task(send_email=False, limit_articles=3)
    
    elif args.run_now:
        logger.info("🚀 Running task immediately with email...")
        limit = args.limit if args.limit else None
        automation.run_daily_task(send_email=True, limit_articles=limit)
    
    elif args.local_only:
        logger.info("🏠 Running task in local-only mode (no emails)...")
        limit = args.limit if args.limit else None
        automation.run_daily_task(send_email=False, limit_articles=limit)
    
    elif args.schedule:
        automation.schedule_daily_runs()
    
    else:
        # Default: run full analysis with email (Chris's production workflow)
        logger.info("🏢 Running full daily analysis with email...")
        automation.run_daily_task(send_email=True)


if __name__ == "__main__":
    main() 