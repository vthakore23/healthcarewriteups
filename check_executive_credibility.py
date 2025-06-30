#!/usr/bin/env python3
"""
Standalone tool to check executive credibility and promise history
Can be used independently to research specific executives
"""
import argparse
import sys
from datetime import datetime
from management_truth_tracker import ManagementTruthTracker, PromiseStatus, PromiseType
import json


def print_header():
    """Print tool header"""
    print("\n" + "🕵️ "*20)
    print("EXECUTIVE CREDIBILITY CHECKER")
    print("Management Truth Tracker™")
    print("🕵️ "*20 + "\n")


def search_executives(tracker: ManagementTruthTracker, search_term: str):
    """Search for executives by name or company"""
    import sqlite3
    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()
    
    try:
        # Search by executive name or company
        cursor.execute("""
            SELECT DISTINCT executive_name, company, executive_title
            FROM promises
            WHERE executive_name LIKE ? OR company LIKE ?
            ORDER BY company, executive_name
        """, (f"%{search_term}%", f"%{search_term}%"))
        
        results = cursor.fetchall()
        
        if not results:
            print(f"❌ No executives found matching '{search_term}'")
            return []
        
        print(f"\n🔍 Found {len(results)} executive(s):")
        print("-" * 60)
        
        for i, (name, company, title) in enumerate(results, 1):
            print(f"{i}. {name} - {title} at {company}")
        
        return results
        
    finally:
        conn.close()


def display_executive_details(tracker: ManagementTruthTracker, 
                            executive_name: str, company: str):
    """Display detailed credibility report for an executive"""
    details = tracker.get_executive_promise_details(executive_name, company)
    
    print(f"\n{'='*80}")
    print(f"EXECUTIVE: {executive_name}")
    print(f"COMPANY: {company}")
    print(f"{'='*80}\n")
    
    # Credibility summary
    cred = details['credibility_summary']
    score = cred['credibility_score']
    
    # Visual score representation
    score_bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
    
    print(f"📊 CREDIBILITY SCORE: [{score_bar}] {score:.1%}")
    
    if score >= 0.8:
        print("   ✅ HIGH CREDIBILITY - Reliable track record")
    elif score >= 0.6:
        print("   ⚠️  MODERATE CREDIBILITY - Some delays/issues")
    else:
        print("   🚨 LOW CREDIBILITY - High risk of failure/delays")
    
    print(f"\n📈 TRACK RECORD:")
    print(f"   Total Promises: {details['total_promises']}")
    print(f"   ✅ On Time: {len(details['on_time_promises'])} ({details['on_time_rate']:.1%})")
    print(f"   ⚠️  Late: {len(details['late_promises'])} ({details['late_rate']:.1%})")
    print(f"   ❌ Failed: {len(details['failed_promises'])} ({details['failure_rate']:.1%})")
    print(f"   ⏳ Pending: {len(details['pending_promises'])}")
    
    if cred.get('average_delay_days', 0) > 0:
        print(f"   📅 Average Delay: {cred['average_delay_days']:.1f} days")
    
    # Show failed promises
    if details['failed_promises']:
        print(f"\n❌ FAILED PROMISES ({len(details['failed_promises'])} total):")
        print("-" * 80)
        
        for i, promise in enumerate(details['failed_promises'][:5], 1):
            print(f"\n{i}. {promise['promise_type'].replace('_', ' ').title()}")
            print(f"   Date: {promise['date_made'][:10]}")
            print(f"   Promise: \"{promise['promise_text'][:150]}...\"")
            if promise['deadline']:
                print(f"   Deadline: {promise['deadline'][:10]} (MISSED)")
            if promise['outcome_details']:
                print(f"   What happened: {promise['outcome_details']}")
            print(f"   Confidence level: {promise['confidence_language']}")
    
    # Show overdue pending promises
    overdue = [p for p in details['pending_promises'] 
               if 'OVERDUE' in p.get('status_display', '')]
    
    if overdue:
        print(f"\n⏰ OVERDUE PROMISES ({len(overdue)} total):")
        print("-" * 80)
        
        for i, promise in enumerate(overdue[:3], 1):
            print(f"\n{i}. {promise['promise_type'].replace('_', ' ').title()}")
            print(f"   Promise: \"{promise['promise_text'][:150]}...\"")
            print(f"   Status: {promise['status_display']}")
    
    # Investment recommendation
    print(f"\n💡 INVESTMENT IMPLICATIONS:")
    print("-" * 80)
    
    if score >= 0.8:
        print("✅ This executive has a strong track record of delivery")
        print("   • Timeline guidance is likely reliable")
        print("   • Low risk of surprise delays")
    elif score >= 0.6:
        print("⚠️  This executive has a mixed track record")
        print(f"   • Add {int(cred.get('average_delay_days', 30))} days buffer to timelines")
        print("   • Monitor promises closely")
    else:
        print("🚨 This executive has poor credibility")
        print("   • High risk of delays and failures")
        print("   • Consider reducing exposure ahead of key milestones")
        print("   • Verify all claims independently")


def check_company_credibility(tracker: ManagementTruthTracker, company: str):
    """Check overall company credibility"""
    cred = tracker.get_company_credibility(company)
    
    print(f"\n{'='*80}")
    print(f"COMPANY: {company}")
    print(f"{'='*80}\n")
    
    score = cred['overall_credibility']
    score_bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
    
    print(f"📊 COMPANY CREDIBILITY: [{score_bar}] {score:.1%}")
    print(f"   Total Executives Tracked: {cred['total_executives']}")
    print(f"   Total Promises: {cred['total_promises']}")
    
    # Breakdown by promise type
    if cred.get('by_promise_type'):
        print(f"\n📈 PERFORMANCE BY PROMISE TYPE:")
        for ptype, stats in cred['by_promise_type'].items():
            if isinstance(stats, dict) and stats.get('total', 0) > 0:
                success_rate = stats.get('success_rate', 0)
                total = stats.get('total', 0)
                print(f"   • {ptype.replace('_', ' ').title()}: "
                      f"{success_rate:.0%} success ({total} promises)")


def export_report(tracker: ManagementTruthTracker, executive_name: str, 
                 company: str, output_file: str):
    """Export detailed report to file"""
    report = tracker.generate_executive_accountability_report(executive_name, company)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report exported to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Check executive credibility and promise history"
    )
    
    parser.add_argument(
        "action",
        choices=["search", "check", "company", "export"],
        help="Action to perform"
    )
    
    parser.add_argument(
        "query",
        help="Executive name, company name, or search term"
    )
    
    parser.add_argument(
        "--company",
        help="Company name (for executive check)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file for export"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    tracker = ManagementTruthTracker()
    
    if args.action == "search":
        # Search for executives
        results = search_executives(tracker, args.query)
        
        if results and len(results) == 1:
            # Auto-display if only one result
            name, company, _ = results[0]
            print(f"\n📌 Auto-displaying details for {name}...")
            display_executive_details(tracker, name, company)
    
    elif args.action == "check":
        # Check specific executive
        if not args.company:
            print("❌ Error: --company required for executive check")
            print("   Example: check 'John Smith' --company 'BioPharma Inc'")
            sys.exit(1)
        
        display_executive_details(tracker, args.query, args.company)
    
    elif args.action == "company":
        # Check company credibility
        check_company_credibility(tracker, args.query)
    
    elif args.action == "export":
        # Export report
        if not args.company:
            print("❌ Error: --company required for export")
            sys.exit(1)
        
        output_file = args.output or f"{args.query.replace(' ', '_')}_{args.company.replace(' ', '_')}_credibility.txt"
        export_report(tracker, args.query, args.company, output_file)
    
    print("\n" + "-"*80)
    print("Use 'python check_executive_credibility.py -h' for help")


if __name__ == "__main__":
    main() 