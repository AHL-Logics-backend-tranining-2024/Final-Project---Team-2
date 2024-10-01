from typing import List
from fastapi import APIRouter, Depends, HTTPException,status

from app.api.auth.oauth import get_current_admin_user
from app.models import *

router = APIRouter()

fake_db_status ={}

@router.post("/statuses/", response_model=OrderStatusResponseModel, status_code=status.HTTP_201_CREATED)
async def create_status(status: OrderStatusCreateModel, current_user: dict = Depends(get_current_admin_user)):
    new_status = OrderStatusModel(
        name=status.name,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    fake_db_status[new_status.id] = new_status.dict()
    return new_status

@router.get("/statuses/{status_id}", response_model=OrderStatusResponseModel)
async def get_status(status_id: UUID, current_user: dict = Depends(get_current_admin_user)):
    if status_id not in fake_db_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return OrderStatusModel(**fake_db_status[status_id])

@router.get("/statuses/", response_model=List[OrderStatusResponseModel])
async def list_statuses(current_user: dict = Depends(get_current_admin_user)):
    return [OrderStatusModel(**status) for status in fake_db_status.values()]

@router.put("/statuses/{status_id}", response_model=OrderStatusResponseModel)
async def update_status(status_id: UUID, status_update: OrderStatusUpdateModel, current_user: dict = Depends(get_current_admin_user)):
    if status_id not in fake_db_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    
    current_status = fake_db_status[status_id]
    updated_status = {**current_status, "name": status_update.name, "updated_at": datetime.now(timezone.utc)}
    fake_db_status[status_id] = updated_status
    return OrderStatusModel(**updated_status)

@router.delete("/statuses/{status_id}")
async def delete_status(status_id: UUID, current_user: dict = Depends(get_current_admin_user)):
    if status_id not in fake_db_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    
    deleted_status = fake_db_status.pop(status_id)
    return DeleteResponseModel(
        message=f"Status '{deleted_status.get('name')}' has been successfully deleted",
        status_id=status_id
    )