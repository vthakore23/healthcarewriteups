#!/usr/bin/env python3
"""
Test script to verify API keys are working
"""
import os
from dotenv import load_dotenv
import anthropic
import openai

# Load environment variables
load_dotenv()

print("Testing API keys...\n")

# Test Anthropic
if os.getenv('ANTHROPIC_API_KEY'):
    print("Testing Anthropic API...")
    try:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model="claude-3-sonnet-20240229",  # Using sonnet instead of opus
            messages=[{"role": "user", "content": "Say 'Hello, healthcare automation is working!'"}],
            max_tokens=50
        )
        print(f"✅ Anthropic API working: {response.content[0].text}")
    except Exception as e:
        print(f"❌ Anthropic API error: {e}")
else:
    print("❌ No Anthropic API key found")

print()

# Test OpenAI
if os.getenv('OPENAI_API_KEY'):
    print("Testing OpenAI API...")
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a model that definitely exists
            messages=[{"role": "user", "content": "Say 'Hello, healthcare automation is working!'"}],
            max_tokens=50
        )
        print(f"✅ OpenAI API working: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
else:
    print("❌ No OpenAI API key found")

print("\nRecommended settings:")
if os.getenv('ANTHROPIC_API_KEY'):
    print("- Use AI_MODEL=claude-3-sonnet-20240229 in your .env file")
elif os.getenv('OPENAI_API_KEY'):
    print("- Use AI_MODEL=gpt-4-turbo-preview or gpt-3.5-turbo in your .env file") 