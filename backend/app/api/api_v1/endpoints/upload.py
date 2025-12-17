import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.s3 import s3_service

router = APIRouter()

@router.post("/image", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image to S3/R2 storage.
    Returns the public URL or object key.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    object_name = f"images/{uuid.uuid4()}.{ext}"

    url = s3_service.upload_file(file.file, object_name)

    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    return {"url": url, "filename": object_name}
