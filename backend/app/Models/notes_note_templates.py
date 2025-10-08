from __future__ import annotations

import uuid
from typing import Any
from sqlalchemy import Table, Column, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID

from app.Infrastructure.db import Base

notes_note_templates_association = Table(
    "notes_note_templates",
    Base.metadata,
    Column(
        "note_id",
        UUID(as_uuid=True),
        ForeignKey("public.notes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "note_template_id",
        UUID(as_uuid=True),
        ForeignKey("public.note_templates.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    schema="public",
)