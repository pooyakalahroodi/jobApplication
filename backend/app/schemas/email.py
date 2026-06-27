from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmailStatus, MatchStatus


class EmailImport(BaseModel):
    subject: str
    sender: str | None = None
    body: str
    received_at: datetime | None = None


class EmailRead(BaseModel):
    id: int
    subject: str
    sender: str | None
    body: str
    received_at: datetime | None
    email_status: EmailStatus
    match_status: MatchStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

