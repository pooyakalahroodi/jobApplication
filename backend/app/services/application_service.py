from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories import applications as application_repository


def list_applications(db: Session) -> list[Application]:
    return application_repository.list_applications(db)


def get_application(db: Session, application_id: int) -> Application:
    return application_repository.get_application(db, application_id)

