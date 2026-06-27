from sqlalchemy.orm import Session

from app.models.job_ad import JobAd
from app.repositories import job_ads as job_ad_repository
from app.schemas.job_ad import JobAdCapture


def capture_job_ad(db: Session, payload: JobAdCapture) -> JobAd:
    job_ad = JobAd(**payload.model_dump())
    return job_ad_repository.create_job_ad(db, job_ad)


def list_job_ads(db: Session) -> list[JobAd]:
    return job_ad_repository.list_job_ads(db)


def get_job_ad(db: Session, job_ad_id: int) -> JobAd:
    return job_ad_repository.get_job_ad(db, job_ad_id)

