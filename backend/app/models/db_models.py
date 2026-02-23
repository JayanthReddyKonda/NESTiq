"""SQLAlchemy ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    filename: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    analysis_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    designs: Mapped[list[Design]] = relationship("Design", back_populates="room", cascade="all, delete-orphan")


class Design(Base):
    __tablename__ = "designs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"))
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    design_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    room: Mapped[Room] = relationship("Room", back_populates="designs")
    render_jobs: Mapped[list[RenderJob]] = relationship("RenderJob", back_populates="design", cascade="all, delete-orphan")


class RenderJob(Base):
    __tablename__ = "render_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    design_id: Mapped[str] = mapped_column(String(36), ForeignKey("designs.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | processing | done | failed
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    design: Mapped[Design] = relationship("Design", back_populates="render_jobs")
