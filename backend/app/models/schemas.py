"""Pydantic v2 schemas (request / response)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Shared ────────────────────────────────────────────────────────────────────

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Room ──────────────────────────────────────────────────────────────────────

class RoomDimensions(BaseModel):
    width: float = Field(..., description="Width in metres")
    height: float = Field(..., description="Ceiling height in metres")
    depth: float = Field(..., description="Depth in metres")


class RoomAnalysis(BaseModel):
    room_type: str
    dimensions: RoomDimensions
    lighting: str
    existing_features: list[str]
    style_hints: list[str]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class RoomAnalyzeResponse(BaseSchema):
    room_id: str
    filename: str
    file_url: str | None
    analysis: RoomAnalysis
    created_at: datetime


# ── Design ────────────────────────────────────────────────────────────────────

class FurniturePiece(BaseModel):
    id: str
    name: str
    category: str
    style: str
    color: str
    position: dict[str, float]  # {x, y, z}
    rotation: float = 0.0       # Y-axis degrees
    dimensions: dict[str, float]  # {w, h, d}
    model_url: str | None = None
    price_usd: float | None = None
    vendor: str | None = None
    sku: str | None = None


class DesignGenerateRequest(BaseModel):
    room_id: str
    style: str = Field(default="modern", description="Desired interior style")
    preferences: dict[str, Any] = Field(default_factory=dict)


class DesignGenerateResponse(BaseSchema):
    design_id: str
    room_id: str
    style: str
    furniture: list[FurniturePiece]
    layout_notes: str
    color_palette: list[str]
    estimated_cost_usd: float
    created_at: datetime


# ── Render ────────────────────────────────────────────────────────────────────

class RenderRequest(BaseModel):
    design_id: str


class RenderJobResponse(BaseSchema):
    job_id: str
    design_id: str
    status: str                  # pending | processing | done | failed
    image_url: str | None = None
    error: str | None = None
    created_at: datetime


# ── AR ────────────────────────────────────────────────────────────────────────

class ARPosition(BaseModel):
    furniture_id: str
    x: float
    y: float
    z: float
    rotation_y: float = 0.0


class ARSessionResponse(BaseModel):
    design_id: str
    model_url: str
    positions: list[ARPosition]
    scale_factor: float = 1.0
    ar_modes: str = "webxr scene-viewer quick-look"


# ── Agent / Procurement ───────────────────────────────────────────────────────

class ProcureRequest(BaseModel):
    design_id: str
    budget_usd: float | None = None
    preferred_vendors: list[str] = Field(default_factory=list)


class AgentStreamEvent(BaseModel):
    event: str   # "thought" | "action" | "result" | "error"
    data: Any


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
