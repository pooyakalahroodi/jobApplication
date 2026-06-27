from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.matching import MatchingRunResult
from app.services.matching_service import run_matching

router = APIRouter()


@router.post("/run")
def run_matcher(db: Session = Depends(get_db)) -> MatchingRunResult:
    return run_matching(db)
