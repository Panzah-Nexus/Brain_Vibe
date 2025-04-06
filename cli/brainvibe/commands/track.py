"""
Track code changes and analyze them using BrainVibe
"""

import os
import json
import time
import subprocess
import requests
from pathlib import Path
import sys
import hashlib
import datetime
import re

def load_config():
    """Load BrainVibe configuration from .brainvibe/config.json"""
    config_path = Path('.brainvibe/config.json')
    if not config_path.exists():
        print("BrainVibe is not initialized in this directory.")
        print("Run 'brainvibe init --project-id <project_id>' to initialize.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def get_git_changes():
    """Get changes from the Git repository"""
    # Make sure all files are staged
    subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
    
    # Check if there are any changes
    result = subprocess.run(['git', 'diff', '--staged'], capture_output=True, text=True)
    if not result.stdout.strip():
        return None
    
    # Generate a change ID based on timestamp and a hash of the diff
    timestamp = datetime.datetime.now().isoformat()
    change_id = f"{timestamp}-{hashlib.md5(result.stdout.encode()).hexdigest()[:8]}"
    
    # Create a temporary commit
    commit_msg = f"BrainVibe analysis snapshot {change_id}"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
    
    # Get the diff from the commit
    diff = subprocess.run(['git', 'show', 'HEAD'], capture_output=True, text=True).stdout
    
    return {
        'change_id': change_id,
        'diff_content': diff,
        'timestamp': timestamp
    }

def should_ignore_file(file_path, ignore_patterns):
    """Check if a file should be ignored based on patterns"""
    for pattern in ignore_patterns:
        if re.match(pattern, file_path):
            return True
    return False

def load_ignore_patterns(ignore_file_path=None):
    """Load ignore patterns from .brainvibeignore or custom file"""
    # Default patterns
    patterns = [
        r'.*node_modules/.*',
        r'.*\.git/.*',
        r'.*\.brainvibe/.*',
        r'.*__pycache__/.*',
        r'.*venv/.*',
        r'.*\.env.*',
        r'.*\.md$',
        r'.*\.txt$',
        r'.*package-lock\.json$',
        r'.*\.lock$',
        r'.*\.jpg$',
        r'.*\.jpeg$',
        r'.*\.png$',
        r'.*\.gif$',
        r'.*\.pdf$',
        r'.*\.exe$',
        r'.*\.dll$',
        r'.*\.bin$'
    ]
    
    # If custom ignore file is specified
    if ignore_file_path:
        file_path = Path(ignore_file_path)
    else:
        file_path = Path('.brainvibeignore')
    
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Convert glob pattern to regex pattern
                        pattern = line.replace('.', '\\.').replace('*', '.*')
                        patterns.append(f'.*{pattern}.*')
            print(f"Loaded ignore patterns from {file_path}")
        except Exception as e:
            print(f"Error reading ignore file: {e}")
    
    return patterns

def send_changes_to_api(config, changes):
    """Send changes to the BrainVibe API for analysis"""
    url = f"{config['api_url']}/projects/{config['project_id']}/analyze-diff/"
    
    data = {
        "repo_path": str(Path.cwd()),
        "change_id": changes['change_id'],
        "diff_content": changes['diff_content']
    }
    
    try:
        print(f"Sending changes to BrainVibe API: {url}")
        print(f"Project ID: {config['project_id']}")
        print(f"Change ID: {changes['change_id']}")
        print(f"Diff length: {len(changes['diff_content'].splitlines())} lines")
        
        response = requests.post(url, json=data)
        
        # Print detailed debug info if there's a problem
        if response.status_code != 200:
            print(f"API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        result = response.json()
        print(f"Analysis complete!")
        
        if 'topics_created' in result and result['topics_created']:
            print(f"New topics discovered:")
            for topic in result['topics_created']:
                print(f"  - {topic}")
        else:
            print("No new topics discovered in this change.")
            
        return True
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the BrainVibe backend is running at:", config['api_url'])
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending changes to API: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def track_command(args):
    """Track code changes and analyze them using BrainVibe"""
    config = load_config()
    print(f"Tracking code changes for project: {config['project_id']}")
    
    # Load ignore patterns
    ignore_patterns = load_ignore_patterns(args.ignore_file)
    
    # Convert interval from milliseconds to seconds
    interval_seconds = args.interval / 1000 if args.interval else 120
    print(f"Commit interval set to {interval_seconds} seconds")
    
    if args.one_shot:
        # Run analysis once and exit
        changes = get_git_changes()
        if changes:
            send_changes_to_api(config, changes)
        else:
            print("No changes detected.")
        return 0
    
    # Continuous watching mode
    print("Watching for file changes... (Press Ctrl+C to stop)")
    last_analysis_time = 0
    
    try:
        while True:
            # Only analyze changes if it's been at least <interval> seconds since the last analysis
            current_time = time.time()
            if current_time - last_analysis_time >= interval_seconds:
                changes = get_git_changes()
                if changes:
                    if send_changes_to_api(config, changes):
                        last_analysis_time = current_time
                        print(f"Next analysis scheduled in {interval_seconds} seconds")
                
            # Check more frequently than the full interval to be responsive
            time.sleep(min(5, interval_seconds / 4))  
    except KeyboardInterrupt:
        print("\nStopping file watching.")
    
    return 0 