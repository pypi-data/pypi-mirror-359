# cyborgdb_service/core/config.py
import os
import secrets
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    # API configuration
    APP_NAME: str = "CyborgDB Service"
    APP_DESCRIPTION: str = "REST API for CyborgDB: The Confidential Vector Database"
    APP_VERSION: str = "0.9.0"
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    API_PREFIX: str = f"/{API_VERSION}"
    
    # Server configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "true").lower() == "true"
    CYBORGDB_API_KEY: Optional[str] = os.getenv("CYBORGDB_API_KEY")

    # Make sure these are settable via .env file
    CYBORGDB_DB_TYPE: Optional[str] = os.getenv("CYBORGDB_DB_TYPE")
    CYBORGDB_CONNECTION_STRING: Optional[str] = os.getenv("CYBORGDB_CONNECTION_STRING")
    
    # CyborgDB configuration
    INDEX_LOCATION: Optional[str] = os.getenv("INDEX_LOCATION")
    CONFIG_LOCATION: Optional[str] = os.getenv("CONFIG_LOCATION")
    ITEMS_LOCATION: Optional[str] = os.getenv("ITEMS_LOCATION")
    INDEX_TABLE_NAME: str = os.getenv("INDEX_TABLE_NAME", "index")
    CONFIG_TABLE_NAME: str = os.getenv("CONFIG_TABLE_NAME", "config")
    ITEMS_TABLE_NAME: str = os.getenv("ITEMS_TABLE_NAME", "items")
    INDEX_CONNECTION_STRING: Optional[str] = os.getenv("INDEX_CONNECTION_STRING")
    CONFIG_CONNECTION_STRING: Optional[str] = os.getenv("CONFIG_CONNECTION_STRING")
    ITEMS_CONNECTION_STRING: Optional[str] = os.getenv("ITEMS_CONNECTION_STRING")
    CPU_THREADS: int = int(os.getenv("CPU_THREADS", "0"))
    GPU_ACCELERATE: bool = os.getenv("GPU_ACCELERATE", "False").lower() == "true"

    # Concurrency settings
    WORKERS: int = int(os.getenv("WORKERS", "0"))  # 0 means auto-calculate based on CPU count

    # Replace the Config class with model_config
    model_config = SettingsConfigDict(env_file=".env")

    # Set fallbacks for locations and connection strings
    @model_validator(mode='after')
    def set_fallbacks(self):
        self.INDEX_LOCATION = self.INDEX_LOCATION or self.CYBORGDB_DB_TYPE
        self.CONFIG_LOCATION = self.CONFIG_LOCATION or self.CYBORGDB_DB_TYPE
        self.ITEMS_LOCATION = self.ITEMS_LOCATION or self.CYBORGDB_DB_TYPE
        self.INDEX_CONNECTION_STRING = self.INDEX_CONNECTION_STRING or self.CYBORGDB_CONNECTION_STRING
        self.CONFIG_CONNECTION_STRING = self.CONFIG_CONNECTION_STRING or self.CYBORGDB_CONNECTION_STRING
        self.ITEMS_CONNECTION_STRING = self.ITEMS_CONNECTION_STRING or self.CYBORGDB_CONNECTION_STRING
        return self

def ensure_api_key():
    """Ensure we have an API key, generating one if necessary."""
    # Check environment variable
    if key := os.getenv("SERVICE_API_KEY"):
        return key
    
    # Check anything else

    # Generate a new API key
    key = secrets.token_urlsafe(32)
    os.environ["SERVICE_API_KEY"] = key

    print("\n   API Key Generated")
    print(f"   Key: {key}")
    print(f"   Saved to environment variable: SERVICE_API_KEY")
    print("   To disable auth: REQUIRE_API_KEY=false\n")
        
settings = Settings()