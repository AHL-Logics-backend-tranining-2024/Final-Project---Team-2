from datetime import datetime,timezone
import re
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, validator
from app.utils import get_password_hash, verify_password


#------------ Token Model -----------------#
# Token Model for handling authentication tokens
class Token(BaseModel):
    access_token: str  # The access token for authentication
    token_type: str    # The type of the token (e.g., "bearer")
    
# TokenData Model for storing user information associated with the token
class TokenData(BaseModel):
    user_id: Optional[UUID] = None    


#------------ User Model -----------------#
class UserBaseModel(BaseModel):
    username: str
    email: EmailStr

class UserCreateRequestModel(UserBaseModel):
    password: str = Field(
        ...,
        min_length=8,
        example="Jibreen123@",
    )
    
    @validator('password')
    def validate_password(cls, password: str):
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter.')
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter.')
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValueError('Password must contain at least one digit.')
        # Check for at least one special character
        if not re.search(r'[@$!%*?&]', password):
            raise ValueError('Password must contain at least one special character.')
        
        return password
    
class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    is_admin: bool = False  # Default values for admin status
    is_active: bool = True  # Default values for active status
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    

    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str):
        return verify_password(password, self.hashed_password)
   
    
class CreateUserResponseModel(UserBaseModel):
    id: UUID
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    