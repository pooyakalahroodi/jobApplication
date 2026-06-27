from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.enums import EmailStatus, MatchStatus


def create_email(db: Session, email: Email) -> Email:
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def list_emails(db: Session) -> list[Email]:
    return list(db.scalars(select(Email).order_by(Email.created_at.desc())).all())


def get_email(db: Session, email_id: int) -> Email:
    return db.get_one(Email, email_id)


def update_email(db: Session, email: Email) -> Email:
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def list_unmatched_actionable_emails(db: Session) -> list[Email]:
    return list(
        db.scalars(
            select(Email).where(
                Email.match_status == MatchStatus.NOT_SET,
                Email.email_status.in_(
                    [EmailStatus.PENDING, EmailStatus.REJECTED, EmailStatus.ACCEPTED]
                ),
            )
        ).all()
    )
