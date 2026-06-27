from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.extraction_run import ExtractionRun


def create_extraction_run(db: Session, extraction_run: ExtractionRun) -> ExtractionRun:
    db.add(extraction_run)
    db.commit()
    db.refresh(extraction_run)
    return extraction_run


def list_extraction_runs(db: Session) -> list[ExtractionRun]:
    return list(db.scalars(select(ExtractionRun).order_by(ExtractionRun.created_at.desc())).all())
