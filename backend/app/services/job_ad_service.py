from sqlalchemy.orm import Session

from app.models.enums import ExtractionSourceType
from app.models.job_ad import JobAd
from app.repositories import applications as application_repository
from app.repositories import extraction_runs as extraction_run_repository
from app.repositories import job_ads as job_ad_repository
from app.schemas.job_ad import JobAdCapture, JobAdUpdate


def capture_job_ad(db: Session, payload: JobAdCapture) -> JobAd:
    data = payload.model_dump()
    if data["description"] is None:
        data["description"] = data["selected_text"] or data["raw_text"]
    job_ad = JobAd(**data)
    return job_ad_repository.create_job_ad(db, job_ad)


def list_job_ads(db: Session) -> list[JobAd]:
    return job_ad_repository.list_job_ads(db)


def get_job_ad(db: Session, job_ad_id: int) -> JobAd:
    return job_ad_repository.get_job_ad(db, job_ad_id)


def update_job_ad(db: Session, job_ad_id: int, payload: JobAdUpdate) -> JobAd:
    job_ad = job_ad_repository.get_job_ad(db, job_ad_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job_ad, field, value)
    return job_ad_repository.update_job_ad(db, job_ad)


def delete_job_ad(db: Session, job_ad_id: int) -> None:
    job_ad = job_ad_repository.get_job_ad(db, job_ad_id)
    for application in application_repository.list_applications_by_job_ad_id(db, job_ad.id):
        application.job_ad_id = None
        application_repository.update_application(db, application)
    extraction_run_repository.delete_extraction_runs_by_source(
        db,
        ExtractionSourceType.JOB_AD,
        job_ad.id,
    )
    job_ad_repository.delete_job_ad(db, job_ad)
