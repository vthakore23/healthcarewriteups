#!/usr/bin/env python3
"""
Test script to verify the healthcare news automation system is working
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🧪 TESTING HEALTHCARE NEWS AUTOMATION SYSTEM")
print("=" * 60)

# Test 1: Check if environment variables are loaded
print("\n1. Testing environment variables...")
import config

print(f"   AI Model: {config.AI_MODEL}")
print(f"   Anthropic API Key: {'✅ Set' if config.ANTHROPIC_API_KEY else '❌ Missing'}")
print(f"   OpenAI API Key: {'✅ Set' if config.OPENAI_API_KEY else '❌ Missing'}")

# Test 2: Check AI generator initialization
print("\n2. Testing AI generator initialization...")
try:
    from ai_generator_optimized import OptimizedAISummaryGenerator
    ai_gen = OptimizedAISummaryGenerator(max_workers=1)
    print(f"   ✅ AI Generator initialized with provider: {ai_gen.ai_provider}")
except Exception as e:
    print(f"   ❌ AI Generator failed: {e}")
    sys.exit(1)

# Test 3: Check scraper initialization
print("\n3. Testing scraper initialization...")
try:
    from scraper_optimized import OptimizedLifeScienceScraper
    scraper = OptimizedLifeScienceScraper(max_workers=1)
    print("   ✅ Scraper initialized successfully")
except Exception as e:
    print(f"   ❌ Scraper failed: {e}")
    sys.exit(1)

# Test 4: Test full automation initialization
print("\n4. Testing full automation system...")
try:
    from main_optimized import OptimizedHealthcareNewsAutomation
    automation = OptimizedHealthcareNewsAutomation()
    print("   ✅ Full automation system initialized successfully")
except Exception as e:
    print(f"   ❌ Full automation failed: {e}")
    sys.exit(1)

# Test 5: Test article structure
print("\n5. Testing article structure...")
try:
    from scraper_optimized import NewsArticle
    from datetime import datetime
    
    test_article = NewsArticle(
        title="Test Article",
        url="https://example.com/test",
        content="This is a test article about Pfizer's new drug development...",
        published_date=datetime.now(),
        company_name="Pfizer Inc."
    )
    print("   ✅ Article structure working correctly")
except Exception as e:
    print(f"   ❌ Article structure failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED! System is ready to run.")
print("=" * 60)

print("\nNext steps:")
print("1. Run web interface: python3 web_interface.py")
print("2. Or run command line: python3 main_optimized.py --demo")
print("3. Or run full analysis: python3 main_optimized.py --local-only") 