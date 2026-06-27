from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application
from app.schemas.application import ApplicationRead
from app.schemas.matching import ManualMatchRequest, MatchingRunResult
from app.services.matching_service import confirm_match, run_matching

router = APIRouter()


@router.post("/run")
def run_matcher(db: Session = Depends(get_db)) -> MatchingRunResult:
    return run_matching(db)


@router.post("/confirm", response_model=ApplicationRead)
def confirm_manual_match(
    payload: ManualMatchRequest,
    db: Session = Depends(get_db),
) -> Application:
    return confirm_match(db, payload.job_ad_id, payload.email_id)
