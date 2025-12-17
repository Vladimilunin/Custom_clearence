from fastapi import APIRouter
from app.api.api_v1.endpoints import parts, invoices, upload

api_router = APIRouter()
api_router.include_router(parts.router, prefix="/parts", tags=["parts"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
