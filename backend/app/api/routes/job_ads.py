from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_ad import JobAd
from app.schemas.job_ad import JobAdCapture, JobAdRead

router = APIRouter()


@router.post("/capture", response_model=JobAdRead)
def capture_job_ad(payload: JobAdCapture, db: Session = Depends(get_db)) -> JobAd:
    job_ad = JobAd(**payload.model_dump())
    db.add(job_ad)
    db.commit()
    db.refresh(job_ad)
    return job_ad


@router.get("", response_model=list[JobAdRead])
def list_job_ads(db: Session = Depends(get_db)) -> list[JobAd]:
    return list(db.scalars(select(JobAd).order_by(JobAd.created_at.desc())).all())


@router.get("/{job_ad_id}", response_model=JobAdRead)
def get_job_ad(job_ad_id: int, db: Session = Depends(get_db)) -> JobAd:
    return db.get_one(JobAd, job_ad_id)

