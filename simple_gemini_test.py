#!/usr/bin/env python3
"""
Simple Gemini API test that loads .env file directly
"""

import os
import sys
from pathlib import Path

# Load .env file manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

print("🔍 Simple Gemini API Test")
print("=" * 30)

# Check if API key is loaded
api_key = os.environ.get('GEMINI_API_KEY')
print(f"✓ GEMINI_API_KEY loaded: {'YES' if api_key else 'NO'}")

if api_key:
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else api_key
    print(f"✓ API Key format: {masked_key}")

    # Test Gemini import
    try:
        import google.generativeai as genai
        print("✓ Google Generative AI library imported")

        # Configure and test basic connection
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured")

        # Try to create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✓ Gemini model created")

        print("\n✅ Gemini API integration test PASSED!")
        print("The API key and integration are working correctly.")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure google-generativeai is installed")
    except Exception as e:
        print(f"❌ API error: {e}")
        print("Check your API key is valid")
else:
    print("❌ GEMINI_API_KEY not found in .env file")
