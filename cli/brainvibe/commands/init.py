"""
Initialize BrainVibe in a project
"""

import os
import json
import subprocess
from pathlib import Path
import sys

def init_command(args):
    """Initialize BrainVibe in a project directory"""
    project_id = args.project_id
    api_url = args.api_url
    
    print(f"Initializing BrainVibe with project ID: {project_id}")
    
    # Create .brainvibe directory
    brainvibe_dir = Path('.brainvibe')
    if brainvibe_dir.exists():
        print(f"BrainVibe is already initialized in this directory.")
        overwrite = input("Do you want to overwrite the existing configuration? (y/n): ")
        if overwrite.lower() != 'y':
            print("Initialization canceled.")
            return 1
    
    brainvibe_dir.mkdir(exist_ok=True)
    
    # Create config file
    config = {
        'project_id': project_id,
        'api_url': api_url,
        'initialized_at': str(Path.cwd()),
    }
    
    with open(brainvibe_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Check if git is initialized
    if not Path('.git').exists():
        print("Initializing Git repository for tracking changes...")
        subprocess.run(['git', 'init'], check=True)
        
        # Create .gitignore if it doesn't exist
        gitignore_path = Path('.gitignore')
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write("""# BrainVibe .gitignore
.brainvibe/
__pycache__/
*.py[cod]
*$py.class
.env
.venv
env/
venv/
ENV/
""")
    
    # Create .brainvibeignore if it doesn't exist
    brainvibeignore_path = Path('.brainvibeignore')
    if not brainvibeignore_path.exists():
        with open(brainvibeignore_path, 'w') as f:
            f.write("""# BrainVibe Ignore File
# Patterns listed here will be ignored by the BrainVibe tracking system
# Format: One pattern per line, similar to .gitignore

# Dependencies
node_modules
package-lock.json
yarn.lock
bower_components
vendor
.venv
env
venv
pip-wheel-metadata
poetry.lock
Pipfile.lock

# Build directories
dist
build
out
target
.next
.nuxt
public/build

# Cache directories
.cache
__pycache__

# Documentation
docs
*.md
*.rst
*.txt
LICENSE*
README*

# Configuration files
.env*
*.config.js
*.config.ts
tsconfig.json
jest.config.js

# IDE files
.vscode
.idea
.DS_Store

# Logs
logs
*.log

# Binary files
*.jpg
*.jpeg
*.png
*.gif
*.pdf
*.zip
*.exe
*.dll
""")
        print("Created .brainvibeignore file")
    
    # Create initial commit if no commits exist
    result = subprocess.run(['git', 'log', '-1'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Creating initial commit...")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for BrainVibe tracking'], check=True)
    
    print(f"""
BrainVibe initialized successfully!
Project ID: {project_id}
API URL: {api_url}
Directory: {os.getcwd()}

Run 'brainvibe track' to start tracking code changes.
""")
    
    return 0 