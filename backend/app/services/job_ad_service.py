from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.enums import ApplicationStatus, ExtractionSourceType, JobAdStatus
from app.models.job_ad import JobAd
from app.repositories import application_events as event_repository
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
    updated_job_ad = job_ad_repository.update_job_ad(db, job_ad)
    if updated_job_ad.status == JobAdStatus.APPLIED:
        _ensure_application_for_applied_job(db, updated_job_ad)
    return updated_job_ad


def _ensure_application_for_applied_job(db: Session, job_ad: JobAd) -> None:
    application = application_repository.get_application_by_job_ad_id(db, job_ad.id)
    if application is None:
        application = Application(
            job_ad_id=job_ad.id,
            status=ApplicationStatus.APPLIED,
            company=job_ad.company,
            role_title=job_ad.title,
        )
        application_repository.create_application(db, application)
        event_repository.create_application_event(
            db,
            ApplicationEvent(
                application_id=application.id,
                email_id=None,
                event_type=ApplicationStatus.APPLIED.value,
                notes="Created when captured job was marked as applied.",
            ),
        )
        db.commit()
    elif application.status != ApplicationStatus.REJECTED:
        application.status = ApplicationStatus.APPLIED
        application_repository.update_application(db, application)


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
