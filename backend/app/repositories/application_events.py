from sqlalchemy.orm import Session

from app.models.application_event import ApplicationEvent


def create_application_event(db: Session, event: ApplicationEvent) -> ApplicationEvent:
    db.add(event)
    db.flush()
    return event

