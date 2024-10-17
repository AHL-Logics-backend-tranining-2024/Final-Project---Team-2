from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth.oauth import get_current_admin_user, get_current_user
from app.connection_to_db import get_db
from app.schemas import (
    ChangeRoleRequestModel,
    CreateUserResponseModel,
    GetOrderToUserResponseModel,
    GetUserResponseModel,
    UpdateUserRequestModel,
    UpdatedUserResponseModel,
    UserCreateRequestModel,
)
from app.models import User
from app.services.user_service import UserService
from app.api.auth.auth import *
from sqlalchemy.orm import Session

# Router and fake database setup
router = APIRouter()


# Endpoint to create a new user
@router.post(
    "/", response_model=CreateUserResponseModel, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreateRequestModel, db: Session = Depends(get_db)):
   user_service = UserService(db)
   return user_service.create_user(user)  


@router.put("/change_role", status_code=status.HTTP_200_OK)
async def change_role(
    request: ChangeRoleRequestModel,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.change_user_role(request)
    return {"message": "User role updated successfully."}


@router.put("/{user_id}", response_model=UpdatedUserResponseModel)
async def update_user(
    user_id: UUID,
    user_update: UpdateUserRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own details.",
        )

    # Step 2: Use the UserService to update the user
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, user_update)

    # Step 3: Return the updated user data
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    user_service = UserService(db)
    return user_service.delete_user(current_user.id, user_id)


@router.get(
    "/", response_model=list[GetUserResponseModel], status_code=status.HTTP_200_OK
)
async def get_all_users(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)): 
    user_service = UserService(db) 
    return user_service.get_all_users()
    


@router.get("/{user_id}", response_model=GetUserResponseModel)
async def get_user_details(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session =  Depends(get_db)
):
     # Step 1: Authenticate User
    if not current_user.is_admin and str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own details.",
        )

    # Step 2: Retrieve User Data
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    return user


@router.get("/{user_id}/orders",response_model=list[GetOrderToUserResponseModel], status_code=status.HTTP_200_OK)
async def get_orders_for_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
# Step 2: Retrieve User Data
    user_service = UserService(db)
    return user_service.getOrdersForUser(user_id)