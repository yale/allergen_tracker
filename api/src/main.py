"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import HealthResponse
from routes.allergens import router as allergens_router
from routes.meals import router as meals_router
from routes.websocket import router as websocket_router
from services.realtime_listener import AllergenCache
from websocket.connection_manager import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - start/stop Firebase listener."""
    import asyncio

    # Startup
    # Set the event loop for WebSocket broadcasts from Firebase callback thread
    manager = ConnectionManager.get_instance()
    manager.set_event_loop(asyncio.get_event_loop())

    cache = AllergenCache.get_instance()
    cache.start_listener()
    logger.info("Application startup complete")
    yield
    # Shutdown
    cache.stop_listener()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Allergen Tracker API",
    description="API for tracking allergen exposure in baby food entries",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend
# In production with nginx proxy, requests come from same origin
# These origins are for local development
import os
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(allergens_router, prefix="/api")
app.include_router(meals_router, prefix="/api")
app.include_router(websocket_router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="API is running")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
