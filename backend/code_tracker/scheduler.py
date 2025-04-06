"""
Module for scheduling periodic code scans.
This allows automatic scanning of repositories for changes without requiring user commits.
"""
import os
import time
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Set up logger
logger = logging.getLogger(__name__)

class ChangeTracker:
    """
    Tracks file changes in a project directory.
    """
    def __init__(self, project_id: str, repo_path: str):
        """
        Initialize a ChangeTracker for a project.
        
        Args:
            project_id: ID of the project to track
            repo_path: Path to the project's repository
        """
        self.project_id = project_id
        self.repo_path = repo_path
        self.file_metadata = {}  # Stores metadata for each tracked file
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        Get the hash of a file's contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            A hash string of the file contents
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return ""
    
    def scan_for_changes(self) -> List[Dict[str, Any]]:
        """
        Scan the repository for changed files.
        
        Returns:
            A list of dictionaries with information about changed files
        """
        logger.info(f"Scanning for changes in project {self.project_id} at {self.repo_path}")
        changed_files = []
        
        try:
            # Walk through the repository
            for root, dirs, files in os.walk(self.repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                # Skip node_modules directory
                if 'node_modules' in dirs:
                    dirs.remove('node_modules')
                
                # Skip virtual environments
                if 'venv' in dirs:
                    dirs.remove('venv')
                if 'env' in dirs:
                    dirs.remove('env')
                
                for file in files:
                    # Skip non-code files
                    if not self._is_code_file(file):
                        continue
                    
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.repo_path)
                    
                    # Get current hash
                    current_hash = self._get_file_hash(full_path)
                    last_modified = os.path.getmtime(full_path)
                    
                    # Check if the file has changed
                    if relative_path in self.file_metadata:
                        old_metadata = self.file_metadata[relative_path]
                        if old_metadata['hash'] != current_hash:
                            changed_files.append({
                                'file_path': relative_path,
                                'full_path': full_path,
                                'last_modified': last_modified,
                                'previous_hash': old_metadata['hash'],
                                'current_hash': current_hash
                            })
                    
                    # Update metadata
                    self.file_metadata[relative_path] = {
                        'hash': current_hash,
                        'last_modified': last_modified
                    }
        
        except Exception as e:
            logger.exception(f"Error scanning for changes: {e}")
        
        logger.info(f"Found {len(changed_files)} changed files")
        return changed_files
    
    def _is_code_file(self, filename: str) -> bool:
        """
        Check if a file is a code file worth tracking.
        
        Args:
            filename: The filename to check
            
        Returns:
            True if the file is a code file, False otherwise
        """
        code_extensions = [
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', 
            '.hpp', '.cs', '.go', '.rb', '.php', '.html', '.css', '.scss', 
            '.sass', '.less', '.vue', '.svelte', '.rs', '.swift', '.kt', 
            '.kts', '.dart', '.elm', '.ex', '.exs', '.erl', '.hrl', '.hs',
            '.scala', '.sc', '.clj', '.cljs', '.cljc', '.sol'
        ]
        
        _, ext = os.path.splitext(filename.lower())
        return ext in code_extensions


class ScheduledScanner:
    """
    Scans projects for changes at scheduled intervals.
    """
    def __init__(self):
        """Initialize the scanner."""
        self.trackers = {}  # Maps project_id to ChangeTracker instances
        self.last_scan_times = {}  # Maps project_id to last scan time
    
    def register_project(self, project_id: str, repo_path: str) -> bool:
        """
        Register a project for scheduled scanning.
        
        Args:
            project_id: ID of the project to register
            repo_path: Path to the project's repository
            
        Returns:
            True if registration succeeded, False otherwise
        """
        try:
            if not os.path.isdir(repo_path):
                logger.error(f"Repository path {repo_path} is not a directory")
                return False
            
            self.trackers[project_id] = ChangeTracker(project_id, repo_path)
            self.last_scan_times[project_id] = datetime.now()
            logger.info(f"Registered project {project_id} for scheduled scanning")
            
            # Perform an initial scan to establish baselines
            self.trackers[project_id].scan_for_changes()
            
            return True
        except Exception as e:
            logger.exception(f"Error registering project {project_id}: {e}")
            return False
    
    def scan_project(self, project_id: str) -> Dict[str, Any]:
        """
        Scan a project for changes.
        
        Args:
            project_id: ID of the project to scan
            
        Returns:
            A dictionary with the scan results
        """
        logger.info(f"Scanning project {project_id}")
        
        if project_id not in self.trackers:
            return {
                "status": "error",
                "message": f"Project {project_id} is not registered for scanning"
            }
        
        try:
            # Update last scan time
            self.last_scan_times[project_id] = datetime.now()
            
            # Scan for changes
            changed_files = self.trackers[project_id].scan_for_changes()
            
            if not changed_files:
                return {
                    "status": "success",
                    "message": "No changes detected",
                    "changed_files": 0
                }
            
            # Process each changed file
            from main.services import analyze_code_change
            
            results = []
            for file_info in changed_files:
                file_path = file_info['file_path']
                full_path = file_info['full_path']
                
                # Read the current content
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {full_path}: {e}")
                    continue
                
                # Compute a diff
                from code_tracker.cursor_integration import compute_diff
                
                # We don't have the original content, so use an empty string
                # This is not ideal, but for scheduled scans it's acceptable
                diff_content = compute_diff("", current_content)
                
                # Analyze the change
                result = analyze_code_change(
                    project_id,
                    file_path,
                    diff_content,
                    'scheduled_scan'
                )
                
                results.append({
                    "file_path": file_path,
                    "analysis_result": result
                })
            
            return {
                "status": "success",
                "message": f"Scanned {len(changed_files)} changed files",
                "changed_files": len(changed_files),
                "results": results
            }
            
        except Exception as e:
            logger.exception(f"Error scanning project {project_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def scan_all_projects(self) -> Dict[str, Any]:
        """
        Scan all registered projects for changes.
        
        Returns:
            A dictionary with the scan results for all projects
        """
        logger.info("Scanning all registered projects")
        
        results = {}
        for project_id in self.trackers:
            results[project_id] = self.scan_project(project_id)
        
        return {
            "status": "success",
            "message": f"Scanned {len(results)} projects",
            "results": results
        }
    
    def scan_due_projects(self, interval_hours: int = 24) -> Dict[str, Any]:
        """
        Scan projects that are due for scanning.
        
        Args:
            interval_hours: Number of hours between scans
            
        Returns:
            A dictionary with the scan results for due projects
        """
        logger.info(f"Scanning projects due for scanning (interval: {interval_hours} hours)")
        
        now = datetime.now()
        due_projects = []
        
        for project_id, last_scan_time in self.last_scan_times.items():
            time_since_last_scan = now - last_scan_time
            if time_since_last_scan > timedelta(hours=interval_hours):
                due_projects.append(project_id)
        
        logger.info(f"Found {len(due_projects)} projects due for scanning")
        
        results = {}
        for project_id in due_projects:
            results[project_id] = self.scan_project(project_id)
        
        return {
            "status": "success",
            "message": f"Scanned {len(results)} due projects",
            "results": results
        }


# Singleton instance of the scanner
scanner = ScheduledScanner() 