from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import JobAdStatus


class JobAdCapture(BaseModel):
    url: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    description: str | None = None
    captured_at: datetime | None = None


class JobAdRead(BaseModel):
    id: int
    url: str | None
    title: str
    company: str | None
    location: str | None
    description: str | None
    status: JobAdStatus
    captured_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

