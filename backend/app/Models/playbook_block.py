from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.Infrastructure.db import Base
import uuid
from sqlalchemy import text

class PlaybookBlock(Base):
    __tablename__ = "playbook_blocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    playbook_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("playbooks.id"), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, server_default=text("now()"))
    title: Mapped[str] = mapped_column(String, nullable=False, default="New Block")
    block_type: Mapped[str] = mapped_column(String, nullable=False, default="RULES")
