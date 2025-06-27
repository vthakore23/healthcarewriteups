#!/usr/bin/env python3
"""
Performance test script for Healthcare News Automation
"""
import time
import json
import os
from datetime import datetime

# Import our modules
from main_optimized import OptimizedHealthcareNewsAutomation

def run_performance_test():
    """Run performance test with timing metrics"""
    print("🧪 HEALTHCARE NEWS AUTOMATION - PERFORMANCE TEST")
    print("=" * 60)
    
    automation = OptimizedHealthcareNewsAutomation()
    
    # Test with different article limits
    test_cases = [3, 5, 10]
    
    for limit in test_cases:
        print(f"\n📊 Testing with {limit} articles...")
        
        start_time = time.time()
        automation.run_daily_task(send_email=False, limit_articles=limit)
        end_time = time.time()
        
        elapsed = end_time - start_time
        avg_per_article = elapsed / limit
        
        # Load the report to get actual counts
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_file = f'reports/report_{date_str}.json'
            
            with open(report_file, 'r') as f:
                data = json.load(f)
                
            summaries = len(data['summaries'])
            analyses = len(data['analyses'])
            
            print(f"⏱️  Performance Results for {limit} articles:")
            print(f"   • Total time: {elapsed:.1f} seconds")
            print(f"   • Average per article: {avg_per_article:.1f} seconds")
            print(f"   • Summaries generated: {summaries}")
            print(f"   • Deep analyses: {analyses}")
            print(f"   • Articles per minute: {(summaries / elapsed) * 60:.1f}")
            
        except Exception as e:
            print(f"   ❌ Could not load report: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    run_performance_test() 