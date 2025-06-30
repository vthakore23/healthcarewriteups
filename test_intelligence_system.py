#!/usr/bin/env python3
"""
Quick test script to verify the Healthcare Investment Intelligence System
"""
import os
import sys

def test_imports():
    """Test that all intelligence modules can be imported"""
    print("🧬 Testing Healthcare Investment Intelligence System")
    print("="*60)
    
    print("\n1. Testing imports...")
    try:
        from management_truth_tracker import ManagementTruthTracker, PromiseType, PromiseStatus
        print("✅ Management Truth Tracker imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Management Truth Tracker: {e}")
        return False
    
    try:
        from fda_decision_analyzer import FDADecisionAnalyzer, FDASubmission, DrugType
        print("✅ FDA Decision Analyzer imported successfully")
    except Exception as e:
        print(f"❌ Failed to import FDA Decision Analyzer: {e}")
        return False
    
    try:
        from integrated_intelligence_system import IntegratedIntelligenceSystem
        print("✅ Integrated Intelligence System imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Integrated Intelligence System: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of each system"""
    print("\n2. Testing basic functionality...")
    
    # Test Management Truth Tracker
    try:
        from management_truth_tracker import ManagementTruthTracker
        tracker = ManagementTruthTracker()
        print("✅ Management Truth Tracker initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Management Truth Tracker: {e}")
        return False
    
    # Test FDA Decision Analyzer
    try:
        from fda_decision_analyzer import FDADecisionAnalyzer
        analyzer = FDADecisionAnalyzer()
        print("✅ FDA Decision Analyzer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize FDA Decision Analyzer: {e}")
        return False
    
    # Test Integrated Intelligence System
    try:
        from integrated_intelligence_system import IntegratedIntelligenceSystem
        intel_system = IntegratedIntelligenceSystem()
        print("✅ Integrated Intelligence System initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Integrated Intelligence System: {e}")
        return False
    
    return True

def test_database_creation():
    """Test that databases can be created"""
    print("\n3. Testing database creation...")
    
    databases = ['management_promises.db', 'fda_submissions.db']
    for db in databases:
        if os.path.exists(db):
            print(f"✅ Database exists: {db}")
        else:
            print(f"⚠️  Database will be created on first use: {db}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "🧬 "*15)
    print("HEALTHCARE INVESTMENT INTELLIGENCE SYSTEM TEST")
    print("🧬 "*15 + "\n")
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
    
    if not test_basic_functionality():
        all_passed = False
    
    if not test_database_creation():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe Healthcare Investment Intelligence System is ready to use.")
        print("\nTry these commands:")
        print("  - python demo_integrated_intelligence.py     # See features in action")
        print("  - python main_enhanced_intelligence.py --demo  # Run on real articles")
        print("  - python main_enhanced_intelligence.py --run-now  # Full analysis")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*60)

if __name__ == "__main__":
    main() 