import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from .management.commands.init_project import init_project

class CursorIntegration:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / '.brainvibe'
        self.cursor_config_path = self.workspace_path / '.cursor'
        
    def setup_cursor_integration(self) -> bool:
        """Set up Cursor integration for the current workspace."""
        try:
            # Create Cursor configuration if it doesn't exist
            if not self.cursor_config_path.exists():
                self._create_cursor_config()
            
            # Initialize BrainVibe project if not already initialized
            if not self.config_path.exists():
                return init_project(str(self.workspace_path))
            
            return True
            
        except Exception as e:
            print(f"Error setting up Cursor integration: {str(e)}")
            return False
    
    def _create_cursor_config(self) -> None:
        """Create Cursor configuration file."""
        config = {
            'brainvibe': {
                'enabled': True,
                'auto_track': True,
                'project_id': str(self.workspace_path.name)
            }
        }
        
        self.cursor_config_path.mkdir(exist_ok=True)
        with open(self.cursor_config_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def track_changes(self, file_path: str, content: str) -> None:
        """Track changes made in Cursor.
        
        Args:
            file_path: Path to the changed file
            content: New content of the file
        """
        try:
            # Get the relative path from workspace root
            rel_path = os.path.relpath(file_path, str(self.workspace_path))
            
            # Create or update the file in the workspace
            full_path = self.workspace_path / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            # Stage the changes in git
            self._run_git_command(['add', rel_path])
            
            # Create a commit with a meaningful message
            self._run_git_command(['commit', '-m', f'Cursor change: {rel_path}'])
            
        except Exception as e:
            print(f"Error tracking changes: {str(e)}")
    
    def _run_git_command(self, command: list) -> None:
        """Run a git command in the workspace directory."""
        import subprocess
        subprocess.run(['git'] + command, cwd=str(self.workspace_path), check=True)

def setup_cursor_workspace(workspace_path: str) -> bool:
    """Set up Cursor workspace with BrainVibe integration.
    
    Args:
        workspace_path: Path to the Cursor workspace
        
    Returns:
        bool: True if setup was successful
    """
    integration = CursorIntegration(workspace_path)
    return integration.setup_cursor_integration() 