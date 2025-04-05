from typing import List, Optional, Set
from pydantic import BaseModel


class TopicBase(BaseModel):
    topic_id: str
    display_name: str
    status: str = "NOT_LEARNED"  # "NOT_LEARNED" or "LEARNED"
    prerequisites: List[str] = []
    short_description: Optional[str] = None
    
    
class Topic(TopicBase):
    projects: List[str] = []  # List of project_ids where this topic appears
    
    
class ProjectBase(BaseModel):
    project_id: str
    name: str
    
    
class Project(ProjectBase):
    topic_ids: List[str] = []
    
    
class DiffAnalysisRequest(BaseModel):
    git_diff: str
    prompt: Optional[str] = None
    ai_output: Optional[str] = None
    
    
class TopicStatusUpdate(BaseModel):
    status: str  # "LEARNED" or "NOT_LEARNED"
    
    
class NewTopic(BaseModel):
    topic_id: str
    display_name: str
    short_description: Optional[str] = None
    prerequisites: List[str] = []
    parent_child_relations: Optional[List[dict]] = None 