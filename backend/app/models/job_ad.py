from datetime import datetime

from sqlalchemy import DateTime, Enum, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import JobAdStatus


class JobAd(Base):
    __tablename__ = "job_ads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(index=True)
    company: Mapped[str | None] = mapped_column(index=True, nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(nullable=True)
    page_title: Mapped[str | None] = mapped_column(nullable=True)
    selected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    json_ld: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[JobAdStatus] = mapped_column(
        Enum(JobAdStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=JobAdStatus.NOT_APPLIED,
        nullable=False,
    )
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    applications = relationship("Application", back_populates="job_ad")
