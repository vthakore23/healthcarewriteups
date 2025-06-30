#!/usr/bin/env python3
"""
Populate sample data in FDA and Management databases for demonstration
"""
import sys
import os
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from management_truth_tracker import ManagementTruthTracker, PromiseType, PromiseStatus
from fda_decision_analyzer import FDADecisionAnalyzer, FDASubmission, DrugType, FDAReviewDivision, ReviewPathway


def populate_management_data():
    """Populate sample management promise data"""
    tracker = ManagementTruthTracker()
    
    # Moderna promises
    moderna_promises = [
        {
            "executive": "Stéphane Bancel",
            "title": "CEO",
            "company": "Moderna, Inc.",
            "promise": "We expect to report topline data from our Phase 3 RSV vaccine trial in Q1 2024",
            "type": PromiseType.DATA_READOUT,
            "date_made": datetime(2023, 11, 2),
            "deadline": datetime(2024, 3, 31),
            "source": "Q3 2023 Earnings Call",
            "confidence": "confident"
        },
        {
            "executive": "Stéphane Bancel",
            "title": "CEO", 
            "company": "Moderna, Inc.",
            "promise": "We plan to file for FDA approval of our next-gen COVID vaccine by mid-2024",
            "type": PromiseType.FDA_SUBMISSION,
            "date_made": datetime(2023, 9, 15),
            "deadline": datetime(2024, 6, 30),
            "source": "JP Morgan Healthcare Conference",
            "confidence": "on track"
        },
        {
            "executive": "Stephen Hoge",
            "title": "President",
            "company": "Moderna, Inc.",
            "promise": "We will complete enrollment for our personalized cancer vaccine trial by Q4 2023",
            "type": PromiseType.ENROLLMENT_COMPLETION,
            "date_made": datetime(2023, 6, 1),
            "deadline": datetime(2023, 12, 31),
            "source": "ASCO Conference Presentation",
            "confidence": "very confident"
        }
    ]
    
    # Add Moderna promises
    for p in moderna_promises:
        promise_id = tracker.track_promise(
            p["executive"], p["title"], p["company"], p["promise"],
            p["type"], p["date_made"], p["deadline"], p["source"], p["confidence"]
        )
        print(f"Added promise: {promise_id}")
        
        # Update some promises as completed
        if "enrollment" in p["promise"].lower():
            # Mark enrollment as completed on time
            tracker.update_promise_status(
                promise_id,
                PromiseStatus.DELIVERED_ON_TIME,
                datetime(2023, 12, 15),
                "Enrollment completed with 850 patients"
            )
    
    # Pfizer promises
    pfizer_promises = [
        {
            "executive": "Albert Bourla",
            "title": "CEO",
            "company": "Pfizer Inc.",
            "promise": "We expect to launch our RSV vaccine for older adults in Q3 2023",
            "type": PromiseType.PRODUCT_LAUNCH,
            "date_made": datetime(2023, 5, 1),
            "deadline": datetime(2023, 9, 30),
            "source": "Q1 2023 Earnings Call",
            "confidence": "very confident"
        },
        {
            "executive": "Mikael Dolsten",
            "title": "Chief Scientific Officer",
            "company": "Pfizer Inc.",
            "promise": "Phase 2b data for our obesity drug will be available in H1 2024",
            "type": PromiseType.DATA_READOUT,
            "date_made": datetime(2023, 10, 15),
            "deadline": datetime(2024, 6, 30),
            "source": "R&D Day Presentation",
            "confidence": "expect"
        }
    ]
    
    # Add Pfizer promises
    for p in pfizer_promises:
        promise_id = tracker.track_promise(
            p["executive"], p["title"], p["company"], p["promise"],
            p["type"], p["date_made"], p["deadline"], p["source"], p["confidence"]
        )
        print(f"Added promise: {promise_id}")
        
        # Mark RSV launch as successful but late
        if "RSV vaccine" in p["promise"]:
            tracker.update_promise_status(
                promise_id,
                PromiseStatus.DELIVERED_LATE,
                datetime(2023, 10, 20),
                "Abrysvo launched successfully, 3 weeks later than promised"
            )
    
    print("\nManagement promise data populated successfully!")


def populate_fda_data():
    """Populate sample FDA submission data"""
    analyzer = FDADecisionAnalyzer()
    
    # Moderna submissions
    moderna_submissions = [
        FDASubmission(
            company_name="Moderna, Inc.",
            drug_name="mRNA-1283",
            drug_type=DrugType.VACCINE,
            indication="Next-generation COVID-19 vaccine",
            review_division=FDAReviewDivision.ANTIMICROBIAL,
            review_pathway=ReviewPathway.STANDARD,
            submission_date=datetime(2024, 7, 1),
            submission_type="BLA",
            pdufa_date=datetime(2025, 5, 1),
            has_breakthrough_designation=False,
            has_fast_track=True,
            primary_endpoint="Immunogenicity non-inferiority",
            primary_endpoint_met=True,
            safety_profile_grade=4,
            pivotal_trial_size=3000,
            unmet_medical_need=False
        ),
        FDASubmission(
            company_name="Moderna, Inc.",
            drug_name="mRNA-1345",
            drug_type=DrugType.VACCINE,
            indication="Respiratory syncytial virus (RSV) vaccine",
            review_division=FDAReviewDivision.ANTIMICROBIAL,
            review_pathway=ReviewPathway.PRIORITY,
            submission_date=datetime(2023, 7, 17),
            submission_type="BLA",
            pdufa_date=datetime(2024, 5, 12),
            has_breakthrough_designation=True,
            primary_endpoint="Prevention of RSV-LRTD",
            primary_endpoint_met=True,
            safety_profile_grade=4,
            pivotal_trial_size=37000,
            unmet_medical_need=True,
            decision_type=None,  # Still pending
            decision_date=None
        )
    ]
    
    # Pfizer submissions
    pfizer_submissions = [
        FDASubmission(
            company_name="Pfizer Inc.",
            drug_name="Danuglipron",
            drug_type=DrugType.SMALL_MOLECULE,
            indication="Type 2 diabetes and obesity",
            review_division=FDAReviewDivision.ENDOCRINOLOGY,
            review_pathway=ReviewPathway.STANDARD,
            submission_date=datetime(2024, 9, 1),
            submission_type="NDA",
            pdufa_date=datetime(2025, 7, 1),
            has_fast_track=True,
            primary_endpoint="HbA1c reduction and weight loss",
            primary_endpoint_met=True,
            safety_profile_grade=3,
            pivotal_trial_size=1200,
            unmet_medical_need=True
        )
    ]
    
    # Save submissions
    for submission in moderna_submissions:
        if analyzer.save_submission(submission):
            print(f"Added FDA submission: {submission.drug_name} for {submission.indication}")
    
    for submission in pfizer_submissions:
        if analyzer.save_submission(submission):
            print(f"Added FDA submission: {submission.drug_name} for {submission.indication}")
    
    print("\nFDA submission data populated successfully!")


def main():
    """Run all data population"""
    print("🔧 Populating sample data for demonstration...\n")
    
    print("1️⃣ Populating Management Promise Data")
    print("-" * 50)
    populate_management_data()
    
    print("\n2️⃣ Populating FDA Submission Data")
    print("-" * 50)
    populate_fda_data()
    
    print("\n✅ Sample data population complete!")
    print("\nYou can now test the stock ticker intelligence with:")
    print("  python3 stock_ticker_intelligence.py MRNA")
    print("  python3 stock_ticker_intelligence.py PFE")


if __name__ == "__main__":
    main() 