"""
In-memory async render job queue.

Each render job is a asyncio.Task that updates a shared status dict.
For production, swap this with Celery + Redis or ARQ.
# TODO: PRODUCTION — replace with persistent task queue (Celery/ARQ/Dramatiq)
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class RenderJob:
    def __init__(self, job_id: str, design_id: str) -> None:
        self.job_id = job_id
        self.design_id = design_id
        self.status: str = JobStatus.PENDING
        self.image_url: str | None = None
        self.error: str | None = None
        self.created_at: datetime = datetime.now(timezone.utc)
        self.updated_at: datetime = self.created_at
        self._task: asyncio.Task | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "design_id": self.design_id,
            "status": self.status,
            "image_url": self.image_url,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class RenderQueue:
    """Thread-safe (asyncio) in-memory job queue."""

    def __init__(self) -> None:
        self._jobs: dict[str, RenderJob] = {}

    def get_job(self, job_id: str) -> RenderJob | None:
        return self._jobs.get(job_id)

    async def submit(
        self,
        design_id: str,
        design_data: dict,
        ai_provider,
        renders_dir: str,
        backend_public_url: str,
        job_id: str | None = None,  # caller can pin the ID (keeps DB + queue in sync)
    ) -> RenderJob:
        job_id = job_id or str(uuid.uuid4())
        job = RenderJob(job_id=job_id, design_id=design_id)
        self._jobs[job_id] = job

        task = asyncio.create_task(
            self._run(job, design_data, ai_provider, renders_dir, backend_public_url),
            name=f"render-{job_id}",
        )
        job._task = task
        logger.info("Render job %s submitted for design %s", job_id, design_id)
        return job

    async def _run(
        self,
        job: RenderJob,
        design_data: dict,
        ai_provider,
        renders_dir: str,
        backend_public_url: str,
    ) -> None:
        job.status = JobStatus.PROCESSING
        job.updated_at = datetime.now(timezone.utc)

        try:
            image_bytes: bytes = await ai_provider.render_design(design_data)

            os.makedirs(renders_dir, exist_ok=True)
            filename = f"{job.job_id}.png"
            filepath = os.path.join(renders_dir, filename)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            job.image_url = f"{backend_public_url}/static/renders/{filename}"
            job.status = JobStatus.DONE
            logger.info("Render job %s completed → %s", job.job_id, job.image_url)

        except Exception as exc:
            logger.exception("Render job %s failed", job.job_id)
            job.status = JobStatus.FAILED
            job.error = str(exc)

        finally:
            job.updated_at = datetime.now(timezone.utc)


# ── Singleton ─────────────────────────────────────────────────────────────────

_queue: RenderQueue | None = None


def get_render_queue() -> RenderQueue:
    """FastAPI dependency — returns the singleton render queue."""
    global _queue
    if _queue is None:
        _queue = RenderQueue()
    return _queue
