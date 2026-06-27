from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmailStatus, MatchStatus


class EmailImport(BaseModel):
    subject: str
    sender: str | None = None
    body: str
    received_at: datetime | None = None


class EmailUpdate(BaseModel):
    email_status: EmailStatus | None = None
    match_status: MatchStatus | None = None
    extracted_company: str | None = None
    extracted_role_title: str | None = None


class EmailRead(BaseModel):
    id: int
    subject: str
    sender: str | None
    body: str
    extracted_company: str | None
    extracted_role_title: str | None
    extraction_confidence: float | None
    received_at: datetime | None
    email_status: EmailStatus
    match_status: MatchStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
