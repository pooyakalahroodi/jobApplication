from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ApplicationStatus


class ApplicationRead(BaseModel):
    id: int
    job_ad_id: int | None
    status: ApplicationStatus
    company: str | None
    role_title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    company: str | None = None
    role_title: str | None = None
