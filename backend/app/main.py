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
    # Try to get from S3
    file_stream = s3_service.get_file(filename)
    if file_stream:
        return StreamingResponse(file_stream, media_type="image/jpeg")

    # Fallback to local if needed
    if os.path.exists(os.path.join(IMAGES_DIR, filename)):
        return FileResponse(os.path.join(IMAGES_DIR, filename))

    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/")
def read_root():
    return {"Hello": "World"}

