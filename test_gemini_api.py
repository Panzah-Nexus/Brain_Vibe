#!/usr/bin/env python3
"""
Test Gemini API integration for BrainVibe
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def test_gemini_api():
    """Test the Gemini API integration"""

    print("🔍 Testing Gemini API Integration")
    print("=" * 40)

    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"✓ GEMINI_API_KEY environment variable: {'SET' if api_key else 'NOT SET'}")

    if not api_key:
        print("\n❌ GEMINI_API_KEY not found!")
        print("Please set your API key:")
        print("export GEMINI_API_KEY='your_actual_api_key_here'")
        return False

    # Mask the key for security
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else api_key
    print(f"✓ API Key format: {masked_key}")

    try:
        # Import the Gemini analyzer
        from backend.code_analyzer.gemini_analyzer import GeminiTopicAnalyzer
        print("✓ Gemini analyzer imported successfully")

        # Initialize analyzer
        analyzer = GeminiTopicAnalyzer()
        print("✓ Gemini analyzer initialized")

        # Test diff with various programming concepts
        test_diff = '''diff --git a/app.py b/app.py
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/app.py
@@ -0,0 +1,25 @@
+import asyncio
+import requests
+from typing import List, Dict, Optional
+from dataclasses import dataclass
+import jwt
+from functools import wraps
+
+@dataclass
+class User:
+    id: int
+    name: str
+    email: str
+
+async def fetch_user_data(user_id: int) -> Optional[User]:
+    """Fetch user data asynchronously with error handling"""
+    try:
+        response = await requests.get(f'/api/users/{user_id}')
+        if response.status_code == 200:
+            data = response.json()
+            return User(**data)
+    except Exception as e:
+        print(f"Error fetching user {user_id}: {e}")
+        return None
+
+def authenticate_token(token: str) -> Optional[Dict]:
+    """Validate JWT token"""
+    try:
+        return jwt.decode(token, 'secret', algorithms=['HS256'])
+    except jwt.ExpiredSignatureError:
+        return None
+    except jwt.InvalidTokenError:
+        return None'''

        print("\n🔄 Testing topic extraction...")
        print(f"Input diff length: {len(test_diff)} characters")

        # Analyze the diff
        result = analyzer.analyze_diff(
            code_diff=test_diff,
            completed_topics=[],
            to_learn_topics=[]
        )

        print("✓ API call successful!")

        # Display results
        topics = result.get('topics', [])
        print(f"📚 Extracted {len(topics)} topics:")

        for i, topic in enumerate(topics[:5], 1):  # Show first 5 topics
            title = topic.get('title', 'N/A')
            description = topic.get('description', 'N/A')[:80]
            print(f"  {i}. {title}")
            print(f"     {description}...")

        if len(topics) > 5:
            print(f"     ... and {len(topics) - 5} more topics")

        print("\n✅ Gemini API integration test PASSED!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
        return False

    except Exception as e:
        print(f"❌ API test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        if "API_KEY" in str(e):
            print("This might be an API key issue - please verify your key is correct")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
