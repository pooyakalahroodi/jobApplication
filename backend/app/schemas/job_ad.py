from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import JobAdStatus


class JobAdCapture(BaseModel):
    url: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    description: str | None = None
    source: str | None = None
    page_title: str | None = None
    selected_text: str | None = None
    raw_text: str | None = None
    json_ld: list[dict] | None = None
    captured_at: datetime | None = None


class JobAdRead(BaseModel):
    id: int
    url: str | None
    title: str
    company: str | None
    location: str | None
    description: str | None
    source: str | None
    page_title: str | None
    selected_text: str | None
    raw_text: str | None
    json_ld: list[dict] | None
    status: JobAdStatus
    captured_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
