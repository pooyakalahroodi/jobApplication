from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories import application_events as event_repository
from app.repositories import applications as application_repository
from app.schemas.application import ApplicationDetailRead, ApplicationUpdate


def list_applications(db: Session) -> list[Application]:
    return application_repository.list_applications(db)


def get_application(db: Session, application_id: int) -> Application:
    return application_repository.get_application(db, application_id)


def get_application_detail(db: Session, application_id: int) -> ApplicationDetailRead:
    application = application_repository.get_application(db, application_id)
    return ApplicationDetailRead.model_validate(
        {
            **application.__dict__,
            "job_ad": application.job_ad,
            "events": event_repository.list_events_by_application_id(db, application.id),
        }
    )


def update_application(
    db: Session,
    application_id: int,
    payload: ApplicationUpdate,
) -> Application:
    application = application_repository.get_application(db, application_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    return application_repository.update_application(db, application)


def delete_application(db: Session, application_id: int) -> None:
    application = application_repository.get_application(db, application_id)
    event_repository.delete_events_by_application_id(db, application.id)
    application_repository.delete_application(db, application)
