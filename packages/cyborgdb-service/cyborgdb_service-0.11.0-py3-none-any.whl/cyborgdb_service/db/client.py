import threading
from fastapi import HTTPException, status
import os

try:
    # Attempt to import cyborgdb_core first
    import cyborgdb_core as cyborgdb
except ImportError:
    # If that fails, fall back to cyborgdb_lite
    import cyborgdb_lite as cyborgdb
    from cyborgdb_lite import Client, DBConfig
else:
    from cyborgdb_core import Client, DBConfig

from cyborgdb_service.core.config import settings
from cyborgdb_service.core.security import hex_to_bytes

# Thread-local storage for client instancesAdd commentMore actions
_thread_local = threading.local()

def initialize_client():
    """
    Initialize the CyborgDB client.
    """
    
    try:
        # Initialize client with settings from config
        index_location = DBConfig(
            location=settings.INDEX_LOCATION,
            table_name = settings.INDEX_TABLE_NAME,
            connection_string=settings.INDEX_CONNECTION_STRING,
        )
        config_location = DBConfig(
            location=settings.CONFIG_LOCATION,
            table_name = settings.CONFIG_TABLE_NAME,
            connection_string=settings.CONFIG_CONNECTION_STRING,
        )
        items_location = DBConfig(
            location=settings.ITEMS_LOCATION,
            table_name = settings.ITEMS_TABLE_NAME,
            connection_string=settings.ITEMS_CONNECTION_STRING,
        )
        
        client = Client(
            api_key=settings.CYBORGDB_API_KEY,
            index_location=index_location,
            config_location=config_location,
            items_location=items_location,
            cpu_threads=settings.CPU_THREADS,
            gpu_accelerate=settings.GPU_ACCELERATE
        )
        
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize CyborgDB client: {str(e)}"
        )

def get_client():
    """
    Get the CyborgDB client instance. Thread-safe implementation.
    """
    # Check if the current thread has a client
    if not hasattr(_thread_local, "client"):
        # If not, create one for this thread
        _thread_local.client = initialize_client()
    
    return _thread_local.client

def load_index(index_name: str, index_key_hex: str):
    """
    Load an index with the provided encryption key.
    """
    current_client = get_client()
    index_key = hex_to_bytes(index_key_hex)
    
    try:
        return current_client.load_index(index_name=index_name, index_key=index_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index not found: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load index: {str(e)}"
        )

def create_index_config(config_data):
    """
    Create the appropriate IndexConfig object from request data.
    """
    try:
        if config_data.type == "ivf":
            return cyborgdb.IndexIVF(
                dimension=config_data.dimension,
                n_lists=config_data.n_lists,
                metric=config_data.metric
            )
        elif config_data.type == "ivfpq":
            return cyborgdb.IndexIVFPQ(
                dimension=config_data.dimension,
                n_lists=config_data.n_lists,
                pq_dim=config_data.pq_dim,
                pq_bits=config_data.pq_bits,
                metric=config_data.metric
            )
        elif config_data.type == "ivfflat":
            return cyborgdb.IndexIVFFlat(
                dimension=config_data.dimension,
                n_lists=config_data.n_lists,
                metric=config_data.metric
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported index type: {config_data.type}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create index config: {str(e)}"
        )