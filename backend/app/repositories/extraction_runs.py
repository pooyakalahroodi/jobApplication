from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ExtractionSourceType
from app.models.extraction_run import ExtractionRun


def create_extraction_run(db: Session, extraction_run: ExtractionRun) -> ExtractionRun:
    db.add(extraction_run)
    db.commit()
    db.refresh(extraction_run)
    return extraction_run


def list_extraction_runs(db: Session) -> list[ExtractionRun]:
    return list(db.scalars(select(ExtractionRun).order_by(ExtractionRun.created_at.desc())).all())


def delete_extraction_runs_by_source(
    db: Session,
    source_type: ExtractionSourceType,
    source_id: int,
) -> None:
    runs = db.scalars(
        select(ExtractionRun).where(
            ExtractionRun.source_type == source_type,
            ExtractionRun.source_id == source_id,
        )
    ).all()
    for run in runs:
        db.delete(run)
