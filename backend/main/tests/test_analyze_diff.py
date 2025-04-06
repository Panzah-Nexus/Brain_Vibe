"""
Test script for the analyze_diff endpoint.

This script demonstrates how to call the analyze_diff endpoint and process the response.
"""

import requests
import json
import sys
import os


def test_analyze_diff(base_url, project_id, repo_path):
    """
    Test the analyze_diff endpoint.
    
    Args:
        base_url: The base URL of the API
        project_id: The ID of the project to analyze
        repo_path: Path to the Git repository
    """
    url = f"{base_url}/projects/{project_id}/analyze-diff/"
    
    # Prepare the request data
    data = {
        "repo_path": repo_path
    }
    
    print(f"Calling API: {url}")
    print(f"Project ID: {project_id}")
    print(f"Repository path: {repo_path}")
    
    # Make the API call
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Process the response
        result = response.json()
        
        print("\nAPI Response:")
        print(f"Status code: {response.status_code}")
        print(f"Message: {result.get('message')}")
        print(f"Topics created: {result.get('topics_created')}")
        print(f"Topics updated: {result.get('topics_updated')}")
        
        # Print the topics
        topics = result.get('topics', [])
        if topics:
            print("\nTopics:")
            for topic in topics:
                status = "NEW" if topic.get('is_new') else "UPDATED"
                print(f"  - {topic.get('title')} ({topic.get('topic_id')}) - {status}")
        else:
            print("No topics were created or updated.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(f"API error: {error_data}")
            except ValueError:
                print(f"API error (non-JSON): {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    # Get arguments from command line or use defaults
    if len(sys.argv) > 3:
        base_url = sys.argv[1]
        project_id = sys.argv[2]
        repo_path = sys.argv[3]
    else:
        base_url = "http://localhost:8000/api"
        
        # Use default project ID from environment or fallback
        project_id = os.environ.get("TEST_PROJECT_ID", "web-app-1")
        
        # Default repo path - adjust as needed
        repo_path = os.environ.get("TEST_REPO_PATH", "/path/to/repo")
        
        print("No arguments provided, using defaults.")
        print("Usage: python test_analyze_diff.py <base_url> <project_id> <repo_path>")
    
    # Run the test
    test_analyze_diff(base_url, project_id, repo_path) 