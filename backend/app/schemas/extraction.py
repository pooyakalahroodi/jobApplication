from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ExtractionSourceType, ExtractionStatus


class ExtractionRunRead(BaseModel):
    id: int
    source_type: ExtractionSourceType
    source_id: int
    extractor: str
    model: str | None
    prompt_version: str
    raw_input_hash: str
    raw_output: str | None
    parsed_json: dict | None
    confidence: float | None
    status: ExtractionStatus
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
