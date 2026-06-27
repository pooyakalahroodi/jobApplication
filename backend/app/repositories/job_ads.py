from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import JobAdStatus
from app.models.job_ad import JobAd


def create_job_ad(db: Session, job_ad: JobAd) -> JobAd:
    db.add(job_ad)
    db.commit()
    db.refresh(job_ad)
    return job_ad


def list_job_ads(db: Session) -> list[JobAd]:
    return list(db.scalars(select(JobAd).order_by(JobAd.created_at.desc())).all())


def get_job_ad(db: Session, job_ad_id: int) -> JobAd:
    return db.get_one(JobAd, job_ad_id)


def update_job_ad(db: Session, job_ad: JobAd) -> JobAd:
    db.add(job_ad)
    db.commit()
    db.refresh(job_ad)
    return job_ad


def delete_job_ad(db: Session, job_ad: JobAd) -> None:
    db.delete(job_ad)
    db.commit()


def list_matchable_job_ads(db: Session) -> list[JobAd]:
    return list(
        db.scalars(
            select(JobAd).where(JobAd.status.in_([JobAdStatus.NOT_APPLIED, JobAdStatus.APPLIED]))
        ).all()
    )
