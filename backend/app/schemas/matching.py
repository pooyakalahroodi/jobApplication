from pydantic import BaseModel


class MatchingRunResult(BaseModel):
    processed_count: int
    matched_count: int
    needs_review_count: int
    unmatched_count: int


class ManualMatchRequest(BaseModel):
    job_ad_id: int
    email_id: int

