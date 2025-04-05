from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.models import Topic, TopicStatusUpdate
from app.database import db

router = APIRouter(
    prefix="/api/v1/topics",
    tags=["topics"]
)


@router.get("", response_model=List[Topic])
async def get_topics():
    """
    Get all topics.
    """
    topics = db.get_all_topics()
    return list(topics.values())


@router.get("/{topic_id}", response_model=Dict[str, Any])
async def get_topic(topic_id: str):
    """
    Get a topic by ID.
    """
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic


@router.post("/{topic_id}/complete", response_model=Dict[str, Any])
async def complete_topic(topic_id: str, update: TopicStatusUpdate):
    """
    Mark a topic as completed.
    """
    # Check if topic exists
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Update the topic status
    success = db.update_topic_status(topic_id, update.status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update topic status")
    
    # Get the updated topic
    updated_topic = db.get_topic(topic_id)
    
    return updated_topic


@router.get("/{topic_id}/projects", response_model=List[Dict[str, Any]])
async def get_topic_projects(topic_id: str):
    """
    Get all projects that contain a topic.
    """
    # Check if topic exists
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get the projects for the topic
    project_ids = topic.get("projects", [])
    projects = [db.get_project(project_id) for project_id in project_ids if db.get_project(project_id)]
    
    return projects 