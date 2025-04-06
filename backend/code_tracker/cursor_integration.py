"""
Module for integrating with Cursor AI/IDE.
Provides functionality to capture code changes made by Cursor AI.
"""
import json
import logging
import hashlib
import difflib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)

def generate_change_id(content: str, timestamp: float = None) -> str:
    """
    Generate a unique ID for a code change based on content and timestamp.
    
    Args:
        content: The content of the change
        timestamp: Optional timestamp to include in the hash
        
    Returns:
        A unique string ID for the change
    """
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    
    # Create a hash of the content and timestamp
    hash_input = f"{content}_{timestamp}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:24]


def compute_diff(original_content: str, new_content: str) -> str:
    """
    Compute a unified diff between original and new content.
    
    Args:
        original_content: The original content
        new_content: The new content
        
    Returns:
        A unified diff string
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
    Process a code change made by Cursor AI.
    
    Args:
        project_id: The ID of the project
        file_path: Path to the file that was changed
        original_content: Original content of the file
        new_content: New content of the file after the change
        cursor_session_id: Optional session ID from Cursor
        metadata: Optional metadata about the change
        
    Returns:
        A dictionary with information about the processed change
    """
    # Import inside the function to avoid circular imports
    from main.models import Project, CodeChange
    from main.utils import llm_utils
    
    logger.info(f"Processing Cursor change for project {project_id}, file {file_path}")
    
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
        change_id = cursor_session_id or generate_change_id(diff_content)
        
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
        
        # Analyze the change to extract topics
        topics = llm_utils.analyze_diff(diff_content, {"project_id": project_id})
        
        # Process and save the extracted topics
        from main.services import process_and_save_topics
        result = process_and_save_topics(project_id, topics)
        
        # Update the CodeChange record to mark it as analyzed
        code_change.is_analyzed = True
        code_change.save()
        
        # Add the extracted topics to the CodeChange record
        if topics:
            from main.models import Topic
            for topic_data in topics:
                topic_id = topic_data.get("topic_id")
                if topic_id:
                    try:
                        topic = Topic.objects.get(topic_id=topic_id)
                        code_change.extracted_topics.add(topic)
                    except Topic.DoesNotExist:
                        logger.warning(f"Topic with ID {topic_id} not found")
        
        return {
            "status": "success",
            "change_id": change_id,
            "topics_extracted": len(topics),
            "topics": topics
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