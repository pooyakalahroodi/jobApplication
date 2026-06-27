from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.email import Email
from app.schemas.email import EmailImport, EmailRead
from app.services import email_service

router = APIRouter()


@router.post("/import", response_model=EmailRead)
def import_email(payload: EmailImport, db: Session = Depends(get_db)) -> Email:
    return email_service.import_email(db, payload)


@router.get("", response_model=list[EmailRead])
def list_emails(db: Session = Depends(get_db)) -> list[Email]:
    return email_service.list_emails(db)


@router.get("/{email_id}", response_model=EmailRead)
def get_email(email_id: int, db: Session = Depends(get_db)) -> Email:
    return email_service.get_email(db, email_id)
