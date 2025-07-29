from typing import Dict
from fastapi import APIRouter

from cyborgdb_service.core.config import settings

router = APIRouter()

@router.get("/health", response_model=Dict[str, str], summary="Health check endpoint")
async def health_check():
    """
    Check if the API is running.
    """
    return {
        "status": "healthy", 
        "api_version": settings.API_VERSION,
        "version": settings.APP_VERSION
    }