"""POST /api/rooms/analyze — upload a room image and get structured analysis."""

from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.db_models import Room
from app.models.schemas import RoomAnalyzeResponse, RoomAnalysis
from app.services.ai_provider import BaseAIProvider, get_ai_provider

router = APIRouter(prefix="/api/rooms", tags=["rooms"])
settings = get_settings()

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@router.post("/analyze", response_model=RoomAnalyzeResponse, summary="Upload and analyse a room image")
async def analyze_room(
    file: UploadFile = File(..., description="Room photograph (JPEG / PNG / WEBP)"),
    db: AsyncSession = Depends(get_db),
    ai: BaseAIProvider = Depends(get_ai_provider),
) -> RoomAnalyzeResponse:
    # ── Validate ─────────────────────────────────────────────────────────────
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > settings.upload_max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.upload_max_mb} MB limit")

    # ── Save upload ───────────────────────────────────────────────────────────
    os.makedirs(settings.uploads_dir, exist_ok=True)
    safe_name = os.path.basename(file.filename or "upload.jpg")
    upload_path = os.path.join(settings.uploads_dir, safe_name)
    with open(upload_path, "wb") as f:
        f.write(image_bytes)
    file_url = f"{settings.backend_public_url}/static/uploads/{safe_name}"

    # ── AI analysis ───────────────────────────────────────────────────────────
    analysis_raw = await ai.analyze_room(image_bytes, file.filename or "upload")

    # ── Persist ───────────────────────────────────────────────────────────────
    room = Room(
        filename=safe_name,
        file_url=file_url,
        analysis_json=json.dumps(analysis_raw),
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    analysis = RoomAnalysis(**analysis_raw)
    return RoomAnalyzeResponse(
        room_id=room.id,
        filename=room.filename,
        file_url=room.file_url,
        analysis=analysis,
        created_at=room.created_at,
    )
