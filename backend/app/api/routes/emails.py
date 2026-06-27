from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.email import Email
from app.schemas.email import EmailImport, EmailRead
from app.services.email_extraction_service import infer_email_status

router = APIRouter()


@router.post("/import", response_model=EmailRead)
def import_email(payload: EmailImport, db: Session = Depends(get_db)) -> Email:
    email = Email(**payload.model_dump(), email_status=infer_email_status(payload.subject, payload.body))
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@router.get("", response_model=list[EmailRead])
def list_emails(db: Session = Depends(get_db)) -> list[Email]:
    return list(db.scalars(select(Email).order_by(Email.created_at.desc())).all())


@router.get("/{email_id}", response_model=EmailRead)
def get_email(email_id: int, db: Session = Depends(get_db)) -> Email:
    return db.get_one(Email, email_id)

