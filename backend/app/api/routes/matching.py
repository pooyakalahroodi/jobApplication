from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.matching_service import run_matching

router = APIRouter()


@router.post("/run")
def run_matcher(db: Session = Depends(get_db)) -> dict[str, int]:
    matched_count = run_matching(db)
    return {"matched_count": matched_count}

