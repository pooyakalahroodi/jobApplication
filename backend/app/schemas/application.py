from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ApplicationStatus
from app.schemas.job_ad import JobAdRead


class ApplicationRead(BaseModel):
    id: int
    job_ad_id: int | None
    status: ApplicationStatus
    company: str | None
    role_title: str | None
    manual_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    company: str | None = None
    role_title: str | None = None
    manual_notes: str | None = None


class ApplicationEventRead(BaseModel):
    id: int
    application_id: int
    email_id: int | None
    event_type: str
    event_date: datetime | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationDetailRead(ApplicationRead):
    job_ad: JobAdRead | None
    events: list[ApplicationEventRead]
