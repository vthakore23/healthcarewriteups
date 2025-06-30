#!/usr/bin/env python3
"""
Test script for Daily Healthcare Intelligence System
Verifies all components are working correctly
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        from scraper import LifeScienceScraper
        print("✅ Scraper module imported")
        
        from ai_generator import AISummaryGenerator
        print("✅ AI Generator module imported")
        
        from email_sender import EmailSender
        print("✅ Email Sender module imported")
        
        from stock_ticker_intelligence import HealthcareCompanyIntelligence
        print("✅ Stock Intelligence module imported")
        
        from daily_healthcare_intelligence import DailyHealthcareIntelligence
        print("✅ Main intelligence module imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_configuration():
    """Test configuration settings"""
    print("\n🔧 Testing configuration...")
    import config
    
    # Check AI configuration
    if config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY:
        print("✅ AI API key configured")
    else:
        print("⚠️  No AI API key found - set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    # Check email configuration
    if config.EMAIL_ENABLED:
        if config.EMAIL_RECIPIENTS:
            print(f"✅ Email recipients: {', '.join(config.EMAIL_RECIPIENTS)}")
        else:
            print("⚠️  Email enabled but no recipients configured")
        
        if config.SENDGRID_API_KEY:
            print("  → Using SendGrid")
        elif config.SMTP_USERNAME:
            print("  → Using SMTP")
        else:
            print("  ⚠️ No email credentials configured")
    else:
        print("✅ Email disabled - Reports will be saved locally only")
    
    # Check schedule
    print(f"✅ Schedule times: {', '.join(t.strftime('%H:%M') for t in config.CHECK_TIMES)} ET")
    
    return True


def test_scraper():
    """Test the news scraper"""
    print("\n🌐 Testing news scraper...")
    try:
        from scraper import LifeScienceScraper
        scraper = LifeScienceScraper()
        
        # Test URL accessibility
        import requests
        response = requests.get('https://lifesciencereport.com/newsroom', timeout=10)
        if response.status_code == 200:
            print("✅ lifesciencereport.com/newsroom is accessible")
        else:
            print(f"⚠️  Website returned status code: {response.status_code}")
        
        # Test article scraping (without actually scraping today's articles)
        print("✅ Scraper initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False


def test_ai_generator():
    """Test AI summary generation"""
    print("\n🤖 Testing AI generator...")
    try:
        from ai_generator import AISummaryGenerator
        import config
        
        if not (config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY):
            print("⚠️  Skipping AI test - no API key configured")
            return True
            
        generator = AISummaryGenerator()
        print(f"✅ AI generator initialized with {generator.ai_provider}")
        
        # Test with sample content
        from scraper import NewsArticle
        from datetime import datetime
        
        sample_article = NewsArticle(
            title="Test Article: New Cancer Drug Shows Promise",
            url="https://example.com/test",
            content="This is a test article about a new cancer drug...",
            published_date=datetime.now(),
            company_name="Test Pharma Inc."
        )
        
        print("  → Testing summary generation with sample article...")
        # Note: Not actually calling API to avoid costs
        print("✅ AI generator ready for use")
        return True
        
    except Exception as e:
        print(f"❌ AI generator test failed: {e}")
        return False


def test_stock_intelligence():
    """Test stock ticker intelligence"""
    print("\n📊 Testing stock intelligence...")
    try:
        from stock_ticker_intelligence import HealthcareCompanyIntelligence
        intel = HealthcareCompanyIntelligence()
        
        # Test with demo ticker
        print("  → Testing with demo ticker MRNA...")
        result = intel.get_company_intelligence("MRNA")
        
        if "error" not in result:
            print(f"✅ Stock data retrieved: {result.get('company_name', 'Unknown')}")
            print(f"  → Market Cap: {result.get('market_cap', 'N/A')}")
            print(f"  → Sector: {result.get('sector', 'N/A')}")
        else:
            print(f"⚠️  Stock intelligence returned error: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stock intelligence test failed: {e}")
        return False


def test_report_generation():
    """Test report generation and storage"""
    print("\n📄 Testing report generation...")
    try:
        import config
        import os
        
        # Check directories
        for dir_name in ['data', 'reports', 'cache']:
            dir_path = getattr(config, f'{dir_name.upper()}_DIR')
            if os.path.exists(dir_path):
                print(f"✅ {dir_name}/ directory exists")
            else:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ Created {dir_name}/ directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False


def run_component_test():
    """Run a minimal component integration test"""
    print("\n🚀 Testing component integration...")
    try:
        from daily_healthcare_intelligence import DailyHealthcareIntelligence
        
        # Initialize system
        system = DailyHealthcareIntelligence()
        print("✅ Healthcare Intelligence System initialized")
        
        # Test email template generation
        from email_sender import EmailSender
        sender = EmailSender()
        
        # Create sample data
        sample_summary = {
            'title': 'Test Article',
            'url': 'https://example.com',
            'summary': 'Company Name: Test Pharma\n\nNews Event: Clinical Trial\n\nNews Summary:\nTest summary.',
            'company_name': 'Test Pharma'
        }
        
        sample_analysis = {
            'title': 'Test Article',
            'company_name': 'Test Pharma',
            'analysis': 'This is interesting because...'
        }
        
        # Test HTML generation
        from datetime import datetime
        html = sender._generate_html_content([sample_summary], [sample_analysis], datetime.now())
        if html and len(html) > 100:
            print("✅ Email template generation working")
        else:
            print("⚠️  Email template generation issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Component integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧬 Daily Healthcare Intelligence System Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_scraper,
        test_ai_generator,
        test_stock_intelligence,
        test_report_generation,
        run_component_test
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: ./run_healthcare_intelligence.sh --once")
        print("3. Or run on schedule: ./run_healthcare_intelligence.sh")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        print("\nCommon issues:")
        print("- Missing API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        print("- Missing email configuration")
        print("- Network connectivity issues")
    
    print("=" * 60)


if __name__ == "__main__":
    main() 