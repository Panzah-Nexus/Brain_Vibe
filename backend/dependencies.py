"""
Dependency providers for the API
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# API key header for authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Environment variable name for the Gemini API key
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

def get_gemini_api_key() -> str:
    """
    Get the Google Gemini API key from the environment
    
    Returns:
        The Gemini API key
        
    Raises:
        HTTPException: If the API key is not set
    """
    api_key = os.environ.get(GEMINI_API_KEY_ENV)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini API key not set. Please set {GEMINI_API_KEY_ENV} environment variable."
        )
    return api_key

async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> str:
    """
    Verify the API key for authenticated endpoints
    
    Args:
        api_key: The API key from the X-API-Key header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid
    """
    # In a real application, you would validate this against a database
    # For simplicity, we're using a hardcoded value or environment variable
    expected_key = os.environ.get("BRAINVIBE_API_KEY", "brainvibe-dev-key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key 