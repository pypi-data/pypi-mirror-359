from fastapi import Security, HTTPException, status, Header
from fastapi.security import APIKeyHeader
from typing import Optional

from cyborgdb_service.core.config import settings

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)  # Changed to non-auto error

# Helper function to convert hex key to bytes
def hex_to_bytes(hex_key):
    """
    Convert hex string to bytes for encryption key.
    """
    try:
        return bytes.fromhex(hex_key)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hex string for encryption key"
        ) from exc

def get_api_key(api_key: Optional[str] = Security(api_key_header)):
    """
    Validate the API key from the request header.
    Skip validation if REQUIRE_API_KEY is False.
    """
    if not settings.REQUIRE_API_KEY:
        return None
        
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required"
        )
        
    if api_key != settings.CYBORGDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
        
    return api_key