"""
Design generation and render endpoints.

POST /api/designs/generate
POST /api/designs/render
GET  /api/designs/render/{job_id}
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.db_models import Design, RenderJob, Room
from app.models.schemas import (
    DesignGenerateRequest,
    DesignGenerateResponse,
    FurniturePiece,
    RenderJobResponse,
    RenderRequest,
)
from app.services.ai_provider import BaseAIProvider, get_ai_provider
from app.services.render_queue import get_render_queue, RenderQueue

router = APIRouter(prefix="/api/designs", tags=["designs"])
settings = get_settings()


# ── POST /api/designs/generate ────────────────────────────────────────────────

@router.post("/generate", response_model=DesignGenerateResponse, summary="Generate a furniture design for a room")
async def generate_design(
    body: DesignGenerateRequest,
    db: AsyncSession = Depends(get_db),
    ai: BaseAIProvider = Depends(get_ai_provider),
) -> DesignGenerateResponse:
    # Look up room & analysis
    result = await db.get(Room, body.room_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Room not found")

    room: Room = result
    analysis = json.loads(room.analysis_json or "{}")

    # Generate design via AI
    design_raw = await ai.generate_design(analysis, body.style, body.preferences)

    # Persist
    design = Design(
        room_id=room.id,
        style=body.style,
        design_json=json.dumps(design_raw),
    )
    db.add(design)
    await db.commit()
    await db.refresh(design)

    furniture = [FurniturePiece(**f) for f in design_raw["furniture"]]

    return DesignGenerateResponse(
        design_id=design.id,
        room_id=room.id,
        style=body.style,
        furniture=furniture,
        layout_notes=design_raw.get("layout_notes", ""),
        color_palette=design_raw.get("color_palette", []),
        estimated_cost_usd=design_raw.get("estimated_cost_usd", 0.0),
        created_at=design.created_at,
    )


# ── POST /api/designs/render ──────────────────────────────────────────────────

@router.post("/render", response_model=RenderJobResponse, summary="Submit a render job for a design")
async def submit_render(
    body: RenderRequest,
    db: AsyncSession = Depends(get_db),
    ai: BaseAIProvider = Depends(get_ai_provider),
    queue: RenderQueue = Depends(get_render_queue),
) -> RenderJobResponse:
    # Look up design
    design: Design | None = await db.get(Design, body.design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")

    design_data = json.loads(design.design_json or "{}")

    # Generate a shared job_id so DB record and queue entry stay in sync
    job_id = str(uuid.uuid4())

    # Persist job record with stable ID
    job_record = RenderJob(id=job_id, design_id=design.id, status="pending")
    db.add(job_record)
    await db.commit()

    # Submit to async queue using the same job_id
    queued = await queue.submit(
        design_id=design.id,
        design_data=design_data,
        ai_provider=ai,
        renders_dir=settings.renders_dir,
        backend_public_url=settings.backend_public_url,
        job_id=job_id,
    )

    return RenderJobResponse(
        job_id=queued.job_id,
        design_id=design.id,
        status=queued.status,
        image_url=queued.image_url,
        error=queued.error,
        created_at=queued.created_at,
    )


# ── GET /api/designs/render/{job_id} ─────────────────────────────────────────

@router.get("/render/{job_id}", response_model=RenderJobResponse, summary="Poll render job status")
async def get_render_status(
    job_id: str,
    queue: RenderQueue = Depends(get_render_queue),
) -> RenderJobResponse:
    job = queue.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Render job not found")

    return RenderJobResponse(
        job_id=job.job_id,
        design_id=job.design_id,
        status=job.status,
        image_url=job.image_url,
        error=job.error,
        created_at=job.created_at,
    )
