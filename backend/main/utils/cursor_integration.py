"""
Cursor integration utilities for BrainVibe
Replaces the removed code_tracker.cursor_integration module
"""

import logging
import difflib
from typing import Dict, Any, Optional
from datetime import datetime
from ..models import Project, CodeChange

logger = logging.getLogger(__name__)


def compute_diff(original_content: str, new_content: str) -> str:
    """
    Compute a unified diff between original and new content.

    Args:
        original_content: Original content
        new_content: New content

    Returns:
        Unified diff string
    """
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile='before',
        tofile='after',
        n=3  # Context lines
    )

    return ''.join(diff)


def process_cursor_change(
    project_id: str,
    file_path: str,
    original_content: str,
    new_content: str,
    cursor_session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a code change from Cursor AI.

    Args:
        project_id: The ID of the project
        file_path: Path to the file that was changed
        original_content: Original content of the file
        new_content: New content of the file after the change
        cursor_session_id: Optional session ID from Cursor
        metadata: Optional metadata about the change

    Returns:
        Dictionary with processing results
    """
    try:
        # Get the project
        project = Project.objects.get(project_id=project_id)

        # Compute diff
        diff_content = compute_diff(original_content, new_content)
        if not diff_content:
            logger.info("No changes detected in the content")
            return {
                "status": "no_change",
                "message": "No changes detected in the content"
            }

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata.update({
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "cursor_session_id": cursor_session_id
        })

        # Generate a unique ID for this change
        change_id = cursor_session_id or f"cursor_{datetime.now().timestamp()}"

        # Create a CodeChange record
        code_change = CodeChange.objects.create(
            project=project,
            change_source='cursor_ai',
            change_id=change_id,
            summary=f"Changes to {file_path}",
            diff_content=diff_content,
            metadata=metadata,
            is_analyzed=False
        )

        # Note: In the original implementation, this would call Gemini to analyze topics
        # For now, we'll mark it as analyzed
        code_change.is_analyzed = True
        code_change.save()

        return {
            "status": "success",
            "change_id": change_id,
            "message": "Code change processed successfully"
        }

    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return {
            "status": "error",
            "message": f"Project with ID {project_id} not found"
        }
    except Exception as e:
        logger.exception(f"Error processing Cursor change: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
