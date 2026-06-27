from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.enums import ExtractionSourceType
from app.repositories import application_events as event_repository
from app.repositories import emails as email_repository
from app.repositories import extraction_runs as extraction_run_repository
from app.schemas.email import EmailImport, EmailUpdate
from app.services.email_extraction_service import extract_email_facts


def import_email(db: Session, payload: EmailImport) -> Email:
    extraction = extract_email_facts(payload.subject, payload.body)
    email = Email(
        **payload.model_dump(),
        email_status=extraction.email_status,
        extracted_company=extraction.company,
        extracted_role_title=extraction.role_title,
        extraction_confidence=extraction.confidence,
    )
    return email_repository.create_email(db, email)


def list_emails(db: Session) -> list[Email]:
    return email_repository.list_emails(db)


def get_email(db: Session, email_id: int) -> Email:
    return email_repository.get_email(db, email_id)


def update_email(db: Session, email_id: int, payload: EmailUpdate) -> Email:
    email = email_repository.get_email(db, email_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(email, field, value)
    return email_repository.update_email(db, email)


def delete_email(db: Session, email_id: int) -> None:
    email = email_repository.get_email(db, email_id)
    event_repository.unlink_email_from_events(db, email.id)
    extraction_run_repository.delete_extraction_runs_by_source(
        db,
        ExtractionSourceType.EMAIL,
        email.id,
    )
    email_repository.delete_email(db, email)
