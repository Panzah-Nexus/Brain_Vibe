"""
Git Utilities for Code Analysis

This module provides utilities for working with Git repositories and diffs.
"""

import os
import re
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

def get_git_diff(repo_path: str, commit_hash: Optional[str] = None, 
                previous_hash: Optional[str] = None,
                file_path: Optional[str] = None) -> str:
    """
    Get the git diff for a specific commit or between two commits.
    
    Args:
        repo_path: Path to the Git repository
        commit_hash: The commit hash to get the diff for (current changes if None)
        previous_hash: The previous commit hash to compare with
        file_path: Optional path to a specific file to get diff for
        
    Returns:
        The diff content as a string
    """
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        cmd = ['git']
        
        if commit_hash is None and previous_hash is None:
            # Get unstaged changes
            cmd.extend(['diff'])
        elif commit_hash and previous_hash is None:
            # Get diff for a specific commit
            cmd.extend(['show', commit_hash])
        elif commit_hash and previous_hash:
            # Get diff between two commits
            cmd.extend(['diff', f'{previous_hash}..{commit_hash}'])
        
        # Add file path if specified
        if file_path:
            cmd.append('--')
            cmd.append(file_path)
        
        # Run the git command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        return process.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return ""
    except Exception as e:
        logger.error(f"Error getting git diff: {str(e)}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return ""

def get_recent_commits(repo_path: str, count: int = 10) -> List[Dict[str, str]]:
    """
    Get the most recent commits from a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        count: Number of commits to retrieve
        
    Returns:
        A list of dictionaries containing commit information
    """
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Format: hash, author name, author email, date, subject
        format_str = "--pretty=format:%H|%an|%ae|%ad|%s"
        
        # Run the git command
        process = subprocess.run(
            ['git', 'log', format_str, f'-{count}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        # Parse the output into a list of dictionaries
        commits = []
        for line in process.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author_name': parts[1],
                    'author_email': parts[2],
                    'date': parts[3],
                    'subject': parts[4]
                })
        
        return commits
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return []
    except Exception as e:
        logger.error(f"Error getting recent commits: {str(e)}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return []

def get_commit_files(repo_path: str, commit_hash: str) -> List[str]:
    """
    Get the list of files changed in a specific commit.
    
    Args:
        repo_path: Path to the Git repository
        commit_hash: The commit hash
        
    Returns:
        A list of file paths
    """
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Run the git command
        process = subprocess.run(
            ['git', 'show', '--name-only', '--pretty=format:', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        # Parse the output into a list of file paths
        files = [file for file in process.stdout.strip().split('\n') if file]
        return files
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return []
    except Exception as e:
        logger.error(f"Error getting commit files: {str(e)}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return []

def parse_diff_summary(diff_content: str) -> Dict[str, Any]:
    """
    Parse a git diff and extract summary information.
    
    Args:
        diff_content: The diff content as a string
        
    Returns:
        A dictionary containing summary information about the diff
    """
    if not diff_content:
        return {
            'files_changed': 0,
            'insertions': 0,
            'deletions': 0,
            'file_summaries': []
        }
    
    # Extract file paths and changes
    file_pattern = r'diff --git a/(.*) b/(.*)'
    file_matches = re.finditer(file_pattern, diff_content)
    
    files_changed = 0
    total_insertions = 0
    total_deletions = 0
    file_summaries = []
    
    current_file = None
    
    for line in diff_content.split('\n'):
        # Check for file changes
        file_match = re.match(file_pattern, line)
        if file_match:
            files_changed += 1
            current_file = file_match.group(2)  # Use the 'b' path
            file_summaries.append({
                'file': current_file,
                'insertions': 0,
                'deletions': 0
            })
        
        # Count insertions and deletions
        if line.startswith('+') and not line.startswith('+++'):
            total_insertions += 1
            if current_file and file_summaries:
                file_summaries[-1]['insertions'] += 1
        elif line.startswith('-') and not line.startswith('---'):
            total_deletions += 1
            if current_file and file_summaries:
                file_summaries[-1]['deletions'] += 1
    
    return {
        'files_changed': files_changed,
        'insertions': total_insertions,
        'deletions': total_deletions,
        'file_summaries': file_summaries
    }

def is_valid_git_repo(repo_path: str) -> bool:
    """
    Check if a path is a valid Git repository.
    
    Args:
        repo_path: Path to check
        
    Returns:
        True if the path is a valid Git repository, False otherwise
    """
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Run the git command
        process = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        return process.returncode == 0 and process.stdout.strip() == 'true'
    except Exception as e:
        logger.error(f"Error checking if valid git repo: {str(e)}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return False

def get_repo_info(repo_path: str) -> Dict[str, Any]:
    """
    Get information about a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        A dictionary containing repository information
    """
    if not is_valid_git_repo(repo_path):
        return {
            'is_valid': False
        }
    
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Get remote origin URL
        try:
            remote_process = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True,
                check=False
            )
            remote_url = remote_process.stdout.strip() if remote_process.returncode == 0 else None
        except:
            remote_url = None
        
        # Get current branch
        try:
            branch_process = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=False
            )
            current_branch = branch_process.stdout.strip() if branch_process.returncode == 0 else None
        except:
            current_branch = None
        
        # Get last commit hash
        try:
            hash_process = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=False
            )
            last_commit_hash = hash_process.stdout.strip() if hash_process.returncode == 0 else None
        except:
            last_commit_hash = None
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        return {
            'is_valid': True,
            'remote_url': remote_url,
            'current_branch': current_branch,
            'last_commit_hash': last_commit_hash
        }
    except Exception as e:
        logger.error(f"Error getting repo info: {str(e)}")
        # Change back to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return {
            'is_valid': False,
            'error': str(e)
        } 