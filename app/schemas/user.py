
from datetime import datetime
import re
from typing import ClassVar
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator

from app.models import User


class UserBaseModel(BaseModel):
    username:str = Field(...,example = "jibreen")
    email:EmailStr = Field(...,example= "test@gmail.com")
    password:str = Field(...,example = "Jibreen123%^")
    
    # Define the constraints for the password
    PASSWORD_REGEX: ClassVar[str] = (
        r"^(?=.*[A-Z])"  # At least one uppercase letter
        r"(?=.*[a-z])"  # At least one lowercase letter
        r"(?=.*[0-9])"  # At least one digit
        r"(?=.*[@#$%^&+=])"  # At least one special character
        r".{8,}$"  # Minimum length of 8 characters
    )
    
    # Validator for password constraints
    @validator('password')
    def validate_password(cls, password):
        if not re.match(cls.PASSWORD_REGEX, password):
            raise ValueError(
                "Password must be at least 8 characters long, "
                "and contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character."
            )
        return password
    
class CreateUserRequestModel(UserBaseModel):
    pass

class CreateUserResponseModel(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    