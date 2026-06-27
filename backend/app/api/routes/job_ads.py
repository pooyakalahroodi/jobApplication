from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_ad import JobAd
from app.schemas.job_ad import JobAdCapture, JobAdRead, JobAdUpdate
from app.services import job_ad_service

router = APIRouter()


@router.post("/capture", response_model=JobAdRead)
def capture_job_ad(payload: JobAdCapture, db: Session = Depends(get_db)) -> JobAd:
    return job_ad_service.capture_job_ad(db, payload)


@router.get("", response_model=list[JobAdRead])
def list_job_ads(db: Session = Depends(get_db)) -> list[JobAd]:
    return job_ad_service.list_job_ads(db)


@router.get("/{job_ad_id}", response_model=JobAdRead)
def get_job_ad(job_ad_id: int, db: Session = Depends(get_db)) -> JobAd:
    return job_ad_service.get_job_ad(db, job_ad_id)


@router.patch("/{job_ad_id}", response_model=JobAdRead)
def update_job_ad(
    job_ad_id: int,
    payload: JobAdUpdate,
    db: Session = Depends(get_db),
) -> JobAd:
    return job_ad_service.update_job_ad(db, job_ad_id, payload)


@router.delete("/{job_ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_ad(job_ad_id: int, db: Session = Depends(get_db)) -> Response:
    job_ad_service.delete_job_ad(db, job_ad_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
