import os
import git
import subprocess
from typing import Optional, Tuple


def get_git_repository(repo_path: str) -> Optional[git.Repo]:
    """
    Get a git repository object from a path.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        git.Repo: A git repository object or None if not found
    """
    try:
        # Check if the path is a git repository
        return git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        print(f"Error: {repo_path} is not a valid Git repository")
        return None
    except git.NoSuchPathError:
        print(f"Error: Path {repo_path} does not exist")
        return None


def get_latest_commit_diff(repo_path: str) -> Tuple[bool, str]:
    """
    Get the diff of the latest commit in a repository.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and the diff or error message
    """
    repo = get_git_repository(repo_path)
    if not repo:
        return False, "Failed to open repository"
    
    try:
        # Get the diff between the latest commit and its parent
        if len(repo.head.commit.parents) > 0:
            diff = repo.git.diff('HEAD~1', 'HEAD')
            return True, diff
        else:
            # For the first commit, get the diff between the empty tree and the commit
            diff = repo.git.diff('4b825dc642cb6eb9a060e54bf8d69288fbee4904', 'HEAD')
            return True, diff
    except git.GitCommandError as e:
        return False, f"Git error: {str(e)}"
    except Exception as e:
        return False, f"Error getting diff: {str(e)}"


def get_diff_between_commits(repo_path: str, old_commit: str, new_commit: str) -> Tuple[bool, str]:
    """
    Get the diff between two commits in a repository.
    
    Args:
        repo_path: Path to the git repository
        old_commit: The older commit hash or reference
        new_commit: The newer commit hash or reference
    
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and the diff or error message
    """
    repo = get_git_repository(repo_path)
    if not repo:
        return False, "Failed to open repository"
    
    try:
        diff = repo.git.diff(old_commit, new_commit)
        return True, diff
    except git.GitCommandError as e:
        return False, f"Git error: {str(e)}"
    except Exception as e:
        return False, f"Error getting diff: {str(e)}"


def get_diff_for_path(repo_path: str, file_path: str) -> Tuple[bool, str]:
    """
    Get the diff for a specific file in the repository compared to the last commit.
    
    Args:
        repo_path: Path to the git repository
        file_path: Path to the file, relative to the repository root
    
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and the diff or error message
    """
    repo = get_git_repository(repo_path)
    if not repo:
        return False, "Failed to open repository"
    
    try:
        # Get the diff between the working directory and the index (staged changes)
        diff = repo.git.diff('HEAD', '--', file_path)
        return True, diff
    except git.GitCommandError as e:
        return False, f"Git error: {str(e)}"
    except Exception as e:
        return False, f"Error getting diff: {str(e)}"


def get_repo_path_from_file(file_path: str) -> Optional[str]:
    """
    Get the repository path from a file path.
    
    Args:
        file_path: Path to a file that might be in a git repository
    
    Returns:
        Optional[str]: The path to the repository root, or None if not found
    """
    try:
        # Use git rev-parse to find the repository root
        cmd = ["git", "-C", os.path.dirname(file_path), "rev-parse", "--show-toplevel"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None 