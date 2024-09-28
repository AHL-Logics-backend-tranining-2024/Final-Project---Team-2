
from datetime import datetime, timezone
import re
from typing import ClassVar
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, validator
from app.utils import get_password_hash, verify_password


# User Model
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

    PASSWORD_REGEX: ClassVar[str] = (
            r"^(?=.*[A-Z])"  # At least one uppercase letter
            r"(?=.*[a-z])"  # At least one lowercase letter
            r"(?=.*[0-9])"  # At least one digit
            r"(?=.*[@#$%^&+=])"  # At least one special character
            r".{8,}$"  # Minimum length of 8 characters
        )
    @validator('password')
    def validate_password(cls, password):
        if not re.match(cls.PASSWORD_REGEX, password):
            raise ValueError(
                "Password must be at least 8 characters long, "
                "and contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character."
            )
        return password
    
class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    is_admin: bool = False  # Default values for admin status
    is_active: bool = True  # Default values for active status
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str):
        return verify_password(password, self.hashed_password)

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
class CreateUserResponseModel(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime