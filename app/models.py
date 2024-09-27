from uuid import UUID,uuid4
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Token Model for handling authentication tokens
class Token(BaseModel):
    access_token: str  # The access token for authentication
    token_type: str    # The type of the token (e.g., "bearer")
    
# TokenData Model for storing user information associated with the token
class TokenData(BaseModel):
    username: UUID | None = None  # The user's UUID identifier, or None if not provided
    

# User Model
class User:
    id : UUID = Field(default_factory=uuid4)
    username: str
    password:EmailStr
    hashed_password:str
    is_admin:bool=False
    is_active:bool=True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = None
    
    


