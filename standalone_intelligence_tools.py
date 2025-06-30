#!/usr/bin/env python3
"""
Standalone Intelligence Testing Tools
Test Management Truth Tracker™ and FDA Decision Analyzer outside of reports

This tool allows you to test the accuracy and functionality of:
1. Management Truth Tracker™ - Test executive promise tracking
2. FDA Decision Analyzer - Test FDA approval predictions  
3. Combined Intelligence Analysis - Test both systems together

Usage:
python standalone_intelligence_tools.py --help
"""
import sys
import os
from datetime import datetime, timedelta
import argparse
from typing import List, Dict, Optional
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from management_truth_tracker import ManagementTruthTracker, PromiseType, PromiseStatus
from fda_decision_analyzer import FDADecisionAnalyzer, FDASubmission, DrugType, FDAReviewDivision, ReviewPathway


class StandaloneIntelligenceTester:
    """
    Standalone testing interface for intelligence features
    Allows testing accuracy and functionality outside of daily reports
    """
    
    def __init__(self):
        print("🔧 Initializing Intelligence Systems...")
        self.truth_tracker = ManagementTruthTracker()
        self.fda_analyzer = FDADecisionAnalyzer()
        print("✅ Intelligence Systems Ready!")
    
    def test_management_tracker(self, text_input: str = None):
        """Test Management Truth Tracker with custom text or demo data"""
        print("\n🎯 MANAGEMENT TRUTH TRACKER™ TESTING")
        print("=" * 50)
        
        if text_input:
            print(f"📝 Analyzing input text for executive promises...")
            # Extract promises from the provided text
            promises = self.truth_tracker.extract_promises_from_text(text_input)
            
            if promises:
                print(f"✅ Found {len(promises)} potential promises:")
                for i, promise in enumerate(promises, 1):
                    print(f"\n{i}. Promise: {promise['promise_text']}")
                    print(f"   Executive: {promise.get('executive_name', 'Unknown')}")
                    print(f"   Type: {promise.get('promise_type', 'UNSPECIFIED')}")
                    print(f"   Timeline: {promise.get('timeline', 'Not specified')}")
            else:
                print("❌ No clear executive promises detected in text")
        
        # Show some existing data for testing
        print("\n📊 CURRENT PROMISE TRACKING STATUS:")
        
        # Get recent promises
        recent_promises = self.truth_tracker.get_promises_by_status(PromiseStatus.PENDING)
        if recent_promises:
            print(f"\n⏳ PENDING PROMISES ({len(recent_promises)}):")
            for promise in recent_promises[:5]:  # Show first 5
                print(f"• {promise['promise_text'][:80]}...")
                print(f"  Executive: {promise['executive_name']} | Due: {promise.get('expected_date', 'TBD')}")
        
        # Get failed promises for credibility analysis
        failed_promises = self.truth_tracker.get_promises_by_status(PromiseStatus.BROKEN)
        if failed_promises:
            print(f"\n❌ FAILED PROMISES ({len(failed_promises)}):")
            for promise in failed_promises[:3]:  # Show first 3
                print(f"• {promise['promise_text'][:80]}...")
                print(f"  Executive: {promise['executive_name']} | Failed: {promise.get('outcome_date', 'Unknown')}")
        
        # Show credibility scores for top executives
        print("\n🎭 EXECUTIVE CREDIBILITY ANALYSIS:")
        all_executives = self.truth_tracker.get_all_executives()
        if all_executives:
            for exec_name in list(all_executives.keys())[:5]:  # Top 5 executives
                credibility = self.truth_tracker.calculate_credibility_score(exec_name)
                score = credibility.get('overall_score', 0)
                status = "🟢 HIGH" if score >= 75 else "🟡 MEDIUM" if score >= 50 else "🔴 LOW"
                print(f"• {exec_name}: {score:.1f}% {status}")
        
        return True
    
    def test_fda_analyzer(self, drug_name: str = None, company_name: str = None):
        """Test FDA Decision Analyzer with specific drug/company or demo data"""
        print("\n🏛️ FDA DECISION ANALYZER TESTING")
        print("=" * 50)
        
        if drug_name or company_name:
            print(f"🔍 Analyzing FDA prospects for: {drug_name or company_name}")
            
            # Create a test submission for analysis
            test_submission = FDASubmission(
                drug_name=drug_name or f"{company_name} Drug Candidate",
                company_name=company_name or "Test Company",
                indication="Test Indication",
                drug_type=DrugType.SMALL_MOLECULE,
                review_division=FDAReviewDivision.ONCOLOGY,
                review_pathway=ReviewPathway.STANDARD
            )
            
            # Analyze approval probability
            analysis = self.fda_analyzer.predict_approval_probability(test_submission)
            
            print(f"\n📊 FDA APPROVAL ANALYSIS:")
            print(f"Overall Probability: {analysis['overall_probability']:.1f}%")
            print(f"Confidence Level: {analysis['confidence_level']}")
            
            print(f"\n📈 SCORING BREAKDOWN:")
            for factor, score in analysis['scoring_breakdown'].items():
                print(f"• {factor.replace('_', ' ').title()}: {score:.1f}/100")
            
            if analysis.get('similar_precedents'):
                print(f"\n🔍 SIMILAR PRECEDENTS FOUND: {len(analysis['similar_precedents'])}")
                for precedent in analysis['similar_precedents'][:3]:
                    print(f"• {precedent['drug_name']} ({precedent['company_name']}) - {precedent['outcome']}")
        
        # Show current FDA analysis statistics
        print("\n📊 FDA DATABASE STATISTICS:")
        stats = self.fda_analyzer.get_database_stats()
        print(f"• Total submissions tracked: {stats.get('total_submissions', 0)}")
        print(f"• Approval rate (last 5 years): {stats.get('recent_approval_rate', 0):.1f}%")
        print(f"• Average review time: {stats.get('avg_review_time', 0):.1f} months")
        
        # Show recent approvals/rejections for pattern analysis
        recent_decisions = self.fda_analyzer.get_recent_decisions(limit=5)
        if recent_decisions:
            print(f"\n🗓️ RECENT FDA DECISIONS:")
            for decision in recent_decisions:
                outcome_icon = "✅" if decision['outcome'] == 'Approved' else "❌"
                print(f"{outcome_icon} {decision['drug_name']} - {decision['outcome']} ({decision.get('decision_date', 'Unknown date')})")
        
        return True
    
    def test_combined_intelligence(self, news_text: str):
        """Test combined intelligence analysis on a news article"""
        print("\n🧠 COMBINED INTELLIGENCE ANALYSIS")
        print("=" * 50)
        
        print("📰 Analyzing news text for both promises and FDA implications...")
        
        # 1. Extract management promises
        promises = self.truth_tracker.extract_promises_from_text(news_text)
        
        # 2. Look for FDA-related content
        fda_signals = self._extract_fda_signals(news_text)
        
        print(f"\n🎯 Management Truth Tracker Results:")
        if promises:
            print(f"✅ Detected {len(promises)} executive promises")
            for promise in promises:
                print(f"• {promise['promise_text'][:100]}...")
        else:
            print("❌ No executive promises detected")
        
        print(f"\n🏛️ FDA Decision Analyzer Results:")
        if fda_signals:
            print(f"✅ Detected {len(fda_signals)} FDA-related signals")
            for signal in fda_signals:
                print(f"• Type: {signal['type']} | Context: {signal['context'][:80]}...")
        else:
            print("❌ No significant FDA signals detected")
        
        # 3. Generate combined insights
        insights = self._generate_combined_insights(promises, fda_signals, news_text)
        
        if insights:
            print(f"\n💡 COMBINED INTELLIGENCE INSIGHTS:")
            for insight in insights:
                print(f"• {insight}")
        
        return {
            'promises': promises,
            'fda_signals': fda_signals,
            'insights': insights
        }
    
    def _extract_fda_signals(self, text: str) -> List[Dict]:
        """Extract FDA-related signals from text"""
        fda_keywords = {
            'submission': ['BLA', 'NDA', 'IND', 'submission', 'application'],
            'meeting': ['FDA meeting', 'advisory committee', 'PDUFA', 'breakthrough'],
            'approval': ['approved', 'approval', 'cleared', 'granted'],
            'rejection': ['rejected', 'CRL', 'complete response letter', 'denied'],
            'trial': ['Phase I', 'Phase II', 'Phase III', 'clinical trial', 'pivotal study']
        }
        
        signals = []
        text_lower = text.lower()
        
        for signal_type, keywords in fda_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Find context around the keyword
                    start_idx = text_lower.find(keyword.lower())
                    context_start = max(0, start_idx - 100)
                    context_end = min(len(text), start_idx + 200)
                    context = text[context_start:context_end]
                    
                    signals.append({
                        'type': signal_type,
                        'keyword': keyword,
                        'context': context
                    })
        
        return signals
    
    def _generate_combined_insights(self, promises: List[Dict], fda_signals: List[Dict], text: str) -> List[str]:
        """Generate insights from combined analysis"""
        insights = []
        
        # Check for promise-FDA alignment
        if promises and fda_signals:
            insights.append("🔗 Executive promises detected alongside FDA activity - track promise fulfillment against regulatory outcomes")
        
        # Check for credibility implications
        if promises:
            insights.append(f"📊 {len(promises)} new promises to track - will impact executive credibility scores")
        
        # Check for FDA prediction opportunities
        if fda_signals:
            trial_signals = [s for s in fda_signals if s['type'] == 'trial']
            if trial_signals:
                insights.append(f"🎯 {len(trial_signals)} clinical trial references detected - opportunity for FDA approval prediction")
        
        # Look for timeline commitments
        timeline_words = ['by', 'within', 'expected', 'anticipate', 'plan to', 'will complete']
        if any(word in text.lower() for word in timeline_words):
            insights.append("⏰ Timeline commitments detected - set up automated tracking for promise fulfillment")
        
        return insights
    
    def run_accuracy_test(self):
        """Run comprehensive accuracy tests on both systems"""
        print("\n🎯 COMPREHENSIVE ACCURACY TESTING")
        print("=" * 50)
        
        # Test known scenarios with expected outcomes
        test_cases = [
            {
                'text': "CEO John Smith announced that we expect to complete Phase III trials by Q4 2024 and submit our NDA in early 2025.",
                'expected_promises': 2,
                'expected_fda_signals': 2
            },
            {
                'text': "The FDA granted Breakthrough Therapy designation for our lead compound targeting rare disease patients.",
                'expected_promises': 0,
                'expected_fda_signals': 1
            },
            {
                'text': "Management confirmed they will deliver 50% revenue growth this year and expects regulatory approval within 18 months.",
                'expected_promises': 2,
                'expected_fda_signals': 1
            }
        ]
        
        accuracy_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}:")
            print(f"Text: {test_case['text']}")
            
            result = self.test_combined_intelligence(test_case['text'])
            
            promise_accuracy = len(result['promises']) == test_case['expected_promises']
            fda_accuracy = len(result['fda_signals']) == test_case['expected_fda_signals']
            
            print(f"✅ Promise Detection: {'PASS' if promise_accuracy else 'FAIL'} ({len(result['promises'])}/{test_case['expected_promises']})")
            print(f"✅ FDA Signal Detection: {'PASS' if fda_accuracy else 'FAIL'} ({len(result['fda_signals'])}/{test_case['expected_fda_signals']})")
            
            accuracy_results.append({
                'test_case': i,
                'promise_accuracy': promise_accuracy,
                'fda_accuracy': fda_accuracy
            })
        
        # Calculate overall accuracy
        promise_accuracy = sum(1 for r in accuracy_results if r['promise_accuracy']) / len(accuracy_results) * 100
        fda_accuracy = sum(1 for r in accuracy_results if r['fda_accuracy']) / len(accuracy_results) * 100
        
        print(f"\n📊 OVERALL ACCURACY RESULTS:")
        print(f"• Management Promise Detection: {promise_accuracy:.1f}%")
        print(f"• FDA Signal Detection: {fda_accuracy:.1f}%")
        print(f"• Combined System Accuracy: {(promise_accuracy + fda_accuracy) / 2:.1f}%")
        
        return accuracy_results
    
    def interactive_mode(self):
        """Run interactive testing mode"""
        print("\n🎮 INTERACTIVE TESTING MODE")
        print("=" * 50)
        print("Enter your own text to test the intelligence systems!")
        print("Commands: 'quit' to exit, 'demo' for demo data, 'accuracy' for accuracy test")
        
        while True:
            print("\n" + "─" * 50)
            user_input = input("Enter text to analyze (or command): ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'demo':
                demo_text = """
                CEO Sarah Johnson announced that we expect to file our BLA by the end of Q3 2024. 
                She confirmed the company will achieve $100M in revenue this year and anticipates 
                FDA approval for our lead drug by mid-2025. The Phase III trial enrolled 450 patients 
                and showed a 75% response rate with statistical significance of p<0.001.
                """
                self.test_combined_intelligence(demo_text)
            elif user_input.lower() == 'accuracy':
                self.run_accuracy_test()
            elif user_input:
                self.test_combined_intelligence(user_input)
            else:
                print("Please enter some text to analyze or a command.")


def main():
    """Main function to run standalone intelligence testing"""
    parser = argparse.ArgumentParser(description='Test Healthcare Intelligence Systems')
    parser.add_argument('--mode', choices=['tracker', 'fda', 'combined', 'accuracy', 'interactive'], 
                       default='interactive', help='Testing mode')
    parser.add_argument('--text', type=str, help='Text to analyze')
    parser.add_argument('--drug', type=str, help='Drug name for FDA analysis')
    parser.add_argument('--company', type=str, help='Company name for analysis')
    
    args = parser.parse_args()
    
    print("🚀 Healthcare Investment Intelligence - Standalone Testing")
    print("=" * 60)
    
    tester = StandaloneIntelligenceTester()
    
    if args.mode == 'tracker':
        tester.test_management_tracker(args.text)
    elif args.mode == 'fda':
        tester.test_fda_analyzer(args.drug, args.company)
    elif args.mode == 'combined':
        if args.text:
            tester.test_combined_intelligence(args.text)
        else:
            print("❌ Combined mode requires --text parameter")
    elif args.mode == 'accuracy':
        tester.run_accuracy_test()
    elif args.mode == 'interactive':
        tester.interactive_mode()
    
    print("\n✅ Testing complete!")


if __name__ == '__main__':
    main() 