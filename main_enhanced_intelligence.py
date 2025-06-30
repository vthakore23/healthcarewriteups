#!/usr/bin/env python3
"""
Enhanced main script with integrated Healthcare Investment Intelligence
Includes Management Truth Tracker™ and FDA Decision Pattern Analyzer
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

# Load environment variables
load_dotenv()

# Import standard modules
import config
from scraper_optimized import OptimizedLifeScienceScraper
from ai_generator_optimized import OptimizedAISummaryGenerator
from email_sender import EmailSender

# Import intelligence modules
from integrated_intelligence_system import IntegratedIntelligenceSystem
from management_truth_tracker import ManagementTruthTracker
from fda_decision_analyzer import FDADecisionAnalyzer

# Setup enhanced logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('healthcare_intelligence.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class EnhancedHealthcareIntelligence:
    """Enhanced automation with integrated investment intelligence"""
    
    def __init__(self):
        logger.info("🚀 Initializing Enhanced Healthcare Investment Intelligence...")
        
        # Standard components
        self.scraper = OptimizedLifeScienceScraper(max_workers=5)
        self.ai_generator = OptimizedAISummaryGenerator(max_workers=3)
        self.email_sender = EmailSender()
        
        # Intelligence components
        self.intel_system = IntegratedIntelligenceSystem()
        self.truth_tracker = ManagementTruthTracker()
        self.fda_analyzer = FDADecisionAnalyzer()
        
        logger.info("✅ All systems initialized")
    
    def run_daily_intelligence(self, send_email=True, limit_articles=None):
        """Execute daily intelligence gathering and analysis"""
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("🧬 HEALTHCARE INVESTMENT INTELLIGENCE - DAILY ANALYSIS")
        logger.info("   Including Management Truth Tracking & FDA Pattern Analysis")
        logger.info("=" * 80)
        
        try:
            # 1. Scrape today's articles
            logger.info("\n📥 STEP 1: Fetching today's articles...")
            articles = self.scraper.get_todays_articles()
            
            if not articles:
                logger.info("❌ No new articles found for today")
                return
            
            if limit_articles:
                articles = articles[:limit_articles]
            
            logger.info(f"✅ Found {len(articles)} articles to analyze")
            
            # 2. Generate standard summaries
            logger.info(f"\n🤖 STEP 2: Generating AI summaries...")
            summaries = self.ai_generator.generate_summaries_batch(articles)
            logger.info(f"✅ Generated {len(summaries)} summaries")
            
            # 3. Apply intelligence analysis to each article
            logger.info(f"\n🕵️ STEP 3: Applying investment intelligence analysis...")
            intelligence_results = []
            
            for i, article in enumerate(articles):
                logger.info(f"\n📊 Analyzing article {i+1}/{len(articles)}: {article.title[:60]}...")
                
                try:
                    # Run integrated intelligence analysis
                    intel_analysis = self.intel_system.analyze_news_with_intelligence(article)
                    intelligence_results.append(intel_analysis)
                    
                    # Log key findings
                    if intel_analysis['management_credibility']:
                        cred = intel_analysis['management_credibility']
                        if cred['red_flags']:
                            logger.warning(f"   ⚠️  Credibility issues found: {len(cred['red_flags'])} red flags")
                    
                    if intel_analysis['fda_implications'] and intel_analysis['fda_implications']['submission_analysis']:
                        fda = intel_analysis['fda_implications']['submission_analysis']
                        logger.info(f"   📊 FDA approval probability: {fda['approval_probability']:.1%}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Intelligence analysis failed: {e}")
                    intelligence_results.append(None)
            
            # 4. Select most interesting articles with intelligence weighting
            logger.info(f"\n🎯 STEP 4: Selecting most impactful articles...")
            interesting_indices = self._select_high_impact_articles(summaries, intelligence_results)
            logger.info(f"✅ Selected {len(interesting_indices)} high-impact articles")
            
            # 5. Generate deep analysis for selected articles
            logger.info(f"\n🔍 STEP 5: Generating deep analysis with intelligence insights...")
            analyses = []
            
            for idx in interesting_indices:
                if idx < len(summaries):
                    article = summaries[idx]['article']
                    intel = intelligence_results[idx] if idx < len(intelligence_results) else None
                    
                    # Generate enhanced analysis with intelligence context
                    analysis = self._generate_enhanced_analysis(
                        article=article,
                        summary=summaries[idx]['summary'],
                        intelligence=intel
                    )
                    
                    if analysis:
                        analyses.append(analysis)
            
            # 6. Generate comprehensive intelligence report
            logger.info(f"\n📊 STEP 6: Generating comprehensive intelligence report...")
            intel_report = self.intel_system.generate_comprehensive_report(articles)
            
            # 7. Save all reports
            logger.info(f"\n💾 STEP 7: Saving reports...")
            report_paths = self._save_intelligence_reports(summaries, analyses, intelligence_results, intel_report)
            
            # 8. Send enhanced email report
            if send_email:
                logger.info(f"\n📧 STEP 8: Sending intelligence report...")
                success = self._send_intelligence_email(summaries, analyses, intel_report)
                
                if success:
                    logger.info("✅ Intelligence report sent successfully")
                else:
                    logger.error("❌ Failed to send intelligence report")
            
            # Summary statistics
            elapsed_time = time.time() - start_time
            self._print_analysis_summary(len(articles), len(summaries), len(analyses), 
                                       intel_report, elapsed_time)
            
        except Exception as e:
            logger.error(f"❌ Error in intelligence analysis: {e}", exc_info=True)
    
    def _select_high_impact_articles(self, summaries, intelligence_results):
        """Select articles with highest investment impact using intelligence"""
        scored_articles = []
        
        for idx, (summary, intel) in enumerate(zip(summaries, intelligence_results)):
            score = 0.0
            
            # Base score from content
            base_score = self.ai_generator._score_article_importance(summary)
            score += base_score * 0.5
            
            # Intelligence scoring
            if intel:
                # Management credibility impact
                if intel.get('management_credibility'):
                    cred = intel['management_credibility']
                    if cred.get('red_flags'):
                        score += len(cred['red_flags']) * 10  # Red flags are important
                    if cred.get('new_promises'):
                        score += len(cred['new_promises']) * 5
                
                # FDA decision impact
                if intel.get('fda_implications') and intel['fda_implications'].get('submission_analysis'):
                    fda = intel['fda_implications']['submission_analysis']
                    # High or low probability are both interesting
                    prob = fda.get('approval_probability', 0.5)
                    if prob > 0.8 or prob < 0.3:
                        score += 20
                    score += 10  # Any FDA news is important
                
                # High priority alerts
                if intel.get('investment_alerts'):
                    high_priority = [a for a in intel['investment_alerts'] 
                                   if isinstance(a, dict) and a.get('level') == 'HIGH']
                    score += len(high_priority) * 15
            
            scored_articles.append((idx, score))
        
        # Sort by score and return top articles
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, _ in scored_articles[:2]]  # Top 2 articles
    
    def _generate_enhanced_analysis(self, article, summary, intelligence):
        """Generate deep analysis incorporating intelligence insights"""
        # Start with standard analysis
        base_analysis = self.ai_generator.generate_analysis(
            summary_text=summary,
            article_title=article.title,
            company_name=article.company_name
        )
        
        if not intelligence or not base_analysis:
            return {
                'title': article.title,
                'url': article.url,
                'summary': summary,
                'analysis': base_analysis,
                'company_name': article.company_name
            }
        
        # Enhance with intelligence insights
        enhanced_text = base_analysis + "\n\n"
        enhanced_text += "=" * 60 + "\n"
        enhanced_text += "INVESTMENT INTELLIGENCE INSIGHTS\n"
        enhanced_text += "=" * 60 + "\n\n"
        
        # Add management credibility insights
        if intelligence.get('management_credibility'):
            cred = intelligence['management_credibility']
            enhanced_text += "🕵️ MANAGEMENT CREDIBILITY ANALYSIS:\n\n"
            
            if cred.get('executives_analyzed'):
                for exec in cred['executives_analyzed']:
                    enhanced_text += f"• {exec['name']} ({exec['title']})\n"
                    enhanced_text += f"  - Track Record: {exec['track_record']}\n"
                    enhanced_text += f"  - Credibility Score: {exec['credibility_score']:.0%}\n"
                    if exec.get('average_delay', 0) > 0:
                        enhanced_text += f"  - Average Delay: {exec['average_delay']} days\n"
                    enhanced_text += "\n"
            
            if cred.get('red_flags'):
                enhanced_text += "⚠️ CREDIBILITY RED FLAGS:\n"
                for flag in cred['red_flags']:
                    enhanced_text += f"  - {flag}\n"
                enhanced_text += "\n"
        
        # Add FDA analysis insights
        if intelligence.get('fda_implications') and intelligence['fda_implications'].get('submission_analysis'):
            fda = intelligence['fda_implications']['submission_analysis']
            enhanced_text += "📊 FDA APPROVAL ANALYSIS:\n\n"
            enhanced_text += f"• Approval Probability: {fda['approval_probability']:.0%}\n"
            enhanced_text += f"• Predicted Outcome: {fda['predicted_outcome'].value}\n"
            enhanced_text += f"• Expected Timeline: {fda['timeline_prediction']['expected_review_days']} days\n"
            
            if fda.get('key_risk_factors'):
                enhanced_text += "\nKey Risks:\n"
                for risk in fda['key_risk_factors'][:3]:
                    enhanced_text += f"  - {risk}\n"
            enhanced_text += "\n"
        
        # Add integrated insights
        if intelligence.get('integrated_insights'):
            enhanced_text += "💡 KEY INVESTMENT INSIGHTS:\n"
            for insight in intelligence['integrated_insights']:
                enhanced_text += f"  {insight}\n"
            enhanced_text += "\n"
        
        # Add action items
        if intelligence.get('action_items'):
            enhanced_text += "📋 RECOMMENDED ACTIONS:\n"
            for action in intelligence['action_items']:
                enhanced_text += f"  {action}\n"
        
        return {
            'title': article.title,
            'url': article.url,
            'summary': summary,
            'analysis': enhanced_text,
            'company_name': article.company_name,
            'intelligence': intelligence
        }
    
    def _save_intelligence_reports(self, summaries, analyses, intelligence_results, intel_report):
        """Save all reports including intelligence data"""
        paths = []
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Save standard reports
        report_data = {
            'date': date_str,
            'timestamp': datetime.now().isoformat(),
            'summaries': [s for s in summaries if s],  # Filter None values
            'analyses': analyses,
            'intelligence_results': [i for i in intelligence_results if i],
            'comprehensive_intelligence': intel_report
        }
        
        # Save JSON report
        json_file = os.path.join(config.REPORTS_DIR, f'intelligence_report_{date_str}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
        paths.append(json_file)
        logger.info(f"✅ Intelligence JSON saved: {json_file}")
        
        # Save HTML report
        html_file = os.path.join(config.REPORTS_DIR, f'intelligence_report_{date_str}.html')
        html_content = self._generate_intelligence_html(summaries, analyses, intel_report)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        paths.append(html_file)
        logger.info(f"✅ Intelligence HTML saved: {html_file}")
        
        return paths
    
    def _generate_intelligence_html(self, summaries, analyses, intel_report):
        """Generate enhanced HTML report with intelligence insights"""
        # Use email sender's template as base and enhance it
        date = datetime.now()
        base_html = self.email_sender._generate_html_content(summaries, analyses, date)
        
        # Insert intelligence summary before the closing body tag
        intel_section = self._create_intelligence_summary_html(intel_report)
        
        # Add detailed credibility reports for executives with issues
        credibility_section = self._create_credibility_details_html(summaries, intel_report)
        
        # Find insertion point (before </body>)
        insert_point = base_html.rfind('</body>')
        if insert_point > 0:
            enhanced_html = (base_html[:insert_point] + 
                           intel_section + 
                           credibility_section +
                           base_html[insert_point:])
        else:
            enhanced_html = base_html + intel_section + credibility_section
        
        return enhanced_html
    
    def _create_intelligence_summary_html(self, intel_report):
        """Create HTML section for intelligence summary"""
        html = """
        <div style="margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px;">
            <h2 style="color: white; text-align: center; margin-bottom: 30px;">
                🧬 Investment Intelligence Summary
            </h2>
        """
        
        # High Priority Alerts
        if intel_report.get('high_priority_alerts'):
            html += """
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #d32f2f;">🚨 High Priority Alerts</h3>
            """
            for alert in intel_report['high_priority_alerts']:
                html += f"""
                <p style="margin: 10px 0;">
                    <strong>{alert['company']}:</strong> {alert['alert']['message']}<br>
                    <em style="color: #666;">Action: {alert['alert']['action']}</em>
                </p>
                """
            html += "</div>"
        
        # Credibility Warnings
        if intel_report.get('credibility_warnings'):
            html += """
            <div style="background: #fff8e1; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #f57c00;">⚠️ Management Credibility Warnings</h3>
            """
            for warning in intel_report['credibility_warnings']:
                html += f"""
                <p style="margin: 10px 0;">
                    <strong>{warning['company']}:</strong> {warning['warning']}
                </p>
                """
            html += "</div>"
        
        # FDA Calendar
        if intel_report.get('fda_calendar'):
            html += """
            <div style="background: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #2e7d32;">📅 Upcoming FDA Decisions</h3>
            """
            for item in intel_report['fda_calendar']:
                days = item.get('expected_decision', {}).get('expected_review_days', 'TBD')
                html += f"""
                <p style="margin: 10px 0;">
                    <strong>{item['company']}:</strong> Decision expected in ~{days} days
                    {' (AdCom likely)' if item.get('adcom_likely') else ''}
                </p>
                """
            html += "</div>"
        
        # Investment Themes
        if intel_report.get('investment_themes'):
            html += """
            <div style="background: #f3e5f5; padding: 20px; border-radius: 10px;">
                <h3 style="color: #6a1b9a;">🎯 Investment Themes</h3>
            """
            for theme in intel_report['investment_themes']:
                html += f"<p style='margin: 10px 0;'>{theme}</p>"
            html += "</div>"
        
        html += "</div>"
        return html
    
    def _create_credibility_details_html(self, summaries, intel_report):
        """Create detailed credibility reports for executives with low scores"""
        html = ""
        
        # Collect all executives with credibility issues
        low_cred_executives = []
        
        for detail in intel_report.get('detailed_analyses', []):
            if detail and detail.get('management_credibility'):
                cred = detail['management_credibility']
                for exec in cred.get('executives_analyzed', []):
                    if exec['credibility_score'] < 0.5:  # Low credibility threshold
                        # Get detailed promise history
                        promise_details = self.truth_tracker.get_executive_promise_details(
                            exec['name'], detail['article']['company']
                        )
                        low_cred_executives.append({
                            'exec': exec,
                            'company': detail['article']['company'],
                            'details': promise_details
                        })
        
        if not low_cred_executives:
            return ""
        
        html += """
        <div style="margin-top: 30px; padding: 30px; background: #ffebee; border-radius: 15px;">
            <h2 style="color: #c62828; text-align: center; margin-bottom: 30px;">
                🚨 Executive Credibility Detailed Reports
            </h2>
        """
        
        for item in low_cred_executives:
            exec = item['exec']
            details = item['details']
            company = item['company']
            
            html += f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #d32f2f;">
                <h3 style="color: #c62828;">{exec['name']} - {exec['title']} at {company}</h3>
                <p style="font-size: 18px; color: #d32f2f;">
                    <strong>Credibility Score: {exec['credibility_score']:.0%}</strong> 
                    (Track Record: {exec['track_record']})
                </p>
            """
            
            # Failed promises section
            if details.get('failed_promises'):
                html += """
                <h4 style="color: #d32f2f; margin-top: 20px;">❌ Failed Promises:</h4>
                <ul style="list-style-type: none; padding-left: 0;">
                """
                for promise in details['failed_promises'][:3]:  # Show top 3
                    html += f"""
                    <li style="margin-bottom: 15px; padding: 10px; background: #ffebee; border-radius: 5px;">
                        <strong>{promise['promise_type'].replace('_', ' ').title()}</strong><br>
                        <em>"{promise['promise_text'][:150]}..."</em><br>
                        <span style="color: #666; font-size: 14px;">
                            Promise made: {promise['date_made'][:10]} | 
                            Deadline: {promise['deadline'][:10] if promise['deadline'] else 'No deadline'} |
                            Status: FAILED
                        </span>
                    </li>
                    """
                html += "</ul>"
            
            # Average delay
            if exec.get('average_delay', 0) > 0:
                html += f"""
                <p style="color: #666; margin-top: 15px;">
                    <strong>Average Delay:</strong> {exec['average_delay']} days when promises are delivered
                </p>
                """
            
            # Investment warning
            html += """
            <div style="background: #ffcdd2; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <strong>⚠️ Investment Warning:</strong> This executive has a poor track record of 
                meeting promised timelines. Consider adding significant buffer to any timeline 
                guidance and monitor promises closely.
            </div>
            """
            
            html += "</div>"
        
        # Add link to standalone credibility checker
        html += """
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: #666;">
                For more detailed credibility analysis, use the standalone tool:<br>
                <code style="background: #f5f5f5; padding: 5px 10px; border-radius: 3px;">
                python check_executive_credibility.py search "executive name"
                </code>
            </p>
        </div>
        """
        
        html += "</div>"
        return html
    
    def _send_intelligence_email(self, summaries, analyses, intel_report):
        """Send enhanced email with intelligence insights"""
        # For now, use standard email sender
        # In production, would create custom intelligence email template
        return self.email_sender.send_report(summaries, analyses)
    
    def _print_analysis_summary(self, total_articles, summaries, analyses, intel_report, elapsed_time):
        """Print comprehensive analysis summary"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 INTELLIGENCE ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"✅ Articles processed: {total_articles}")
        logger.info(f"✅ Summaries generated: {summaries}")
        logger.info(f"✅ Deep analyses: {analyses}")
        
        if intel_report:
            logger.info(f"\n🧬 Intelligence Findings:")
            logger.info(f"  • High priority alerts: {len(intel_report.get('high_priority_alerts', []))}")
            logger.info(f"  • Credibility warnings: {len(intel_report.get('credibility_warnings', []))}")
            logger.info(f"  • FDA decisions tracked: {len(intel_report.get('fda_calendar', []))}")
            logger.info(f"  • Investment themes: {len(intel_report.get('investment_themes', []))}")
        
        logger.info(f"\n⏱️  Total time: {elapsed_time:.1f} seconds")
        logger.info(f"⚡ Average per article: {elapsed_time/total_articles:.1f} seconds")
        logger.info("=" * 80)
    
    def check_promises_due(self):
        """Check for promises coming due and generate alerts"""
        logger.info("\n📅 Checking for promises coming due...")
        
        promises_due = self.truth_tracker.check_promises_due(days_ahead=30)
        
        if promises_due:
            logger.info(f"⏰ Found {len(promises_due)} promises due within 30 days:")
            for promise in promises_due[:5]:  # Show top 5
                logger.info(f"  • {promise['company']} - {promise['executive_name']}")
                logger.info(f"    {promise['promise_type']}: Due in {promise['days_until_deadline']} days")
        
        return promises_due


def main():
    """Main entry point for enhanced intelligence system"""
    parser = argparse.ArgumentParser(
        description='Healthcare Investment Intelligence System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --run-now          # Run full intelligence analysis
  %(prog)s --demo             # Run demo with 3 articles
  %(prog)s --check-promises   # Check promises coming due
  %(prog)s --run-demo         # Run intelligence demo
        """
    )
    
    parser.add_argument('--run-now', action='store_true', help='Run intelligence analysis immediately')
    parser.add_argument('--demo', action='store_true', help='Run demo mode (3 articles)')
    parser.add_argument('--check-promises', action='store_true', help='Check promises coming due')
    parser.add_argument('--run-demo', action='store_true', help='Run full intelligence demo')
    parser.add_argument('--local-only', action='store_true', help='Run without sending emails')
    
    args = parser.parse_args()
    
    # Show banner
    print("\n" + "="*80)
    print("   🧬 HEALTHCARE INVESTMENT INTELLIGENCE SYSTEM")
    print("   With Management Truth Tracker™ & FDA Decision Analyzer")
    print("="*80 + "\n")
    
    if args.run_demo:
        # Run the demo script
        import demo_integrated_intelligence
        demo_integrated_intelligence.main()
    elif args.check_promises:
        # Check promises due
        intelligence = EnhancedHealthcareIntelligence()
        intelligence.check_promises_due()
    else:
        # Run analysis
        intelligence = EnhancedHealthcareIntelligence()
        
        if args.demo:
            logger.info("🎯 Running in demo mode (3 articles)...")
            intelligence.run_daily_intelligence(send_email=False, limit_articles=3)
        elif args.run_now:
            logger.info("🚀 Running full intelligence analysis...")
            intelligence.run_daily_intelligence(send_email=not args.local_only)
        else:
            # Default: show help
            parser.print_help()


if __name__ == "__main__":
    main() 