from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application


def list_applications(db: Session) -> list[Application]:
    return list(db.scalars(select(Application).order_by(Application.updated_at.desc())).all())


def get_application(db: Session, application_id: int) -> Application:
    return db.get_one(Application, application_id)


def get_application_by_job_ad_id(db: Session, job_ad_id: int) -> Application | None:
    return db.scalar(select(Application).where(Application.job_ad_id == job_ad_id))


def create_application(db: Session, application: Application) -> Application:
    db.add(application)
    db.flush()
    return application
