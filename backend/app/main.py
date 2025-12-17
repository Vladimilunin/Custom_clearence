from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.services.s3 import s3_service
import logging
import sys

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

app = FastAPI(title="Tamozh Gen API")

origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

try:
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ API router loaded successfully")
except Exception as e:
    logger.error(f"❌ Error importing API router: {e}", exc_info=True)

from fastapi.staticfiles import StaticFiles
import os

# Mount images directory
# Prefer the clean mount point /app/images if it exists (Docker)
if os.path.exists("/app/images"):
    IMAGES_DIR = "/app/images"
else:
    # Fallback to local development path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGES_DIR = os.path.join(BASE_DIR, "_фото (эскизы) изделий")

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
    
    # Fallback to local if needed (though S3 is primary for prod)
    # If we really wanted to fallback to local static files, we'd need to check file existence
    # and serve it. But for now, let's assume S3 is the source of truth.
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/")
def read_root():
    return {"Hello": "World"}

