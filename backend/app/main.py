from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.router import api_router
from app.cache.redis import close_redis_client, get_redis_client
from app.core.config import settings
from app.db.init_db import init_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sou_disha")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SOU 3D Disha backend services...")
    # Initialize database tables and initial seed data
    try:
        await init_database()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

    # Initialize Redis connection
    try:
        await get_redis_client()
    except Exception as e:
        logger.warning(f"Redis initialization warning: {e}")

    yield

    logger.info("Shutting down SOU 3D Disha backend services...")
    await close_redis_client()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-oriented 3D campus navigation and information platform API for Silver Oak University.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount frontend files if present in parent directory or frontend dir
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
index_file = os.path.join(root_dir, "index.html")


@app.get("/", summary="Root index or Frontend UI")
async def root():
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


# Serve only the public frontend assets; never mount the workspace root.
for filename in ["styles.css", "app.js", "three-scene.js", "orbit-controls.js", "manifest.json"]:
    file_path = os.path.join(root_dir, filename)
    if os.path.isfile(file_path):
        def make_route(fp):
            async def serve_file():
                return FileResponse(fp)
            return serve_file
        app.add_api_route(f"/{filename}", make_route(file_path), methods=["GET"], include_in_schema=False)
