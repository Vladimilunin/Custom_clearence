import logging
import sys

from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from app.services.s3 import s3_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("--- STARTUP CONFIG CHECK ---")
    print(f"GROQ_API_KEY present: {bool(settings.GROQ_API_KEY)}")
    if settings.GROQ_API_KEY:
        print(f"GROQ_API_KEY value: {settings.GROQ_API_KEY[:10]}...")
    else:
        print("GROQ_API_KEY IS MISSING!")
    print("----------------------------")
    yield
    # Shutdown

app = FastAPI(
    title="Tamozh Gen API",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Content-Disposition"],
    expose_headers=["Content-Disposition"],
)

try:
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ API router loaded successfully")
except Exception as e:
    logger.error(f"❌ Error importing API router: {e}", exc_info=True)

import os

from fastapi.staticfiles import StaticFiles

# Mount images directory
# Prefer the clean mount point /app/images if it exists (Docker)
if os.path.exists("/app/images"):
    IMAGES_DIR = "/app/images"
else:
    # Fallback to local development path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGES_DIR = os.path.join(BASE_DIR, "_изображения")

if os.path.exists(IMAGES_DIR):
    logger.info(f"Mounting images from {IMAGES_DIR}")
    app.mount("/images_local", StaticFiles(directory=IMAGES_DIR), name="images_local")
else:
    logger.warning(f"Images directory not found at {IMAGES_DIR}")

@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Get image from S3/MinIO with caching headers.
    
    Implements:
    - In-memory caching via S3Service
    - Cache-Control headers for browser caching (1 day)
    - Content-type detection based on extension
    - Fallback to local filesystem
    """
    import mimetypes
    
    # Determine content type from filename
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "image/jpeg"  # Default fallback
    
    # Cache headers for browser caching
    cache_headers = {
        "Cache-Control": "public, max-age=86400",  # 1 day
        "Content-Type": content_type,
    }
    
    # Try to get from S3 (uses internal LRU cache)
    file_stream = s3_service.get_file(filename)
    if file_stream:
        return StreamingResponse(
            file_stream, 
            media_type=content_type,
            headers=cache_headers
        )

    # Fallback to local if needed
    if os.path.exists(os.path.join(IMAGES_DIR, filename)):
        return FileResponse(
            os.path.join(IMAGES_DIR, filename),
            headers=cache_headers
        )

    raise HTTPException(status_code=404, detail="Image not found")


@app.get("/api/cache-stats")
async def get_cache_stats():
    """Get S3 cache statistics for monitoring."""
    return s3_service.cache_stats


@app.get("/api/db-pool-stats")
async def get_db_pool_stats():
    """Get database connection pool statistics for monitoring."""
    from app.db.session import get_pool_status
    return get_pool_status()


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Checks:
    - Database connectivity
    - S3 storage availability
    """
    from app.db.session import AsyncSessionLocal
    
    status = {
        "status": "healthy",
        "database": "unknown",
        "storage": "unknown",
        "cache": s3_service.cache_stats,
    }
    
    # Check database
    try:
        async with AsyncSessionLocal() as db:
            await db.execute("SELECT 1")
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Check S3/MinIO
    try:
        # Just check if we can access the bucket
        s3_service.s3_client.head_bucket(Bucket=s3_service.bucket_name)
        status["storage"] = "connected"
    except Exception as e:
        status["storage"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    return status


@app.get("/")
def read_root():
    return {"Hello": "World"}


# Global exception handler for custom exceptions
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handle custom application errors with structured response."""
    return JSONResponse(
        status_code=400 if exc.code == "VALIDATION_ERROR" else 
                    404 if exc.code == "NOT_FOUND" else
                    429 if exc.code == "RATE_LIMIT" else 500,
        content=exc.to_dict()
    )
