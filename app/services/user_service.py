
from datetime import datetime, timezone
from operator import or_
from uuid import UUID
from fastapi import HTTPException,status
from app.models import Order, User
from app.schemas import ChangeRoleRequestModel, CreateUserResponseModel, GetOrderToUserResponseModel, GetUserResponseModel, UpdateUserRequestModel, UpdatedUserResponseModel, UserCreateRequestModel
from sqlalchemy.orm import Session,joinedload

from app.utils import get_password_hash  


class UserService:
    def __init__(self, db: Session):
     self.db = db

    def create_user(self, user: UserCreateRequestModel) -> CreateUserResponseModel:
        if self.db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
                )

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )

        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return CreateUserResponseModel.from_orm(new_user)
        
            
            
    def get_user_by_id(self, user_id: UUID) -> GetUserResponseModel:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return GetUserResponseModel.from_orm(user)
        
        
            
    def get_all_users(self) -> list[GetUserResponseModel]:
            users = self.db.query(User).all()
            return [GetUserResponseModel.from_orm(user) for user in users]
        
     
     
    def update_user(self, user_id: UUID, user_update: UpdateUserRequestModel) -> UpdatedUserResponseModel:
        
            # Step 1: Retrieve the current user data
            db_user = self.db.query(User).filter(User.id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Step 2: Update user data
            update_data = user_update.dict(exclude_unset=True)

            # Check if the email is being updated and if it's unique
            if 'email' in update_data:
                email_exists = self.db.query(User).filter(User.email == update_data['email']).first()
                if email_exists and email_exists.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
                    )

            # Step 3: Hash password if being updated
            if "password" in update_data:
                db_user.hashed_password = get_password_hash(update_data.pop("password"))

            # Update other fields
            for field, value in update_data.items():
                setattr(db_user, field, value)

            # Step 4: Update the 'updated_at' timestamp
            db_user.updated_at = datetime.now(timezone.utc)

            # Step 5: Commit changes to the database
            self.db.commit()
            self.db.refresh(db_user)

            # Step 6: Return updated user data
            return UpdatedUserResponseModel.from_orm(db_user)
         
            
                 
    def change_user_role(self, request: ChangeRoleRequestModel) -> None:     
            user = self.db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found."
                )

            user.is_admin = request.is_admin
            self.db.commit()
            
            
    def delete_user(self, current_user_id: UUID, user_id: UUID):
        # Check if the user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )

        # Check if the current user is trying to delete their own account
        if str(current_user_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only delete your own account.",
            )

        # Check for active orders
        active_orders = self.db.query(Order).options(joinedload(Order.status)).filter(
         Order.user_id == user.id,
         or_(
            Order.status.has(name="Pending"),
            Order.status.has(name="Processing")
         )
         ).first()

        if active_orders:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has active orders and cannot be deleted.",
            )

        # Delete the user
        self.db.delete(user)
        self.db.commit()

        return {"message": "User deleted successfully"}
    
    
    def getOrdersForUser(self, user_id: UUID):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        orders = self.db.query(Order).filter(Order.user_id == user_id).all()
        
        if not orders:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found for the user."
         )

        # Step 3: Format Response
        formatted_orders = [
         GetOrderToUserResponseModel(
            id=order.id,
            status=order.status.name,
            total_price=order.total_price,
            created_at=order.created_at,
            updated_at=order.updated_at
         )
         for order in orders
        ]

        # Step 4: Return Order List
        return formatted_orders