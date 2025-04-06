#!/usr/bin/env python3
import requests
import json
import sys

def test_analyze_diff(project_id):
    url = f"http://localhost:8000/api/projects/{project_id}/analyze-diff/"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "diff_content": """diff --git a/test.js b/test.js
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/test.js
@@ -0,0 +1,25 @@
+// Simple JavaScript file with React hooks
+import React, { useState, useEffect } from 'react';
+import axios from 'axios';
+
+function UserProfile({ userId }) {
+    const [userData, setUserData] = useState(null);
+    const [loading, setLoading] = useState(true);
+    
+    useEffect(() => {
+        // Fetch user data using axios
+        async function fetchData() {
+            try {
+                const response = await axios.get(`/api/users/${userId}`);
+                setUserData(response.data);
+            } catch (error) {
+                console.error('Error fetching user data:', error);
+            } finally {
+                setLoading(false);
+            }
+        }
+        
+        fetchData();
+    }, [userId]);
+    
+    return loading ? <div>Loading...</div> : <div>{userData.name}</div>;
+}""",
        "repo_path": "/tmp/test-repo",
        "change_id": "test-script-1"
    }
    
    print(f"Testing analyze-diff API for project {project_id}...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("ERROR!")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    else:
        # Use a default project ID if none provided
        project_id = "c87f54e0"
    
    test_analyze_diff(project_id) 