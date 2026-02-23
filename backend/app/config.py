from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration is driven by environment variables (or .env for local dev).

    Production rules enforced here:
    - No Python-level defaults for environment-specific values (URLs, DSNs).
    - Secrets are SecretStr — they never leak into logs, repr, or error traces.
    - Required fields carry no default; a missing value raises ValidationError at
      startup — a loud, early failure rather than a silent runtime bug.
    - Cross-field validators enforce that real AI providers have credentials set.
    """

    model_config = SettingsConfigDict(
        # Auto-loaded for local dev. In Docker, vars are injected via env_file: in compose.
        env_file=".env",
        env_file_encoding="utf-8",
        # Never raise on unknown vars — lets infra/k8s inject extras freely.
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "SpaceForge API"
    app_version: str = "1.0.0"
    # REQUIRED — must be set; no default so a misconfigured deploy fails immediately.
    backend_public_url: str
    port: int = 8000

    # ── Security / Debug ─────────────────────────────────────────────────────
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    secret_key: SecretStr = SecretStr("change-me-in-production")

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated origins, or "*".
    # In production set this to your exact frontend origin(s).
    allowed_origins: str = "*"

    @field_validator("allowed_origins")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ── Database ──────────────────────────────────────────────────────────────
    # REQUIRED — must be explicit so Docker vs local paths are never conflated.
    # Local dev:  sqlite+aiosqlite:///./spaceforge.db
    # Docker:     sqlite+aiosqlite:////app/data/spaceforge.db
    database_url: str

    # ── Storage ───────────────────────────────────────────────────────────────
    static_dir: str = "app/static"
    renders_subdir: str = "renders"
    models_subdir: str = "models"
    uploads_subdir: str = "uploads"
    upload_max_mb: int = 10

    @property
    def renders_dir(self) -> str:
        return os.path.join(self.static_dir, self.renders_subdir)

    @property
    def models_dir(self) -> str:
        return os.path.join(self.static_dir, self.models_subdir)

    @property
    def uploads_dir(self) -> str:
        return os.path.join(self.static_dir, self.uploads_subdir)

    # ── AI Provider ───────────────────────────────────────────────────────────
    # Options: fake | grok
    ai_provider: Literal["fake", "grok"] = "fake"

    # Grok (xAI) — https://console.x.ai
    # Uses the OpenAI SDK pointed at https://api.x.ai/v1
    grok_api_key: SecretStr = SecretStr("")
    grok_model: str = "grok-3"          # best available as of Feb 2026
    grok_base_url: str = "https://api.x.ai/v1"

    # ── Cross-field validation ────────────────────────────────────────────────
    @model_validator(mode="after")
    def validate_provider_credentials(self) -> "Settings":
        """Fail fast at startup if a real AI provider is selected without credentials."""
        if self.ai_provider == "grok" and not self.grok_api_key.get_secret_value():
            raise ValueError(
                "AI_PROVIDER=grok requires GROK_API_KEY to be set. "
                "Get yours at https://console.x.ai"
            )
        return self

    def safe_dump(self) -> dict:
        """
        Loggable config dict with all secrets redacted.
        Always use this in startup logs — never model_dump() directly.
        """
        d = self.model_dump()
        for field in ("secret_key", "grok_api_key"):
            if field in d:
                d[field] = "[REDACTED]"
        return d


@lru_cache
def get_settings() -> Settings:
    return Settings()
