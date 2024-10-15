from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status as http_status
from app.models import Order, Status
from app.schemas import CreateStatusRequestModel, UpdateStatusRequestModel


class StatusService:
    def __init__(self, db: Session):
        self.db = db

    def create_status(self, status: CreateStatusRequestModel) -> Status:
        # Check for unique name
        if self.db.query(Status).filter(Status.name.ilike(status.name)).first():
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Status name already exists",
            )

        new_status = Status(name=status.name)
        self.db.add(new_status)
        self.db.commit()
        self.db.refresh(new_status)
        return new_status

    def get_status(self, status_id: UUID) -> Status:
        status = self.db.query(Status).filter(Status.id == status_id).first()
        if not status:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Status not found"
            )
        return status

    def update_status(
        self, status_id: UUID, status_update: UpdateStatusRequestModel
    ) -> Status:
        status = self.db.query(Status).filter(Status.id == status_id).first()
        if not status:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Status not found"
            )

        # Check for unique name
        existing_status = (
            self.db.query(Status)
            .filter(Status.name.ilike(status_update.name), Status.id != status_id)
            .first()
        )
        if existing_status:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Status with name '{status_update.name}' already exists",
            )

        status.name = status_update.name
        status.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(status)
        return status

    def remove_status(self, status_id: UUID):
        # Check if the status exists
        status = self.db.query(Status).get(status_id)
        if not status:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Status not found"
            )

        # Check if the status is associated with any orders
        associated_orders = self.db.query(Order).filter(Order.status_id == status_id).first()
        if associated_orders:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Can't delete status. It is used in an order. Consider creating a new status for obsolete items."
            )

        # If no issues, delete the status
        self.db.delete(status)
        self.db.commit()