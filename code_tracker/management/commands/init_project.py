import os
import subprocess
import json
from pathlib import Path
from typing import Optional

class ProjectInitializer:
    def __init__(self, project_path: str, github_repo: Optional[str] = None):
        self.project_path = Path(project_path)
        self.github_repo = github_repo
        self.config_path = self.project_path / '.brainvibe'
        
    def initialize(self) -> bool:
        """Initialize a new project with git tracking and BrainVibe configuration."""
        try:
            # Create .brainvibe directory if it doesn't exist
            self.config_path.mkdir(exist_ok=True)
            
            # Initialize git if not already initialized
            if not (self.project_path / '.git').exists():
                self._run_git_command(['init'])
            
            # Clone or pull from GitHub if repo URL provided
            if self.github_repo:
                if not (self.project_path / '.git').exists():
                    self._run_git_command(['clone', self.github_repo, str(self.project_path)])
                else:
                    self._run_git_command(['pull', 'origin', 'main'])
            
            # Create configuration file
            self._create_config()
            
            # Set up git hooks for tracking changes
            self._setup_git_hooks()
            
            return True
            
        except Exception as e:
            print(f"Error initializing project: {str(e)}")
            return False
    
    def _run_git_command(self, command: list) -> None:
        """Run a git command in the project directory."""
        subprocess.run(['git'] + command, cwd=str(self.project_path), check=True)
    
    def _create_config(self) -> None:
        """Create the BrainVibe configuration file."""
        config = {
            'project_id': str(self.project_path.name),
            'github_repo': self.github_repo,
            'tracking_enabled': True,
            'last_analyzed_commit': None
        }
        
        with open(self.config_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def _setup_git_hooks(self) -> None:
        """Set up git hooks for tracking changes."""
        hooks_dir = self.project_path / '.git' / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        # Create post-commit hook
        hook_content = """#!/bin/sh
python -m code_tracker.management.commands.analyze_diff
"""
        hook_path = hooks_dir / 'post-commit'
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make hook executable
        hook_path.chmod(0o755)

def init_project(project_path: str, github_repo: Optional[str] = None) -> bool:
    """Initialize a new BrainVibe project.
    
    Args:
        project_path: Path to the project directory
        github_repo: Optional GitHub repository URL
        
    Returns:
        bool: True if initialization was successful
    """
    initializer = ProjectInitializer(project_path, github_repo)
    return initializer.initialize() 