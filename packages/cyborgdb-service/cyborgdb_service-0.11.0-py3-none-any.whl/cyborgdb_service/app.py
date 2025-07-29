from fastapi import FastAPI
from contextlib import asynccontextmanager

from cyborgdb_service.core.config import settings
from cyborgdb_service.api.routes.health import router as health_router
from cyborgdb_service.api.routes.indexes import router as indexes_router
from cyborgdb_service.api.routes.vectors import router as vectors_router
from cyborgdb_service.db.client import initialize_client

# Define the lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (was previously in on_event)
    initialize_client()
    
    yield  # Application runs here
    
    # Cleanup code (if any) would go here
    # For example: close connections, release resources, etc.

# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan  # Use the new lifespan handler
)

# Include routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(indexes_router, prefix=settings.API_PREFIX)
app.include_router(vectors_router, prefix=settings.API_PREFIX)