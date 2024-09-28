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
    def __init__(self, username: str, email: EmailStr, hashed_password: str):
        self.id: UUID = uuid4()
        self.username: str = username
        self.email: EmailStr = email
        self.hashed_password: str = hashed_password
        self.is_admin: bool = False
        self.is_active: bool = True
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = self.created_at
    
    


