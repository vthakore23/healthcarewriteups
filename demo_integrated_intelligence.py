#!/usr/bin/env python3
"""
Demo script for the Integrated Healthcare Investment Intelligence System
Shows Management Truth Tracker and FDA Decision Analyzer in action
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Import our intelligence systems
from integrated_intelligence_system import IntegratedIntelligenceSystem
from management_truth_tracker import ManagementTruthTracker, PromiseType, PromiseStatus
from fda_decision_analyzer import (
    FDADecisionAnalyzer, FDASubmission, DrugType, 
    FDAReviewDivision, ReviewPathway, FDADecisionType
)
from scraper_optimized import NewsArticle

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def demo_management_truth_tracker():
    """Demonstrate the Management Truth Tracker with real scenarios"""
    print_section("🕵️ MANAGEMENT TRUTH TRACKER™ DEMO")
    
    tracker = ManagementTruthTracker()
    
    # Example 1: A biotech CEO making promises
    print("\n📰 Scenario 1: CEO Makes Bold Promises About FDA Submission")
    print("-" * 60)
    
    promise_1 = tracker.track_promise(
        executive_name="John Smith",
        executive_title="CEO",
        company_name="BioPharma Inc",
        promise_text="We expect to submit our NDA for XYZ-123 to the FDA by Q3 2024",
        promise_type=PromiseType.FDA_SUBMISSION,
        promise_date=datetime(2024, 1, 15),
        deadline_date=datetime(2024, 9, 30),
        source_url="https://example.com/news/1",
        confidence_language="expect to"
    )
    
    print(f"✅ Promise tracked: ID {promise_1}")
    print(f"   Executive: John Smith (CEO)")
    print(f"   Promise: FDA submission by Q3 2024")
    print(f"   Confidence: 'expect to' (moderate confidence)")
    
    # Example 2: Same CEO making another promise
    promise_2 = tracker.track_promise(
        executive_name="John Smith",
        executive_title="CEO",
        company_name="BioPharma Inc",
        promise_text="Our Phase 3 data readout will definitely be completed by June 2024",
        promise_type=PromiseType.DATA_READOUT,
        promise_date=datetime(2024, 2, 1),
        deadline_date=datetime(2024, 6, 30),
        source_url="https://example.com/news/2",
        confidence_language="will definitely"
    )
    
    print(f"\n✅ Another promise tracked: ID {promise_2}")
    print(f"   Promise: Phase 3 data by June 2024")
    print(f"   Confidence: 'will definitely' (high confidence)")
    
    # Example 3: Update promise status - one failed
    print("\n\n📅 Fast forward to July 2024...")
    print("-" * 60)
    
    tracker.update_promise_status(
        promise_id=promise_2,
        status=PromiseStatus.FAILED,
        outcome_date=datetime(2024, 7, 15),
        outcome_details="Company announced 2-month delay in data readout"
    )
    
    print("❌ Promise FAILED: Phase 3 data was delayed")
    
    # Get credibility analysis
    print("\n\n📊 Credibility Analysis for John Smith")
    print("-" * 60)
    
    credibility = tracker.get_executive_credibility("John Smith", "BioPharma Inc")
    
    print(f"Credibility Score: {credibility['credibility_score']:.0%}")
    print(f"Total Promises: {credibility['total_promises']}")
    print(f"Delivered: {credibility['delivered']}")
    print(f"Failed: {credibility['failed']}")
    print(f"Average Delay: {credibility['average_delay_days']} days")
    
    # Example 4: Track promises from another executive
    print("\n\n📰 Scenario 2: CMO Makes Clinical Timeline Promise")
    print("-" * 60)
    
    promise_3 = tracker.track_promise(
        executive_name="Sarah Johnson",
        executive_title="CMO",
        company_name="BioPharma Inc",
        promise_text="We are on track to complete patient enrollment by end of Q2",
        promise_type=PromiseType.CLINICAL_TIMELINE,
        promise_date=datetime(2024, 3, 1),
        deadline_date=datetime(2024, 6, 30),
        source_url="https://example.com/news/3",
        confidence_language="on track"
    )
    
    # Update as delivered
    tracker.update_promise_status(
        promise_id=promise_3,
        status=PromiseStatus.DELIVERED_ON_TIME,
        outcome_date=datetime(2024, 6, 15),
        outcome_details="Enrollment completed ahead of schedule"
    )
    
    print("✅ CMO Sarah Johnson delivered on enrollment promise!")
    
    # Get company-wide analysis
    print("\n\n🏢 Company-Wide Credibility Analysis")
    print("-" * 60)
    
    company_cred = tracker.get_company_credibility("BioPharma Inc")
    
    print(f"Company Credibility Score: {company_cred['overall_credibility']:.0%}")
    print(f"Total Executives Tracked: {company_cred['total_executives']}")
    print("\nBreakdown by Promise Type:")
    promise_types = company_cred.get('by_promise_type', company_cred.get('promise_types_accuracy', {}))
    if promise_types:
        for ptype, stats in promise_types.items():
            if isinstance(stats, dict) and stats.get('total', 0) > 0:
                success_rate = stats.get('success_rate', 0)
                total = stats.get('total', 0)
                print(f"  {ptype}: {success_rate:.0%} success rate ({total} promises)")
            elif isinstance(stats, (int, float)):
                # Handle simple success rate format
                print(f"  {ptype}: {stats:.0%} success rate")

def demo_fda_decision_analyzer():
    """Demonstrate the FDA Decision Analyzer with real scenarios"""
    print_section("📊 FDA DECISION PATTERN ANALYZER DEMO")
    
    analyzer = FDADecisionAnalyzer()
    
    # Example 1: Analyze an oncology drug submission
    print("\n💊 Scenario 1: Novel Oncology Drug for Lung Cancer")
    print("-" * 60)
    
    submission_1 = FDASubmission(
        company_name="OncoTherapeutics",
        drug_name="Cancertrol",
        drug_type=DrugType.SMALL_MOLECULE,
        indication="Non-small cell lung cancer (2nd line)",
        review_division=FDAReviewDivision.ONCOLOGY,
        review_pathway=ReviewPathway.PRIORITY,
        submission_date=datetime(2024, 3, 15),
        has_breakthrough_designation=True,
        primary_endpoint="Overall survival",
        primary_endpoint_met=True,
        safety_profile_grade=4,  # Good safety
        patient_population_size=50000,
        unmet_medical_need=True,
        competing_drugs=["Keytruda", "Opdivo"],
        pivotal_trial_size=450
    )
    
    analysis_1 = analyzer.analyze_submission(submission_1)
    
    print(f"Drug: {submission_1.drug_name} for lung cancer")
    print(f"Approval Probability: {analysis_1['approval_probability']:.0%}")
    print(f"Predicted Outcome: {analysis_1['predicted_outcome'].value}")
    print(f"Expected Review Time: {analysis_1['timeline_prediction']['expected_review_days']} days")
    print(f"AdCom Likely: {'Yes' if analysis_1['adcom_probability'] > 0.5 else 'No'}")
    
    print("\nKey Factors:")
    for factor in analysis_1['key_factors'][:3]:
        print(f"  • {factor}")
    
    # Example 2: Analyze a rare disease drug
    print("\n\n💊 Scenario 2: Orphan Drug for Rare Genetic Disease")
    print("-" * 60)
    
    submission_2 = FDASubmission(
        company_name="RareGen Bio",
        drug_name="Genefixir",
        drug_type=DrugType.GENE_THERAPY,
        indication="Duchenne muscular dystrophy",
        review_division=FDAReviewDivision.NEUROLOGY,
        review_pathway=ReviewPathway.PRIORITY,
        submission_date=datetime(2024, 4, 1),
        has_orphan_designation=True,
        has_breakthrough_designation=True,
        primary_endpoint="6-minute walk test improvement",
        primary_endpoint_met=True,
        safety_profile_grade=3,  # Moderate safety concerns
        patient_population_size=500,
        unmet_medical_need=True,
        competing_drugs=[],
        pivotal_trial_size=45
    )
    
    analysis_2 = analyzer.analyze_submission(submission_2)
    
    print(f"Drug: {submission_2.drug_name} (Gene Therapy)")
    print(f"Approval Probability: {analysis_2['approval_probability']:.0%}")
    print(f"Predicted Outcome: {analysis_2['predicted_outcome'].value}")
    
    print("\nKey Risk Factors:")
    for risk in analysis_2['key_risk_factors'][:3]:
        print(f"  ⚠️  {risk}")
    
    # Example 3: Compare similar drugs
    print("\n\n📊 Historical Precedent Analysis")
    print("-" * 60)
    
    precedents = analyzer.find_precedents(submission_1)
    
    print(f"Found {len(precedents)} similar historical submissions:")
    for i, prec in enumerate(precedents[:3], 1):
        print(f"\n{i}. {prec['drug_name']} by {prec['company_name']}")
        print(f"   Similarity Score: {prec['similarity_score']:.0%}")
        print(f"   Outcome: {prec['decision_type']}")
        print(f"   Review Time: {prec['review_days']} days")

def demo_integrated_intelligence():
    """Demonstrate the integrated intelligence system"""
    print_section("🧬 INTEGRATED INTELLIGENCE SYSTEM DEMO")
    
    intel_system = IntegratedIntelligenceSystem()
    
    # Create a sample news article
    article = NewsArticle(
        title="BioPharma CEO Confident in Q3 FDA Submission for Lead Cancer Drug",
        url="https://example.com/news/biopharma-fda-submission",
        published_date=datetime.now(),
        content="""
        BioPharma Inc's CEO John Smith expressed strong confidence in the company's 
        timeline for their lead oncology candidate XYZ-123. "We are on track to submit 
        our NDA to the FDA by the end of Q3 2024," Smith stated during the earnings call.
        
        The drug showed a 35% improvement in overall survival in the Phase 3 STELLAR trial,
        with 450 patients enrolled. CMO Sarah Johnson added, "The safety profile has been 
        very manageable, with mostly grade 1-2 adverse events."
        
        XYZ-123 is targeting second-line non-small cell lung cancer, where current options
        include Keytruda and Opdivo. The company received Breakthrough Therapy designation
        last year and expects a priority review.
        
        "We believe XYZ-123 could be a game-changer for lung cancer patients," Smith 
        concluded. "Our manufacturing is ready, and we're prepared for a quick launch
        upon approval, which we anticipate by mid-2025."
        """,
        company_name="BioPharma Inc"
    )
    
    print("\n📰 Analyzing News Article:")
    print(f"Title: {article.title}")
    print(f"Company: {article.company_name}")
    
    # Run integrated analysis
    analysis = intel_system.analyze_news_with_intelligence(article)
    
    print("\n\n🔍 INTELLIGENCE ANALYSIS RESULTS")
    print("-" * 60)
    
    # Management credibility findings
    if analysis['management_credibility']:
        cred = analysis['management_credibility']
        print("\n👔 Management Credibility:")
        for exec in cred['executives_analyzed']:
            print(f"\n  {exec['name']} ({exec['title']})")
            print(f"  • Credibility Score: {exec['credibility_score']:.0%}")
            print(f"  • Track Record: {exec['track_record']}")
        
        if cred['new_promises']:
            print("\n  📝 New Promises Detected:")
            for promise in cred['new_promises']:
                print(f"    - {promise}")
    
    # FDA implications
    if analysis['fda_implications'] and analysis['fda_implications']['submission_analysis']:
        fda = analysis['fda_implications']['submission_analysis']
        print("\n\n🏛️ FDA Analysis:")
        print(f"  • Approval Probability: {fda['approval_probability']:.0%}")
        print(f"  • Expected Review: {fda['timeline_prediction']['expected_review_days']} days")
        print(f"  • AdCom Likely: {'Yes' if fda['adcom_probability'] > 0.5 else 'No'}")
    
    # Investment alerts
    if analysis['investment_alerts']:
        print("\n\n🚨 Investment Alerts:")
        for alert in analysis['investment_alerts']:
            if isinstance(alert, dict):
                print(f"  [{alert['level']}] {alert['message']}")
                print(f"         Action: {alert['action']}")
    
    # Generate comprehensive report
    print("\n\n📊 COMPREHENSIVE INTELLIGENCE REPORT")
    print("-" * 60)
    
    articles = [article]  # In real scenario, would have multiple articles
    report = intel_system.generate_comprehensive_report(articles)
    
    if report['high_priority_alerts']:
        print("\n🔴 High Priority Alerts:")
        for alert in report['high_priority_alerts']:
            print(f"  • {alert['company']}: {alert['alert']['message']}")
    
    if report['investment_themes']:
        print("\n🎯 Investment Themes Identified:")
        for theme in report['investment_themes']:
            print(f"  • {theme}")

def main():
    """Run all demos"""
    print("\n" + "🧬 "*20)
    print("HEALTHCARE INVESTMENT INTELLIGENCE SYSTEM")
    print("Demonstration of Core Features")
    print("🧬 "*20)
    
    # Run each demo
    demo_management_truth_tracker()
    input("\n\nPress Enter to continue to FDA Decision Analyzer demo...")
    
    demo_fda_decision_analyzer()
    input("\n\nPress Enter to continue to Integrated Intelligence demo...")
    
    demo_integrated_intelligence()
    
    print("\n\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nThese intelligence features provide:")
    print("  1. Accountability for executive promises")
    print("  2. Data-driven FDA approval predictions")
    print("  3. Integrated insights for smarter investment decisions")
    print("\nRun 'python main_enhanced_intelligence.py --run-now' to analyze real news!")

if __name__ == "__main__":
    main() 