from datetime import timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth.oauth import get_current_admin_user, get_current_user
from app.schemas import (
    ChangeRoleRequestModel,
    CreateUserResponseModel,
    GetUserResponseModel,
    UpdateUserRequestModel,
    UpdatedUserResponseModel,
    User,
    UserCreateRequestModel,
)
from app.utils import get_password_hash
from app.api.auth.auth import *
from app.database import users_db

# Router and fake database setup
router = APIRouter()


# Endpoint to create a new user
@router.post(
    "/", response_model=CreateUserResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreateRequestModel):
    # Check if user already exists by email
    if any(u.get("email") == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Create new user and set hashed password
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),  # Hash the password
    )

    # Store in fake_db
    users_db[str(new_user.id)] = new_user.dict()

    # Return response excluding sensitive fields
    return CreateUserResponseModel(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_admin=new_user.is_admin,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )


@router.put("/change_role", status_code=status.HTTP_200_OK)
async def change_role(
    request: ChangeRoleRequestModel,
    current_user: User = Depends(get_current_admin_user),
):
    try:
        user = users_db.get(str(request.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        user["is_admin"] = request.is_admin
        users_db[str(request.user_id)] = user

        return {"message": "User role updated successfully."}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the user role.",
        )


@router.put("/{user_id}", response_model=UpdatedUserResponseModel)
async def update_user(
    user_id: UUID,
    user_update: UpdateUserRequestModel,
    current_user: User = Depends(get_current_user),
):
    # Step 1 & 2: Authenticate User and Validate User ID
    if str(current_user.get("id")) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own details.",
        )

    # Retrieve the current user data
    user_data = users_db.get(str(user_id))

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Step 3: Update User Data
    update_data = user_update.dict()

    # Check if email is being updated and if it's unique
    if any(u.get("email") == user_update.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    if "password" in update_data:
        # Step 4: Hash Password
        user_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    # Update other fields
    for field, value in update_data.items():
        if value is not None:
            user_data[field] = value

    # Update the 'updated_at' timestamp
    user_data["updated_at"] = datetime.now(timezone.utc)

    # Update the user in the database
    users_db[str(user_id)] = user_data

    # Step 5: Return Updated User Data
    updated_user = User(**user_data)
    return UpdatedUserResponseModel(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_admin=updated_user.is_admin,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, current_user: User = Depends(get_current_user)):

    # Step 1 & 2: Authenticate User and Validate User ID
    if str(current_user.get("id")) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own details.",
        )

    # Retrieve the current user data
    user_data = users_db.get(str(user_id))

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    """ 
    .............................................
    I am waiting for the order model to be ready.
    .............................................
    """

    users_db.pop(str(user_id))

    return


@router.get(
    "/", response_model=list[GetUserResponseModel], status_code=status.HTTP_200_OK
)
async def get_all_users(current_admin: User = Depends(get_current_admin_user)):

    all_users = list(users_db.values())

    return [
        GetUserResponseModel(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_admin=user["is_admin"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )
        for user in all_users
    ]


@router.get("/{user_id}", response_model=GetUserResponseModel)
async def get_user_details(
    user_id: UUID, current_user: User = Depends(get_current_user)
):
    # Step 1: Authenticate User
    if not current_user.get("is_admin") and str(current_user.get("id")) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own details.",
        )

    # Step 2: Validate User ID
    user_data = users_db.get(str(user_id))
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Step 3: Retrieve User Data
    user = User(**user_data)

    # Step 4: Return User Data
    return GetUserResponseModel(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/{user_id}/orders", status_code=status.HTTP_200_OK)
async def get_orders_for_user(
    user_id: UUID, current_user: User = Depends(get_current_user)
):

    # Validate User ID
    if user_id != current_user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    """
     # Retrieve Orders
     orders = [
        order
        for order in orders_db.values()
        if order["user_id"] == user_id
     ]

     # Format Response
     formatted_orders = [
        {
            "id": order["id"],
            "status": order["status"],
            "total_price": order["total_price"],
            "created_at": order["created_at"],
            "updated_at": order["updated_at"]
        }
        for order in orders
     ]

     # Return Order List
     return formatted_orders
    """
