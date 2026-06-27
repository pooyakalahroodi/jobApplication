from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.extraction_run import ExtractionRun
from app.schemas.extraction import ExtractionRunRead
from app.services import extraction_service

router = APIRouter()


@router.post("/emails/{email_id}", response_model=ExtractionRunRead)
def extract_email(email_id: int, db: Session = Depends(get_db)) -> ExtractionRun:
    return extraction_service.extract_email_with_ollama(db, email_id)


@router.post("/job-ads/{job_ad_id}", response_model=ExtractionRunRead)
def extract_job_ad(job_ad_id: int, db: Session = Depends(get_db)) -> ExtractionRun:
    return extraction_service.extract_job_ad_with_ollama(db, job_ad_id)


@router.get("/runs", response_model=list[ExtractionRunRead])
def list_extraction_runs(db: Session = Depends(get_db)) -> list[ExtractionRun]:
    return extraction_service.list_extraction_runs(db)
