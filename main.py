"""
Main script for Healthcare News Automation
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

# Load environment variables
load_dotenv()

# Import our modules
import config
from scraper import LifeScienceScraper
from ai_generator import AISummaryGenerator
from email_sender import EmailSender

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HealthcareNewsAutomation:
    """Main automation class"""
    
    def __init__(self):
        self.scraper = LifeScienceScraper()
        self.ai_generator = AISummaryGenerator()
        self.email_sender = EmailSender()
    
    def run_daily_task(self, send_email=True):
        """Execute the daily news processing task"""
        logger.info("Starting daily healthcare news task")
        
        try:
            # 1. Scrape today's articles
            logger.info("Fetching today's articles...")
            articles = self.scraper.get_todays_articles()
            
            if not articles:
                logger.info("No new articles found for today")
                return
            
            logger.info(f"Found {len(articles)} new articles")
            
            # 2. Generate summaries
            logger.info("Generating summaries...")
            summaries = []
            
            for i, article in enumerate(articles):
                logger.info(f"Processing article {i+1}/{len(articles)}: {article.title}")
                
                summary_text = self.ai_generator.generate_summary(article)
                
                if summary_text:
                    summaries.append({
                        'title': article.title,
                        'url': article.url,
                        'summary': summary_text,
                        'company_name': article.company_name,
                        'article': article
                    })
                else:
                    logger.error(f"Failed to generate summary for: {article.title}")
            
            if not summaries:
                logger.error("No summaries were generated")
                return
            
            # 3. Select interesting articles
            logger.info("Selecting interesting articles...")
            interesting_indices = self.ai_generator.select_interesting_articles(summaries)
            
            # 4. Generate additional analysis for interesting articles with real-time company research
            analyses = []
            for idx in interesting_indices:
                if idx < len(summaries):
                    article_title = summaries[idx]['title']
                    company_name = summaries[idx].get('company_name', '')
                    logger.info(f"Generating news-specific analysis for: {article_title}")
                    logger.info(f"Company: {company_name}")
                    
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
            
            # 5. Save report locally
            self._save_report(summaries, analyses)
            
            # 6. Generate HTML report locally
            date_str = datetime.now().strftime('%Y-%m-%d')
            html_file = os.path.join(config.REPORTS_DIR, f'report_{date_str}.html')
            self._save_html_report(summaries, analyses, html_file)
            
            # 7. Send email report (if enabled)
            if send_email:
                logger.info("Sending email report...")
                success = self.email_sender.send_report(summaries, analyses)
                
                if success:
                    logger.info("Email report sent successfully")
                else:
                    logger.error("Failed to send email report")
            else:
                logger.info(f"Email sending disabled. Report saved to: {html_file}")
            
            logger.info("Daily task completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily task: {e}", exc_info=True)
            # Send error notification
            self._send_error_notification(str(e))
    
    def _save_report(self, summaries, analyses):
        """Save report to local file"""
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_file = os.path.join(config.REPORTS_DIR, f'report_{date_str}.json')
            
            report_data = {
                'date': date_str,
                'timestamp': datetime.now().isoformat(),
                'summaries': summaries,
                'analyses': analyses
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def _save_html_report(self, summaries, analyses, filename):
        """Save HTML report to local file"""
        try:
            # Generate HTML content using the email sender's method
            date = datetime.now()
            html_content = self.email_sender._generate_html_content(summaries, analyses, date)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving HTML report: {e}")
    
    def _send_error_notification(self, error_message):
        """Send error notification email"""
        try:
            subject = "Healthcare News Automation - Error Report"
            content = f"""
            <h2>Error in Healthcare News Automation</h2>
            <p>The following error occurred during the daily news processing:</p>
            <pre>{error_message}</pre>
            <p>Please check the logs for more details.</p>
            """
            
            # Simple error email
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = config.EMAIL_FROM
            msg['To'] = ', '.join(config.EMAIL_RECIPIENTS)
            msg.attach(MIMEText(content, 'html'))
            
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def schedule_daily_runs(self):
        """Schedule daily runs at specified times"""
        for check_time in config.CHECK_TIMES:
            schedule.every().day.at(check_time.strftime("%H:%M")).do(self.run_daily_task)
            logger.info(f"Scheduled daily run at {check_time.strftime('%H:%M')} {config.TIMEZONE}")
        
        logger.info("Scheduler started. Waiting for scheduled times...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Healthcare News Automation')
    parser.add_argument('--run-now', action='store_true', help='Run the task immediately')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    parser.add_argument('--test-email', action='store_true', help='Send a test email')
    parser.add_argument('--local-only', action='store_true', help='Generate reports locally without sending emails')
    
    args = parser.parse_args()
    
    automation = HealthcareNewsAutomation()
    
    if args.test_email:
        logger.info("Sending test email...")
        test_summaries = [{
            'title': 'Test Article',
            'url': 'https://example.com',
            'summary': 'This is a test summary to verify email functionality.'
        }]
        test_analyses = []
        success = automation.email_sender.send_report(test_summaries, test_analyses)
        if success:
            logger.info("Test email sent successfully")
        else:
            logger.error("Failed to send test email")
    
    elif args.run_now:
        logger.info("Running task immediately...")
        automation.run_daily_task()
    
    elif args.local_only:
        logger.info("Running task in local-only mode (no emails)...")
        automation.run_daily_task(send_email=False)
    
    elif args.schedule:
        automation.schedule_daily_runs()
    
    else:
        # Default: run in local-only mode
        logger.info("No arguments provided, running in local-only mode...")
        automation.run_daily_task(send_email=False)


if __name__ == "__main__":
    main() 