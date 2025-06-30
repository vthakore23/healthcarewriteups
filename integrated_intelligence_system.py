"""
Integrated Healthcare Investment Intelligence System
Combines news automation with Management Truth Tracker and FDA Decision Analyzer
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import re
from collections import defaultdict

from management_truth_tracker import (
    ManagementTruthTracker,
    ExecutivePromise,
    PromiseStatus,
    PromiseType
)
from fda_decision_analyzer import (
    FDADecisionAnalyzer,
    FDASubmission,
    DrugType,
    FDAReviewDivision,
    ReviewPathway,
    FDADecisionType
)
from ai_generator_enhanced import EnhancedAIGenerator
from scraper_optimized import NewsArticle

logger = logging.getLogger(__name__)


class IntegratedIntelligenceSystem:
    """Integrates all intelligence components for comprehensive analysis"""
    
    def __init__(self):
        self.truth_tracker = ManagementTruthTracker()
        self.fda_analyzer = FDADecisionAnalyzer()
        self.ai_generator = EnhancedAIGenerator()
        self.company_intelligence = {}
        
    def analyze_news_with_intelligence(self, article: NewsArticle) -> Dict[str, any]:
        """Analyze news article with full intelligence integration"""
        analysis = {
            'article': {
                'title': article.title,
                'company': article.company_name,
                'date': article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown',
                'url': article.url
            },
            'standard_summary': None,
            'management_credibility': None,
            'fda_implications': None,
            'integrated_insights': [],
            'investment_alerts': [],
            'action_items': []
        }
        
        # Generate standard summary
        analysis['standard_summary'] = self.ai_generator.generate_enhanced_summary(article)
        
        # Extract company and executive information
        company_info = self._extract_company_info(article)
        
        # Check management credibility if executives are mentioned
        if company_info['executives']:
            analysis['management_credibility'] = self._analyze_management_credibility(
                article, company_info
            )
        
        # Check for FDA-related content
        if self._is_fda_related(article):
            analysis['fda_implications'] = self._analyze_fda_implications(
                article, company_info
            )
        
        # Generate integrated insights
        analysis['integrated_insights'] = self._generate_integrated_insights(
            analysis, article, company_info
        )
        
        # Generate investment alerts
        analysis['investment_alerts'] = self._generate_investment_alerts(
            analysis, company_info
        )
        
        # Generate action items
        analysis['action_items'] = self._generate_action_items(
            analysis, company_info
        )
        
        return analysis
    
    def _extract_company_info(self, article: NewsArticle) -> Dict:
        """Extract company and executive information from article"""
        info = {
            'company': article.company_name or 'Unknown',
            'company_name': article.company_name or 'Unknown',
            'executives': [],
            'promises': [],
            'fda_mentions': []
        }
        
        # Extract executive names and titles
        exec_pattern = r'(?:CEO|CFO|CMO|President|Chief\s+\w+\s+Officer)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)|([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:CEO|CFO|CMO|President|Chief\s+\w+\s+Officer)'
        
        for match in re.finditer(exec_pattern, article.content):
            name = match.group(1) or match.group(2)
            title_match = re.search(r'(CEO|CFO|CMO|President|Chief\s+\w+\s+Officer)', match.group(0))
            if name and title_match:
                info['executives'].append({
                    'name': name.strip(),
                    'title': title_match.group(1)
                })
        
        # Extract promises from quotes
        quote_pattern = r'"([^"]+)"'
        for quote in re.findall(quote_pattern, article.content):
            if any(word in quote.lower() for word in ['expect', 'anticipate', 'plan', 'will', 'target']):
                info['promises'].append(quote)
        
        # Extract FDA mentions
        fda_pattern = r'(FDA|PDUFA|NDA|BLA|IND|510k|PMA)\s+[^.]*\.'
        info['fda_mentions'] = re.findall(fda_pattern, article.content, re.IGNORECASE)
        
        return info
    
    def _analyze_management_credibility(self, article: NewsArticle, 
                                      company_info: Dict) -> Dict:
        """Analyze management credibility based on the news"""
        credibility_analysis = {
            'executives_analyzed': [],
            'new_promises': [],
            'promise_updates': [],
            'credibility_impact': None,
            'red_flags': []
        }
        
        # Check each executive mentioned
        for exec in company_info['executives']:
            exec_credibility = self.truth_tracker.get_executive_credibility(
                exec['name'], company_info['company']
            )
            
            if exec_credibility:
                credibility_analysis['executives_analyzed'].append({
                    'name': exec['name'],
                    'title': exec['title'],
                    'credibility_score': exec_credibility['credibility_score'],
                    'track_record': f"{exec_credibility['delivered_on_time']}/{exec_credibility['total_promises']} promises delivered on time",
                    'average_delay': exec_credibility.get('average_delay_days', 0)
                })
                
                # Red flags
                if exec_credibility['credibility_score'] < 0.5:
                    credibility_analysis['red_flags'].append(
                        f"⚠️ {exec['name']} has low credibility score ({exec_credibility['credibility_score']:.2f})"
                    )
                
                if exec_credibility.get('failed', 0) > exec_credibility.get('delivered_on_time', 0):
                    credibility_analysis['red_flags'].append(
                        f"🚨 {exec['name']} has more failed promises than successes"
                    )
        
        # Extract and track new promises
        for promise_text in company_info['promises']:
            promises = self.truth_tracker.extract_promise_from_text(
                promise_text,
                company_info['company'],
                company_info['executives'][0]['name'] if company_info['executives'] else 'Unknown',
                company_info['executives'][0]['title'] if company_info['executives'] else 'Executive',
                article.url,
                datetime.now()
            )
            
            for promise in promises:
                # Save the promise
                self.truth_tracker.save_promise(promise)
                credibility_analysis['new_promises'].append({
                    'type': promise.promise_type.value,
                    'deadline': promise.deadline.isoformat() if promise.deadline else 'No specific deadline',
                    'confidence': promise.confidence_language,
                    'text': promise.promise_text[:200] + '...' if len(promise.promise_text) > 200 else promise.promise_text
                })
        
        # Check if this news updates any existing promises
        credibility_analysis['promise_updates'] = self._check_promise_updates(
            article, company_info
        )
        
        return credibility_analysis
    
    def _check_promise_updates(self, article: NewsArticle, 
                             company_info: Dict) -> List[Dict]:
        """Check if the news updates any existing promises"""
        updates = []
        
        # Keywords indicating promise fulfillment or failure
        fulfillment_keywords = ['completed', 'achieved', 'announced', 'received', 'filed', 'submitted']
        failure_keywords = ['delayed', 'postponed', 'failed', 'discontinued', 'terminated']
        
        content_lower = article.content.lower()
        
        # Check for fulfillment
        for keyword in fulfillment_keywords:
            if keyword in content_lower:
                # Look for what was completed
                context_start = max(0, content_lower.find(keyword) - 100)
                context_end = min(len(content_lower), content_lower.find(keyword) + 100)
                context = article.content[context_start:context_end]
                
                updates.append({
                    'type': 'potential_fulfillment',
                    'keyword': keyword,
                    'context': context,
                    'recommendation': 'Review and update relevant promises as DELIVERED'
                })
        
        # Check for delays/failures
        for keyword in failure_keywords:
            if keyword in content_lower:
                context_start = max(0, content_lower.find(keyword) - 100)
                context_end = min(len(content_lower), content_lower.find(keyword) + 100)
                context = article.content[context_start:context_end]
                
                updates.append({
                    'type': 'potential_failure',
                    'keyword': keyword,
                    'context': context,
                    'recommendation': 'Review and update relevant promises as DELAYED or FAILED'
                })
        
        return updates
    
    def _is_fda_related(self, article: NewsArticle) -> bool:
        """Check if article contains FDA-related content"""
        fda_keywords = [
            'FDA', 'PDUFA', 'NDA', 'BLA', 'IND', '510k', 'PMA',
            'approval', 'complete response letter', 'CRL',
            'clinical trial', 'Phase 1', 'Phase 2', 'Phase 3',
            'advisory committee', 'AdCom'
        ]
        
        content_lower = article.content.lower()
        return any(keyword.lower() in content_lower for keyword in fda_keywords)
    
    def _analyze_fda_implications(self, article: NewsArticle, 
                                company_info: Dict) -> Dict:
        """Analyze FDA implications from the news"""
        fda_analysis = {
            'submission_detected': False,
            'submission_analysis': None,
            'timeline_implications': None,
            'regulatory_risks': [],
            'precedent_insights': []
        }
        
        # Check for FDA submission announcement
        submission_patterns = [
            r'submitted?\s+(?:an?\s+)?(?:NDA|BLA|IND|510k|PMA)',
            r'filing\s+(?:of\s+)?(?:an?\s+)?(?:NDA|BLA|IND|510k|PMA)',
            r'(?:NDA|BLA|IND|510k|PMA)\s+submission',
            r'PDUFA\s+date\s+(?:of|set\s+for)\s+([^,.]+)'
        ]
        
        content = article.content
        for pattern in submission_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fda_analysis['submission_detected'] = True
                
                # Create FDA submission object for analysis
                submission = self._create_fda_submission_from_news(
                    article, company_info, match
                )
                
                if submission:
                    # Analyze the submission
                    analysis = self.fda_analyzer.analyze_submission(submission)
                    fda_analysis['submission_analysis'] = analysis
                    
                    # Extract key insights
                    fda_analysis['timeline_implications'] = {
                        'expected_decision': analysis['timeline_prediction'],
                        'adcom_likely': analysis['advisory_committee_prediction']['adcom_required_probability'] > 0.7
                    }
                    
                    fda_analysis['regulatory_risks'] = analysis['key_risk_factors']
                    
                    # Add precedent insights
                    if analysis['similar_precedents']:
                        fda_analysis['precedent_insights'] = [
                            f"{p['drug']} ({p['company']}): {p['outcome']} - similarity: {p['similarity_score']:.2f}"
                            for p in analysis['similar_precedents'][:3]
                        ]
                
                break
        
        # Check for FDA decision announcements
        decision_patterns = [
            r'FDA\s+approved',
            r'received?\s+(?:FDA\s+)?approval',
            r'complete\s+response\s+letter',
            r'CRL\s+from\s+(?:the\s+)?FDA'
        ]
        
        for pattern in decision_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                fda_analysis['regulatory_risks'].append(
                    "FDA decision announced - verify promise fulfillment and timeline accuracy"
                )
        
        return fda_analysis
    
    def _create_fda_submission_from_news(self, article: NewsArticle,
                                       company_info: Dict,
                                       match) -> Optional[FDASubmission]:
        """Create FDA submission object from news content"""
        try:
            # Extract drug name
            drug_pattern = r'(?:for\s+)?([A-Z][a-z]+(?:-[a-z]+)?)\s+(?:for|in)\s+'
            drug_match = re.search(drug_pattern, article.content)
            drug_name = drug_match.group(1) if drug_match else "Unknown Drug"
            
            # Extract indication
            indication_pattern = r'(?:for|in)\s+(?:the\s+)?(?:treatment\s+of\s+)?([^,.\n]+)'
            indication_match = re.search(indication_pattern, article.content[match.end():match.end()+200])
            indication = indication_match.group(1).strip() if indication_match else "Unknown Indication"
            
            # Determine drug type (simplified)
            drug_type = DrugType.SMALL_MOLECULE  # Default
            if any(word in article.content.lower() for word in ['antibody', 'mab']):
                drug_type = DrugType.MONOCLONAL_ANTIBODY
            elif any(word in article.content.lower() for word in ['gene therapy', 'gene-therapy']):
                drug_type = DrugType.GENE_THERAPY
            elif any(word in article.content.lower() for word in ['cell therapy', 'car-t']):
                drug_type = DrugType.CELL_THERAPY
            
            # Determine review division
            division = FDAReviewDivision.ONCOLOGY  # Default
            indication_lower = indication.lower()
            for ind_key, div in self.fda_analyzer.indication_mappings.items():
                if ind_key in indication_lower:
                    division = div
                    break
            
            # Extract review pathways
            pathways = []
            if 'breakthrough' in article.content.lower():
                pathways.append(ReviewPathway.BREAKTHROUGH)
            if 'fast track' in article.content.lower():
                pathways.append(ReviewPathway.FAST_TRACK)
            if 'priority review' in article.content.lower():
                pathways.append(ReviewPathway.PRIORITY)
            if 'orphan' in article.content.lower():
                pathways.append(ReviewPathway.ORPHAN)
            
            # Extract PDUFA date if mentioned
            pdufa_pattern = r'PDUFA\s+date\s+(?:of|set\s+for|is)\s+([^,.]+)'
            pdufa_match = re.search(pdufa_pattern, article.content, re.IGNORECASE)
            pdufa_date = None
            if pdufa_match:
                # Try to parse the date
                date_str = pdufa_match.group(1).strip()
                # Simplified date parsing - would be more robust in production
                try:
                    # Try different date formats
                    for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y']:
                        try:
                            pdufa_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                except:
                    pass
            
            # Create submission object
            submission = FDASubmission(
                company_name=company_info['company'],
                drug_name=drug_name,
                drug_type=drug_type,
                indication=indication,
                review_division=division,
                review_pathway=pathways[0] if pathways else ReviewPathway.STANDARD,
                submission_date=datetime.now(),
                # Optional fields with sensible defaults
                submission_type='NDA' if 'nda' in match.group(0).lower() else 'BLA',
                pdufa_date=pdufa_date,
                has_breakthrough_designation=ReviewPathway.BREAKTHROUGH in pathways,
                has_orphan_designation=ReviewPathway.ORPHAN in pathways,
                has_fast_track=ReviewPathway.FAST_TRACK in pathways,
                primary_endpoint="Not specified in news",
                primary_endpoint_met=False,  # Unknown from news
                safety_profile_grade=3,  # Neutral default
                patient_population_size=0,
                unmet_medical_need=True if 'orphan' in article.content.lower() else False,
                competing_drugs=[],
                pivotal_trial_size=0
            )
            
            return submission
            
        except Exception as e:
            logger.error(f"Error creating FDA submission from news: {e}")
            return None
    
    def _generate_integrated_insights(self, analysis: Dict,
                                    article: NewsArticle,
                                    company_info: Dict) -> List[str]:
        """Generate integrated insights from all analyses"""
        insights = []
        
        # Management credibility insights
        if analysis['management_credibility']:
            cred = analysis['management_credibility']
            
            if cred['executives_analyzed']:
                for exec in cred['executives_analyzed']:
                    if exec['credibility_score'] < 0.5:
                        insights.append(
                            f"🚨 CREDIBILITY WARNING: {exec['name']} has only delivered "
                            f"{exec['track_record']} with avg delay of {exec['average_delay']} days"
                        )
                    elif exec['credibility_score'] > 0.8:
                        insights.append(
                            f"✅ CREDIBILITY STRENGTH: {exec['name']} has strong track record - "
                            f"{exec['track_record']}"
                        )
            
            if cred['new_promises']:
                high_confidence_promises = [p for p in cred['new_promises'] 
                                          if p['confidence'] in ['very_confident', 'confident']]
                if high_confidence_promises:
                    insights.append(
                        f"📌 NEW PROMISES: {len(high_confidence_promises)} high-confidence commitments made"
                    )
        
        # FDA insights
        if analysis['fda_implications'] and analysis['fda_implications']['submission_analysis']:
            fda = analysis['fda_implications']['submission_analysis']
            
            prob = fda['approval_probability']
            if prob >= 0.7:
                insights.append(
                    f"✅ FDA OUTLOOK: High approval probability ({prob:.1%}) - "
                    f"prepare for commercial launch"
                )
            elif prob >= 0.4:
                insights.append(
                    f"⚠️ FDA RISK: Moderate approval probability ({prob:.1%}) - "
                    f"CRL risk is significant"
                )
            else:
                insights.append(
                    f"🚨 FDA CONCERN: Low approval probability ({prob:.1%}) - "
                    f"consider strategic alternatives"
                )
            
            # Timeline insights
            if analysis['fda_implications']['timeline_implications']['adcom_likely']:
                insights.append(
                    "📅 TIMELINE: Advisory Committee likely - add 2-3 months to timeline"
                )
        
        # Pattern recognition
        if company_info['company'] in self.company_intelligence:
            intel = self.company_intelligence[company_info['company']]
            if intel.get('pattern_detected'):
                insights.append(
                    f"📊 PATTERN: {intel['pattern_description']}"
                )
        
        return insights
    
    def _generate_investment_alerts(self, analysis: Dict,
                                  company_info: Dict) -> List[str]:
        """Generate actionable investment alerts"""
        alerts = []
        
        # Critical credibility alerts
        if analysis['management_credibility'] and analysis['management_credibility']['red_flags']:
            for flag in analysis['management_credibility']['red_flags']:
                alerts.append({
                    'level': 'HIGH',
                    'type': 'CREDIBILITY',
                    'message': flag,
                    'action': 'Review position sizing given management credibility concerns'
                })
        
        # FDA decision alerts
        if analysis['fda_implications'] and analysis['fda_implications']['submission_analysis']:
            fda = analysis['fda_implications']['submission_analysis']
            
            if fda['approval_probability'] < 0.4:
                alerts.append({
                    'level': 'HIGH',
                    'type': 'REGULATORY',
                    'message': f"FDA approval unlikely ({fda['approval_probability']:.1%})",
                    'action': 'Consider reducing exposure before PDUFA date'
                })
            
            if fda['timeline_prediction']['extension_probability'] > 0.7:
                alerts.append({
                    'level': 'MEDIUM',
                    'type': 'TIMELINE',
                    'message': f"PDUFA extension likely ({fda['timeline_prediction']['extension_probability']:.1%})",
                    'action': 'Adjust option strategies for extended timeline'
                })
        
        # Promise deadline alerts
        if analysis['management_credibility'] and analysis['management_credibility']['new_promises']:
            for promise in analysis['management_credibility']['new_promises']:
                if promise['deadline'] != 'No specific deadline':
                    deadline = datetime.fromisoformat(promise['deadline'])
                    days_until = (deadline - datetime.now()).days
                    
                    if days_until <= 30:
                        alerts.append({
                            'level': 'MEDIUM',
                            'type': 'CATALYST',
                            'message': f"{promise['type']} deadline in {days_until} days",
                            'action': 'Monitor for pre-announcement volatility'
                        })
        
        return alerts
    
    def _generate_action_items(self, analysis: Dict,
                             company_info: Dict) -> List[str]:
        """Generate specific action items for investors"""
        actions = []
        
        # Based on management credibility
        if analysis['management_credibility']:
            if any(exec['credibility_score'] < 0.5 
                   for exec in analysis['management_credibility']['executives_analyzed']):
                actions.append(
                    "📋 Set calendar reminders for all promise deadlines - management has poor delivery record"
                )
                actions.append(
                    "📋 Consider buying puts or reducing position size ahead of key deadlines"
                )
        
        # Based on FDA analysis
        if analysis['fda_implications'] and analysis['fda_implications']['submission_analysis']:
            fda = analysis['fda_implications']['submission_analysis']
            
            if fda['advisory_committee_prediction']['adcom_required_probability'] > 0.7:
                actions.append(
                    "📋 Research Advisory Committee members and their voting history"
                )
                actions.append(
                    "📋 Monitor for AdCom briefing documents (released 2 days before meeting)"
                )
            
            for rec in fda['recommendations'][:3]:  # Top 3 recommendations
                actions.append(f"📋 {rec}")
        
        # Based on promise updates
        if (analysis['management_credibility'] and 
            analysis['management_credibility']['promise_updates']):
            for update in analysis['management_credibility']['promise_updates']:
                actions.append(
                    f"📋 {update['recommendation']}: {update['type']} detected"
                )
        
        # Pattern-based actions
        if 'conference' in analysis['article']['title'].lower():
            actions.append(
                "📋 Check for presentation slides/posters on company website"
            )
            actions.append(
                "📋 Monitor for peer company presentations at same conference"
            )
        
        return actions
    
    def generate_comprehensive_report(self, articles: List[NewsArticle]) -> Dict:
        """Generate comprehensive report with all intelligence integrated"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'articles_analyzed': len(articles),
            'companies_covered': set(),
            'high_priority_alerts': [],
            'credibility_warnings': [],
            'fda_calendar': [],
            'promise_calendar': [],
            'investment_themes': [],
            'detailed_analyses': []
        }
        
        # Analyze each article
        for article in articles:
            analysis = self.analyze_news_with_intelligence(article)
            report['detailed_analyses'].append(analysis)
            report['companies_covered'].add(article.company_name or 'Unknown')
            
            # Aggregate alerts
            for alert in analysis['investment_alerts']:
                if isinstance(alert, dict) and alert.get('level') == 'HIGH':
                                    report['high_priority_alerts'].append({
                    'company': article.company_name or 'Unknown',
                    'alert': alert
                })
            
            # Aggregate credibility warnings
            if analysis['management_credibility'] and analysis['management_credibility']['red_flags']:
                report['credibility_warnings'].extend([
                    {'company': article.company_name or 'Unknown', 'warning': flag}
                    for flag in analysis['management_credibility']['red_flags']
                ])
            
            # Build FDA calendar
            if analysis['fda_implications'] and analysis['fda_implications']['submission_detected']:
                timeline = analysis['fda_implications'].get('timeline_implications', {})
                if timeline:
                    report['fda_calendar'].append({
                        'company': article.company_name or 'Unknown',
                        'expected_decision': timeline.get('expected_decision'),
                        'adcom_likely': timeline.get('adcom_likely', False)
                    })
            
            # Build promise calendar
            if analysis['management_credibility'] and analysis['management_credibility']['new_promises']:
                for promise in analysis['management_credibility']['new_promises']:
                    if promise['deadline'] != 'No specific deadline':
                        report['promise_calendar'].append({
                            'company': article.company_name or 'Unknown',
                            'promise_type': promise['type'],
                            'deadline': promise['deadline'],
                            'confidence': promise['confidence']
                        })
        
        # Sort calendars by date
        report['fda_calendar'].sort(key=lambda x: x.get('expected_decision', {}).get('expected_review_days', 999))
        report['promise_calendar'].sort(key=lambda x: x['deadline'])
        
        # Identify investment themes
        report['investment_themes'] = self._identify_investment_themes(report)
        
        return report
    
    def _identify_investment_themes(self, report: Dict) -> List[str]:
        """Identify overarching investment themes from the analysis"""
        themes = []
        
        # Theme: Management credibility crisis
        if len(report['credibility_warnings']) >= 3:
            themes.append(
                "🎯 THEME: Multiple companies showing management credibility issues - "
                "favor companies with proven execution track records"
            )
        
        # Theme: FDA decision cluster
        if len(report['fda_calendar']) >= 3:
            upcoming_decisions = [item for item in report['fda_calendar'] 
                                if item.get('expected_decision', {}).get('expected_review_days', 999) < 180]
            if upcoming_decisions:
                themes.append(
                    f"🎯 THEME: {len(upcoming_decisions)} FDA decisions expected within 6 months - "
                    "increase hedging ahead of binary events"
                )
        
        # Theme: Promise deadline cluster
        promise_cluster = defaultdict(int)
        for promise in report['promise_calendar']:
            deadline = datetime.fromisoformat(promise['deadline'])
            month_key = deadline.strftime('%Y-%m')
            promise_cluster[month_key] += 1
        
        for month, count in promise_cluster.items():
            if count >= 3:
                themes.append(
                    f"🎯 THEME: {count} promise deadlines in {month} - "
                    "expect increased volatility and potential catalyst cluster"
                )
        
        return themes


# Usage example
if __name__ == "__main__":
    # Initialize the integrated system
    intel_system = IntegratedIntelligenceSystem()
    
    # Example: Analyze a news article
    sample_article = NewsArticle(
        title="BioTech Corp Announces FDA Submission for Novel Cancer Drug",
        company_name="BioTech Corp",
        published_date=datetime(2024, 1, 15),
        content="""
        BioTech Corp CEO John Smith announced today that the company has submitted 
        a New Drug Application (NDA) to the FDA for BTK-123, its novel cancer treatment 
        for non-small cell lung cancer. "We are highly confident in our data and expect 
        approval by Q3 2024," said Smith. The company received Breakthrough Therapy 
        designation last year. The PDUFA date is set for September 15, 2024.
        
        In the pivotal Phase 3 trial, BTK-123 demonstrated a 45% improvement in 
        progression-free survival compared to standard of care. The safety profile 
        showed a 15% serious adverse event rate, with 2% treatment-related deaths.
        
        Smith also noted that enrollment for their Phase 2 Alzheimer's trial is 
        "on track to complete by June 2024" and data readout is expected in Q4 2024.
        """,
        url="https://example.com/article1"
    )
    
    # Analyze the article
    analysis = intel_system.analyze_news_with_intelligence(sample_article)
    
    # Print insights
    print(json.dumps(analysis, indent=2, default=str)) 