from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_ad_id: Mapped[int | None] = mapped_column(ForeignKey("job_ads.id"), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=ApplicationStatus.UNKNOWN,
        nullable=False,
    )
    company: Mapped[str | None] = mapped_column(index=True, nullable=True)
    role_title: Mapped[str | None] = mapped_column(index=True, nullable=True)
    manual_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    job_ad = relationship("JobAd", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application")
