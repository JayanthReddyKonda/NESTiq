"""SpaceForge — FastAPI application entry point."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.models.schemas import HealthResponse
from app.routers import agent, ar, designs, rooms

logging.basicConfig(
    level=logging.DEBUG if False else logging.INFO,  # overridden below after settings load
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

# Apply log level from config after settings are loaded
logging.getLogger().setLevel(settings.log_level)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Config: %s", settings.safe_dump())

    if settings.allowed_origins == "*" and not settings.debug:
        logger.warning(
            "CORS is set to '*' in a non-debug environment. "
            "Set ALLOWED_ORIGINS to your frontend origin(s) in production."
        )
    if settings.secret_key.get_secret_value() == "change-me-in-production":
        logger.warning(
            "SECRET_KEY is still the placeholder value. "
            "Generate a real one: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Ensure the SQLite data directory exists (important when mounted as a volume)
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "", 1)
    db_dir = os.path.dirname(db_path)
    if db_dir and db_dir not in (".", ""):
        os.makedirs(db_dir, exist_ok=True)
        logger.info("DB dir ready: %s", db_dir)

    # Ensure required static subdirectories exist
    for directory in [settings.renders_dir, settings.models_dir, settings.uploads_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.info("Static dir ready: %s", directory)

    await init_db()
    logger.info("Database initialised")

    _copy_placeholder_model()

    yield

    # ── Shutdown ──
    logger.info("SpaceForge API shutting down")


def _copy_placeholder_model() -> None:
    """
    Ensure a placeholder GLB exists so AR page loads.
    # TODO: PRODUCTION — serve real per-design GLTF files
    """
    model_path = os.path.join(settings.models_dir, "room_default.glb")
    if not os.path.exists(model_path):
        # Write a minimal valid GLB (12-byte header only — enough for model-viewer to load without crash)
        # Real GLB starts with magic 0x46546C67, version 2, length
        header = b"glTF\x02\x00\x00\x00\x0c\x00\x00\x00"  # minimal 12-byte GLB
        with open(model_path, "wb") as f:
            f.write(header)
        logger.info("Placeholder GLB written to %s", model_path)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered interior design & AR placement platform.",
    lifespan=lifespan,
    # Disable docs in production (set DEBUG=true to re-enable)
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# ── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.ngrok(-free)?\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ──────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# ── API Routers ───────────────────────────────────────────────────────────────

app.include_router(rooms.router)
app.include_router(designs.router)
app.include_router(ar.router)
app.include_router(agent.router)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


# ── SPA catch-all ─────────────────────────────────────────────────────────────
# Serves the compiled React frontend for any non-API, non-static route.

_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index = os.path.join(_FRONTEND_DIST, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse(
        status_code=200,
        content={
            "message": "SpaceForge API is running. Frontend not yet built.",
            "docs": "/docs",
        },
    )
