"""
Main FastAPI application for BrainVibe
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import verify_api_key
from .api import projects, topics, analyze_diff

app = FastAPI(
    title="BrainVibe API",
    description="API for BrainVibe - Track code changes and learn as you go",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(
    projects.router,
    prefix="/api",
    tags=["projects"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    topics.router,
    prefix="/api",
    tags=["topics"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    analyze_diff.router,
    prefix="/api",
    tags=["code-analysis"],
    dependencies=[Depends(verify_api_key)]
)

@app.get("/")
async def root():
    """Root endpoint for the API"""
    return {
        "app": "BrainVibe API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 