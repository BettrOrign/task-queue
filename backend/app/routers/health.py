from fastapi import APIRouter, HTTPException, status

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "task-queue-api",
        "version": "0.1.0",
        "api_prefix": settings.api_v1_str,
    }