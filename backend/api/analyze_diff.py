"""
API endpoints for analyzing code diffs
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
import logging

from ..models.project import Project
from ..models.topic import Topic
from ..code_analyzer.diff_analyzer import DiffAnalyzer
from ..dependencies import get_gemini_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/projects/{project_id}/analyze-diff/")
async def analyze_diff(
    project_id: str,
    data: Dict[str, Any] = Body(...),
    gemini_api_key: str = Depends(get_gemini_api_key)
) -> Dict[str, Any]:
    """
    Analyze a code diff to extract programming topics
    
    Args:
        project_id: ID of the project
        data: Dictionary containing diff_content and optionally file_path and change_id
        gemini_api_key: Google Gemini API key from dependencies
        
    Returns:
        Dictionary containing the analysis results
    """
    # Validate the project ID
    project = Project.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Extract the diff content from the request
    diff_content = data.get("diff_content", "")
    if not diff_content:
        return {"topics_extracted": 0, "topics": [], "error": "No diff content provided"}
    
    # Get optional parameters
    file_path = data.get("file_path")
    change_id = data.get("change_id", "unknown")
    
    # Log info about the request
    logger.info(f"Analyzing diff for project {project_id}, change ID {change_id}")
    if file_path:
        logger.info(f"File: {file_path}")
    
    # Initialize the analyzer
    analyzer = DiffAnalyzer(gemini_api_key=gemini_api_key)
    
    # Analyze the diff
    try:
        result = analyzer.analyze_diff(
            project_id=project_id,
            diff_content=diff_content,
            file_path=file_path
        )
        
        # Log the results
        logger.info(f"Extracted {result['topics_extracted']} topics from {file_path or 'unknown file'}")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing diff: {str(e)}")

@router.get("/projects/{project_id}/topics/{topic_id}/generate-tutorial")
async def generate_tutorial(
    project_id: str,
    topic_id: str,
    gemini_api_key: str = Depends(get_gemini_api_key)
) -> Dict[str, Any]:
    """
    Generate a tutorial for a specific topic using Gemini
    
    Args:
        project_id: ID of the project
        topic_id: ID of the topic
        gemini_api_key: Google Gemini API key from dependencies
        
    Returns:
        Dictionary containing the tutorial
    """
    # Check if the project exists
    project = Project.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Check if the topic exists
    topic = Topic.get_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    # Check if the topic belongs to the project
    if topic.project_id != project_id:
        raise HTTPException(status_code=403, detail=f"Topic {topic_id} does not belong to project {project_id}")
    
    # TODO: Implement tutorial generation with Gemini (future feature)
    # For now, return a placeholder
    return {
        "topic_id": topic_id,
        "title": topic.title,
        "tutorial": f"Tutorial content for {topic.title} will be generated using Gemini in a future update."
    } 