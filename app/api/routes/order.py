from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.auth.oauth import get_current_admin_user, get_current_user
from app.connection_to_db import get_db
from app.models import User
from app.services.order_service import OrderService
from app.schemas import (
    CreateOrderRequestModel,
    CreateOrderResponseModel,
    UpdateOrderStatusRequestModel,
    UpdateOrderStatusResponseModel,
    GetOrderResponseModel,
    GetOrderToUserResponseModel
)


router = APIRouter()

@router.post("/", response_model=CreateOrderResponseModel, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_request: CreateOrderRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    return order_service.create_order(current_user.id, order_request)



@router.put("/{order_id}/status", response_model=UpdateOrderStatusResponseModel, status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: UUID,
    status_update: UpdateOrderStatusRequestModel,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    return order_service.update_order_status(order_id, status_update.status)

@router.get("/{order_id}", response_model=GetOrderResponseModel, status_code=status.HTTP_200_OK)
async def get_order_details(
    order_id: UUID = Path(..., description="The ID of the order to retrieve"),
    db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    return order_service.get_order_details(order_id)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID = Path(..., description="The ID of the order to be canceled"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    order_service.cancel_order(order_id, current_user.id)
    return None

