"""
Example script to demonstrate how to use the Gemini API for analyzing code diffs.

This example shows how to:
1. Format a prompt for the Gemini API
2. Call the API to analyze a diff
3. Process the response to extract topics

Note: The actual API integration will be implemented in the future.
"""

import os
import json
import logging
from typing import Dict, Any, List

# Import the utilities created for code analysis
from code_tracker.utils.llm_utils import format_llm_prompt, analyze_diff, mock_topic_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample diff content for demonstration
SAMPLE_DIFF = """diff --git a/src/components/Auth.js b/src/components/Auth.js
new file mode 100644
index 0000000..a1b2c3d
--- /dev/null
+++ b/src/components/Auth.js
@@ -0,0 +1,40 @@
+import React, { useState, useEffect } from 'react';
+import axios from 'axios';
+
+function Auth() {
+  const [user, setUser] = useState(null);
+  const [loading, setLoading] = useState(true);
+  const [error, setError] = useState(null);
+
+  useEffect(() => {
+    const token = localStorage.getItem('token');
+    
+    if (!token) {
+      setLoading(false);
+      return;
+    }
+    
+    axios.get('/api/auth/user', {
+      headers: {
+        'Authorization': `Bearer ${token}`
+      }
+    })
+      .then(response => {
+        setUser(response.data);
+        setLoading(false);
+      })
+      .catch(error => {
+        setError(error.message);
+        setLoading(false);
+      });
+  }, []);
+
+  if (loading) return <div>Loading...</div>;
+  if (error) return <div>Error: {error}</div>;
+  if (!user) return <div>Please login to continue</div>;
+  
+  return <div>Welcome, {user.name}!</div>;
+}
+
+export default Auth;
+"""

def main():
    # Sample project context
    project_context = {
        'project_id': 'sample-react-app',
        'name': 'Sample React App',
        'existing_topics': [
            {'topic_id': 'react-basics', 'title': 'React Basics'},
            {'topic_id': 'javascript-promises', 'title': 'JavaScript Promises'},
            {'topic_id': 'async-await', 'title': 'Async/Await in JavaScript'}
        ]
    }
    
    # Show how to format a prompt for the Gemini API
    prompt = format_llm_prompt(SAMPLE_DIFF, project_context)
    print("Example LLM prompt:")
    print("-" * 80)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 80)
    
    # Analyze the diff with the mock implementation
    print("\nAnalyzing diff with mock implementation:")
    topics = analyze_diff(SAMPLE_DIFF, project_context)
    
    # Print the extracted topics
    print(f"\nExtracted {len(topics)} topics:")
    for topic in topics:
        print(f"- {topic.get('title')} ({topic.get('topic_id')})")
        print(f"  Description: {topic.get('description')}")
        prereqs = topic.get('prerequisites', [])
        if prereqs:
            print(f"  Prerequisites: {', '.join(prereqs)}")
    
    # Save the results to a sample file
    sample_output_file = 'sample_analysis_output.json'
    with open(sample_output_file, 'w') as f:
        json.dump({
            'topics': topics
        }, f, indent=2)
    print(f"\nSample output saved to {sample_output_file}")
    
    print("\nNote: In a real implementation, the Gemini API would be called instead of using mock data.")

if __name__ == "__main__":
    main() 