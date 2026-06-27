from sqlalchemy.orm import Session

from app.models.email import Email
from app.repositories import emails as email_repository
from app.schemas.email import EmailImport
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
