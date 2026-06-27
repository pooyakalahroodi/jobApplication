from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.email import Email
from app.schemas.email import EmailImport, EmailRead, EmailUpdate
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


@router.patch("/{email_id}", response_model=EmailRead)
def update_email(
    email_id: int,
    payload: EmailUpdate,
    db: Session = Depends(get_db),
) -> Email:
    return email_service.update_email(db, email_id, payload)


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email(email_id: int, db: Session = Depends(get_db)) -> Response:
    email_service.delete_email(db, email_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
