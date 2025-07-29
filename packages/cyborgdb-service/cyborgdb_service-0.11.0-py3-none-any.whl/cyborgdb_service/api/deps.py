from fastapi import Depends, Path

from cyborgdb_service.core.security import get_api_key
from cyborgdb_service.db.client import get_client, load_index
from cyborgdb_service.api.schemas.index import IndexOperationRequest

def get_current_client(api_key: str = Depends(get_api_key)):
    """
    Get the current CyborgDB client instance.
    Optionally requires a valid API key, depending on configuration.
    """
    return get_client()

async def get_index(
    index_name: str = Path(...), 
    request: IndexOperationRequest = None,
    api_key: str = Depends(get_api_key)
):
    """
    Load an index by name with the provided encryption key.
    Optionally requires a valid API key, depending on configuration.
    """
    return load_index(index_name, request.index_key)