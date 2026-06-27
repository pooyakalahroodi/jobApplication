from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application_event import ApplicationEvent


def create_application_event(db: Session, event: ApplicationEvent) -> ApplicationEvent:
    db.add(event)
    db.flush()
    return event


def list_events_by_application_id(db: Session, application_id: int) -> list[ApplicationEvent]:
    return list(
        db.scalars(
            select(ApplicationEvent)
            .where(ApplicationEvent.application_id == application_id)
            .order_by(ApplicationEvent.created_at.desc())
        ).all()
    )


def delete_events_by_application_id(db: Session, application_id: int) -> None:
    events = db.scalars(
        select(ApplicationEvent).where(ApplicationEvent.application_id == application_id)
    ).all()
    for event in events:
        db.delete(event)


def unlink_email_from_events(db: Session, email_id: int) -> None:
    events = db.scalars(select(ApplicationEvent).where(ApplicationEvent.email_id == email_id)).all()
    for event in events:
        event.email_id = None
        db.add(event)
