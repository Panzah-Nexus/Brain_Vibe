"""
Utility functions for interacting with Git repositories
"""
import os
import subprocess
import logging
from typing import Optional, List, Dict, Any, Tuple

# Set up logger
logger = logging.getLogger(__name__)

def get_repo_diffs(repo_path: str, from_commit: Optional[str] = None, to_commit: str = "HEAD") -> str:
    """
    Get the diff between two commits in a Git repository.
    If from_commit is None, get the diff of the most recent commit.
    
    Args:
        repo_path: Path to the Git repository
        from_commit: Starting commit (default: previous commit)
        to_commit: Ending commit (default: HEAD)
        
    Returns:
        A string containing the Git diff
    """
    # In real implementation, we would validate the repo path and commits
    logger.info(f"Getting diff for repo: {repo_path} from {from_commit} to {to_commit}")
    
    # STUB: For now, just return a mock diff
    return MOCK_DIFF


def get_recent_commits(repo_path: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Get information about recent commits in a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        count: Number of commits to retrieve
        
    Returns:
        A list of dictionaries with commit information
    """
    logger.info(f"Getting {count} recent commits for repo: {repo_path}")
    
    # STUB: Return mock commits
    return MOCK_COMMITS


def execute_git_command(repo_path: str, command: List[str]) -> Tuple[str, int]:
    """
    Execute a Git command in the given repository.
    
    Args:
        repo_path: Path to the Git repository
        command: Git command and arguments as a list
        
    Returns:
        Tuple of (output, return_code)
    """
    # This is a placeholder that would be implemented in the real version
    full_command = ["git"] + command
    logger.debug(f"Executing git command: {' '.join(full_command)}")
    
    # In the real implementation, we would do:
    # try:
    #     process = subprocess.Popen(
    #         full_command,
    #         cwd=repo_path,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text=True
    #     )
    #     stdout, stderr = process.communicate()
    #     return_code = process.returncode
    #     
    #     if return_code != 0:
    #         logger.error(f"Git command failed: {stderr}")
    #     
    #     return stdout, return_code
    # except Exception as e:
    #     logger.exception(f"Failed to execute git command: {e}")
    #     return str(e), 1
    
    # For now, return a mock success
    return "Mock git command output", 0


# Mock data for stubs
MOCK_COMMITS = [
    {
        "hash": "a1b2c3d4e5f6g7h8i9j0",
        "author": "John Doe",
        "date": "2023-04-05 14:30:45",
        "message": "Add authentication feature"
    },
    {
        "hash": "b2c3d4e5f6g7h8i9j0k1",
        "author": "Jane Smith",
        "date": "2023-04-04 10:15:30",
        "message": "Implement React components"
    },
    {
        "hash": "c3d4e5f6g7h8i9j0k1l2",
        "author": "John Doe",
        "date": "2023-04-03 16:45:20",
        "message": "Set up basic project structure"
    }
]

MOCK_DIFF = """diff --git a/src/components/Auth.js b/src/components/Auth.js
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/src/components/Auth.js
@@ -0,0 +1,42 @@
+import React, { useState } from 'react';
+import { useNavigate } from 'react-router-dom';
+import axios from 'axios';
+import jwt_decode from 'jwt-decode';
+
+function Auth() {
+  const [username, setUsername] = useState('');
+  const [password, setPassword] = useState('');
+  const [error, setError] = useState('');
+  const navigate = useNavigate();
+
+  const handleLogin = async (e) => {
+    e.preventDefault();
+    try {
+      const response = await axios.post('/api/auth/login/', {
+        username,
+        password
+      });
+      
+      const { access, refresh } = response.data;
+      localStorage.setItem('access_token', access);
+      localStorage.setItem('refresh_token', refresh);
+      
+      const decoded = jwt_decode(access);
+      const user_id = decoded.user_id;
+      
+      navigate('/dashboard');
+    } catch (err) {
+      setError('Invalid credentials');
+    }
+  };
+
+  return (
+    <form onSubmit={handleLogin}>
+      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
+      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
+      <button type="submit">Login</button>
+      {error && <p>{error}</p>}
+    </form>
+  );
+}
+
+export default Auth;""" 