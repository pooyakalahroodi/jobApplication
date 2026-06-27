from datetime import datetime

from sqlalchemy import DateTime, Enum, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.enums import ExtractionSourceType, ExtractionStatus


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_type: Mapped[ExtractionSourceType] = mapped_column(
        Enum(ExtractionSourceType, values_callable=lambda enum: [item.value for item in enum]),
        index=True,
        nullable=False,
    )
    source_id: Mapped[int] = mapped_column(index=True, nullable=False)
    extractor: Mapped[str] = mapped_column(default="ollama", nullable=False)
    model: Mapped[str | None] = mapped_column(nullable=True)
    prompt_version: Mapped[str] = mapped_column(nullable=False)
    raw_input_hash: Mapped[str] = mapped_column(nullable=False)
    raw_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=ExtractionStatus.SUCCESS,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
