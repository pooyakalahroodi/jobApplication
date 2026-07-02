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


def delete_email(db: Session, email: Email) -> None:
    db.delete(email)
    db.commit()


def list_unmatched_actionable_emails(db: Session) -> list[Email]:
    return list(
        db.scalars(
            select(Email).where(
                Email.match_status.in_([MatchStatus.NOT_SET, MatchStatus.NEEDS_REVIEW]),
                Email.email_status.in_(
                    [EmailStatus.PENDING, EmailStatus.REJECTED, EmailStatus.ACCEPTED]
                ),
            )
        ).all()
    )
