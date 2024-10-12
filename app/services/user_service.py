
import logging
from sqlite3 import IntegrityError
from fastapi import HTTPException,status
from app.database_models import User
from app.exception import EmailAlreadyExistsException
from app.schemas import CreateUserResponseModel, UserCreateRequestModel
from sqlalchemy.orm import Session

from app.utils import get_password_hash  


class UserService:
    def __init__(self, db: Session):
     self.db = db

    def create_user(self, user: UserCreateRequestModel) -> CreateUserResponseModel:
        if self.db.query(User).filter(User.email == user.email).first():
            raise EmailAlreadyExistsException()

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return CreateUserResponseModel.from_orm(new_user)
        except IntegrityError:
            self.db.rollback()
            # Log specific database integrity errors
            logging.error("Database integrity error occurred while creating a user.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error, possible duplicate entry."
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the user"
            )