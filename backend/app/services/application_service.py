from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories import applications as application_repository
from app.schemas.application import ApplicationUpdate


def list_applications(db: Session) -> list[Application]:
    return application_repository.list_applications(db)


def get_application(db: Session, application_id: int) -> Application:
    return application_repository.get_application(db, application_id)


def update_application(
    db: Session,
    application_id: int,
    payload: ApplicationUpdate,
) -> Application:
    application = application_repository.get_application(db, application_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    return application_repository.update_application(db, application)
