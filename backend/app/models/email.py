from datetime import datetime

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import EmailStatus, MatchStatus


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(index=True)
    sender: Mapped[str | None] = mapped_column(index=True, nullable=True)
    body: Mapped[str] = mapped_column(Text)
    extracted_company: Mapped[str | None] = mapped_column(index=True, nullable=True)
    extracted_role_title: Mapped[str | None] = mapped_column(index=True, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=EmailStatus.UNKNOWN,
        nullable=False,
    )
    match_status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=MatchStatus.NOT_SET,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    events = relationship("ApplicationEvent", back_populates="email")
