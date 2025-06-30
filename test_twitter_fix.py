#!/usr/bin/env python3
"""
Twitter API Fix and Test Script
Tests current Twitter API setup and provides solutions
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_twitter_credentials():
    """Check what Twitter credentials are available"""
    print("🐦 TWITTER API CREDENTIAL CHECK")
    print("=" * 50)
    
    twitter_api_key = os.getenv('TWITTER_API_KEY', '')
    twitter_api_secret = os.getenv('TWITTER_API_SECRET', '')
    twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
    twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
    twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET', '')
    
    print(f"✅ TWITTER_API_KEY: {'Set' if twitter_api_key else 'Missing'}")
    if twitter_api_key:
        print(f"   Value: {twitter_api_key[:15]}...")
        
    print(f"❌ TWITTER_API_SECRET: {'Set' if twitter_api_secret else 'Missing'}")
    print(f"❌ TWITTER_BEARER_TOKEN: {'Set' if twitter_bearer_token else 'Missing'}")
    print(f"❌ TWITTER_ACCESS_TOKEN: {'Set' if twitter_access_token else 'Missing'}")
    print(f"❌ TWITTER_ACCESS_SECRET: {'Set' if twitter_access_secret else 'Missing'}")
    
    print("\n📋 ANALYSIS:")
    if twitter_bearer_token:
        print("✅ You have Bearer Token - Twitter API v2 should work!")
        return "bearer_token"
    elif twitter_api_key and twitter_api_secret and twitter_access_token and twitter_access_secret:
        print("✅ You have full API v1.1 credentials - Can use legacy API!")
        return "api_v1"
    elif twitter_api_key:
        print("⚠️  You only have API Key - Limited functionality")
        print("   Need Bearer Token OR API Secret + Access Tokens for real data")
        return "api_key_only"
    else:
        print("❌ No Twitter credentials found")
        return "none"

def provide_solutions(credential_status):
    """Provide solutions based on credential status"""
    print("\n🔧 SOLUTIONS:")
    print("=" * 50)
    
    if credential_status == "bearer_token":
        print("✅ No action needed - Twitter API should work!")
        
    elif credential_status == "api_v1":
        print("✅ Your API v1.1 credentials should work!")
        print("   The system will auto-detect and use them.")
        
    elif credential_status == "api_key_only":
        print("📝 TO GET REAL TWITTER DATA:")
        print("\n🎯 OPTION 1: Get Bearer Token (Easiest)")
        print("1. Go to https://developer.twitter.com/")
        print("2. Login and go to your app dashboard") 
        print("3. Click on your app")
        print("4. Go to 'Keys and Tokens' tab")
        print("5. Look for 'Bearer Token' section")
        print("6. Click 'Generate' if not already generated")
        print("7. Copy the Bearer Token")
        print("8. Add to .env file:")
        print("   TWITTER_BEARER_TOKEN=your-bearer-token-here")
        
        print("\n🎯 OPTION 2: Get Full API Credentials")
        print("1. In the same 'Keys and Tokens' section")
        print("2. Generate 'API Key and Secret' if needed")
        print("3. Generate 'Access Token and Secret'")
        print("4. Add to .env file:")
        print("   TWITTER_API_SECRET=your-api-secret")
        print("   TWITTER_ACCESS_TOKEN=your-access-token")
        print("   TWITTER_ACCESS_SECRET=your-access-secret")
        
    else:
        print("❌ No Twitter credentials found")
        print("1. Go to https://developer.twitter.com/")
        print("2. Sign up for a developer account (free)")
        print("3. Create a new app")
        print("4. Get your credentials as described above")

def test_twitter_functionality():
    """Test if Twitter functionality works"""
    print("\n🧪 TESTING TWITTER FUNCTIONALITY:")
    print("=" * 50)
    
    try:
        # Import and test
        import tweepy
        
        twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        twitter_api_key = os.getenv('TWITTER_API_KEY', '')
        twitter_api_secret = os.getenv('TWITTER_API_SECRET', '')
        twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
        twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET', '')
        
        if twitter_bearer_token:
            print("🔍 Testing Twitter API v2 with Bearer Token...")
            try:
                client = tweepy.Client(bearer_token=twitter_bearer_token)
                # Test with a simple search
                response = client.search_recent_tweets(query="hello", max_results=10)
                if response.data:
                    print("✅ Twitter API v2 working! Found tweets.")
                    return True
                else:
                    print("⚠️  Twitter API v2 connected but no results")
                    return True
            except Exception as e:
                print(f"❌ Twitter API v2 failed: {e}")
                
        elif all([twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret]):
            print("🔍 Testing Twitter API v1.1...")
            try:
                auth = tweepy.OAuth1UserHandler(
                    twitter_api_key, twitter_api_secret,
                    twitter_access_token, twitter_access_secret
                )
                api = tweepy.API(auth)
                api.verify_credentials()
                print("✅ Twitter API v1.1 working!")
                return True
            except Exception as e:
                print(f"❌ Twitter API v1.1 failed: {e}")
                
        else:
            print("❌ Insufficient credentials for testing")
            
    except ImportError:
        print("❌ tweepy not installed")
        
    return False

def main():
    print("🔧 TWITTER API DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Check credentials
    status = check_twitter_credentials()
    
    # Provide solutions
    provide_solutions(status)
    
    # Test functionality
    working = test_twitter_functionality()
    
    print("\n📊 SUMMARY:")
    print("=" * 50)
    if working:
        print("✅ Twitter API is working correctly!")
        print("   Real tweets should be collected instead of demo data.")
    else:
        print("❌ Twitter API not working")
        print("   Currently using demo data.")
        print("   Follow the solutions above to fix.")
        
    print(f"\n🎯 Current Status: {status}")
    print(f"🔄 API Working: {'Yes' if working else 'No'}")
    
    if not working:
        print("\n💡 QUICK FIX:")
        print("Add this line to your .env file:")
        print("TWITTER_BEARER_TOKEN=your-actual-bearer-token")
        print("\nThen restart the platform: ./run_platform.sh")

if __name__ == "__main__":
    main() 