"""
Example code demonstrating how to hook into Cursor's events to track code changes.

This would be implemented in a Cursor extension that sends data to our Django backend.
"""
import os
import json
import requests
from typing import Dict, Any

# Mock Cursor API event data
CURSOR_EVENT_EXAMPLE = {
    "event_type": "ai_edit_applied",  # This would be a Cursor-specific event type
    "session_id": "cursor_session_123456",
    "file_path": "/path/to/project/src/components/Auth.js",
    "before_content": "// Original content here",
    "after_content": "// New content here with AI-generated changes",
    "cursor_metadata": {
        "prompt_id": "prompt_789",
        "model": "claude-3-opus",
        "timestamp": "2023-04-06T10:15:30Z"
    }
}

# Configuration
API_ENDPOINT = os.environ.get('BRAIN_VIBE_API_ENDPOINT', 'http://localhost:8000/api')
PROJECT_ID = os.environ.get('PROJECT_ID', 'demo-project-id')

def handle_cursor_ai_edit_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a Cursor AI edit event and send it to the Brain Vibe API.
    
    Args:
        event_data: Data from the Cursor event
        
    Returns:
        The API response
    """
    # Extract data from the event
    file_path = event_data.get('file_path', '')
    before_content = event_data.get('before_content', '')
    after_content = event_data.get('after_content', '')
    session_id = event_data.get('session_id', '')
    cursor_metadata = event_data.get('cursor_metadata', {})
    
    # Check if we have the required data
    if not file_path or not after_content:
        print(f"Missing required data in event: {event_data}")
        return {"error": "Missing required data"}
    
    # Prepare the API request
    api_url = f"{API_ENDPOINT}/projects/{PROJECT_ID}/analyze_changes/"
    
    payload = {
        "file_path": file_path,
        "original_content": before_content,
        "new_content": after_content,
        "cursor_session_id": session_id,
        "metadata": cursor_metadata
    }
    
    # Send the request to our API
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to API: {e}")
        return {"error": str(e)}

# Example usage
def main():
    """Example of processing a Cursor event"""
    print("Handling mock Cursor AI edit event...")
    result = handle_cursor_ai_edit_event(CURSOR_EVENT_EXAMPLE)
    print(f"API Response: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main() 