from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.database import db

router = APIRouter(
    prefix="/api/v1",
    tags=["master-brain"]
)


@router.get("/master-graph", response_model=Dict[str, Any])
async def get_master_brain():
    """
    Get the master brain graph data.
    """
    # Get the master brain data
    master_brain_data = db.get_master_brain_data()
    
    return master_brain_data 