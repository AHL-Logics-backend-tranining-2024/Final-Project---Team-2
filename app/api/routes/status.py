from uuid import UUID
from fastapi import APIRouter, Depends,status
from app.api.auth.oauth import get_current_admin_user
from app.connection_to_db import get_db
from app.models import User
from app.schemas import (
    CreateStatusRequestModel,
    CreateStatusResponseModel,
    UpdateStatusRequestModel,
    UpdateStatusResponseModel,
)
from app.services.status_service import StatusService
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/", response_model=CreateStatusResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_status(
    status: CreateStatusRequestModel,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    status_service = StatusService(db)
    new_status = status_service.create_status(status)
    return CreateStatusResponseModel.from_orm(new_status)


@router.get(
    "/{status_id}",
    response_model=CreateStatusResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_status(
    status_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    status_service = StatusService(db)
    status = status_service.get_status(status_id)
    return CreateStatusResponseModel.from_orm(status)


@router.put(
    "/{status_id}",
    response_model=CreateStatusResponseModel,
    status_code=status.HTTP_200_OK,
)
async def update_status(
    status_id: UUID,
    status_update: UpdateStatusRequestModel,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    status_service = StatusService(db)
    updated_status = status_service.update_status(status_id, status_update)
    return UpdateStatusResponseModel.from_orm(updated_status)


@router.delete("/{status_id}",status_code=status.HTTP_204_NO_CONTENT)
async def remove_status(
    status_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db:Session = Depends(get_db)
):
    status_service = StatusService(db)
    return status_service.remove_status(status_id)
