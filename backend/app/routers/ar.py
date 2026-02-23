"""GET /api/ar/session/{design_id}"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.db_models import Design
from app.models.schemas import ARPosition, ARSessionResponse

router = APIRouter(prefix="/api/ar", tags=["ar"])
settings = get_settings()

# Default GLB model served from our static directory.
# # TODO: PRODUCTION — generate per-design GLTF/GLB from furniture layout
_DEFAULT_MODEL_PATH = "/static/models/room_default.glb"


@router.get("/session/{design_id}", response_model=ARSessionResponse, summary="Get AR session data for a design")
async def get_ar_session(
    design_id: str,
    db: AsyncSession = Depends(get_db),
) -> ARSessionResponse:
    design: Design | None = await db.get(Design, design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")

    design_data = json.loads(design.design_json or "{}")
    furniture = design_data.get("furniture", [])

    # Build AR positions from stored furniture layout
    positions = [
        ARPosition(
            furniture_id=f["id"],
            x=f["position"]["x"],
            y=f["position"]["y"],
            z=f["position"]["z"],
            rotation_y=f.get("rotation", 0.0),
        )
        for f in furniture
    ]

    model_url = f"{settings.backend_public_url}{_DEFAULT_MODEL_PATH}"

    return ARSessionResponse(
        design_id=design_id,
        model_url=model_url,
        positions=positions,
        scale_factor=1.0,
        ar_modes="webxr scene-viewer quick-look",
    )
