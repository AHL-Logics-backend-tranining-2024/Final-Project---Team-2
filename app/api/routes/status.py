from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from app.api.auth.oauth import get_current_admin_user
from app.models import *
from app.database import statusOrders_db,orders_db

router = APIRouter()

@router.post("/", response_model=OrderStatusResponseModel, status_code=status.HTTP_201_CREATED)
async def create_status(status: OrderStatusCreateModel, current_user: User = Depends(get_current_admin_user)):
   try:
    if any(existing_status["name"].lower() == status.name.lower() for existing_status in statusOrders_db.values()):
        raise HTTPException(status_code=400, detail="Status name already exists")
    
    new_status = OrderStatusModel(
        name=status.name,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    statusOrders_db[new_status.id] = new_status.dict()
    
    return new_status
    
   except HTTPException as http_ex:
        raise http_ex
    
   except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
        

@router.get("/{status_id}", response_model=OrderStatusResponseModel)
async def get_status(status_id: UUID,current_user: User = Depends(get_current_admin_user)):
    if status_id not in statusOrders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return OrderStatusResponseModel(**statusOrders_db[status_id])


@router.put("/{status_id}", response_model=OrderStatusResponseModel)
async def update_status(status_id: UUID, status_update: OrderStatusUpdateModel, current_user: User = Depends(get_current_admin_user)):
    try:
     if status_id not in statusOrders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    
     if statusOrders_db[status_id]["name"].lower() == status_update.name.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"Status with name '{status_update.name}' already exists")
    
     current_status = statusOrders_db[status_id]
     updated_status = {**current_status, "name": status_update.name, "updated_at": datetime.now(timezone.utc)}
     statusOrders_db[status_id] = updated_status
     return OrderStatusResponseModel(**updated_status)
 
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.delete("/{status_id}")
async def remove_status(status_id: UUID, current_user: User = Depends(get_current_admin_user)):
    try:
     if status_id not in statusOrders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
     
     for order in orders_db.values():
        if order["status_id"] == status_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't delete status . It is used in an order")
    
     deleted_status = statusOrders_db.pop(status_id)
     
     return DeleteResponseModel(
        message=f"Status '{deleted_status.get('name')}' has been successfully deleted",
        status_id=status_id
     )
     
    except HTTPException as http_ex:
        raise http_ex
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )