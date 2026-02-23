"""POST /api/agent/procure — SSE streaming procurement agent."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import Design
from app.models.schemas import ProcureRequest
from app.services.ai_provider import BaseAIProvider, get_ai_provider

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/procure", summary="Stream procurement agent events via SSE")
async def procure(
    body: ProcureRequest,
    db: AsyncSession = Depends(get_db),
    ai: BaseAIProvider = Depends(get_ai_provider),
) -> StreamingResponse:
    design: Design | None = await db.get(Design, body.design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")

    design_data = json.loads(design.design_json or "{}")

    async def _event_stream():
        try:
            async for event in ai.procure(
                design=design_data,
                budget=body.budget_usd,
                vendors=body.preferred_vendors,
            ):
                # SSE format: "data: <json>\n\n"
                payload = json.dumps({"event": event["event"], "data": event["data"]})
                yield f"data: {payload}\n\n"
        except Exception as exc:
            error_payload = json.dumps({"event": "error", "data": str(exc)})
            yield f"data: {error_payload}\n\n"
        finally:
            yield "data: {\"event\": \"done\", \"data\": null}\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",          # disable nginx buffering (if ever added)
            "Connection": "keep-alive",
        },
    )
