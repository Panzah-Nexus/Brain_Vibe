from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.models import Project, ProjectBase, DiffAnalysisRequest
from app.database import db
from app.services.gemini_service import analyze_code_diff
from app.services.graph_service import process_topics_from_gemini

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["projects"]
)


@router.post("", response_model=Project)
async def create_project(project: ProjectBase):
    """
    Create a new project.
    """
    # Check if project already exists
    if db.get_project(project.project_id):
        raise HTTPException(status_code=400, detail="Project already exists")
    
    # Create the project
    project_data = {
        "project_id": project.project_id,
        "name": project.name,
        "topic_ids": []
    }
    
    db.save_project(project.project_id, project_data)
    
    return project_data


@router.get("", response_model=List[Project])
async def get_projects():
    """
    Get all projects.
    """
    projects = db.get_all_projects()
    return list(projects.values())


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """
    Get a project by ID.
    """
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.post("/{project_id}/analyze-diff", response_model=Dict[str, Any])
async def analyze_diff(project_id: str, request: DiffAnalysisRequest):
    """
    Analyze a code diff for a project.
    """
    # Check if project exists
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Analyze the diff using Gemini
    gemini_response = analyze_code_diff(
        git_diff=request.git_diff,
        prompt=request.prompt,
        ai_output=request.ai_output
    )
    
    # Process the topics from Gemini
    new_topics = process_topics_from_gemini(project_id, gemini_response)
    
    # Return the response
    return {
        "project_id": project_id,
        "new_topics": new_topics
    }


@router.get("/{project_id}/topics", response_model=List[Dict[str, Any]])
async def get_project_topics(project_id: str):
    """
    Get all topics for a project.
    """
    # Check if project exists
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the project topics
    topics = db.get_project_topics(project_id)
    
    return topics


@router.get("/{project_id}/graph", response_model=Dict[str, Any])
async def get_project_graph(project_id: str):
    """
    Get the graph data for a project.
    """
    # Check if project exists
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the project graph data
    graph_data = db.get_project_graph_data(project_id)
    
    return graph_data 