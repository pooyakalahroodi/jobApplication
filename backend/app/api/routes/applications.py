from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application
from app.schemas.application import ApplicationDetailRead, ApplicationRead, ApplicationUpdate
from app.services import application_service

router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db)) -> list[Application]:
    return application_service.list_applications(db)


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)) -> Application:
    return application_service.get_application(db, application_id)


@router.get("/{application_id}/detail", response_model=ApplicationDetailRead)
def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
) -> ApplicationDetailRead:
    return application_service.get_application_detail(db, application_id)


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
) -> Application:
    return application_service.update_application(db, application_id, payload)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)) -> Response:
    application_service.delete_application(db, application_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
