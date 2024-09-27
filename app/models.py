# Token Model for handling authentication tokens
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str  # The access token for authentication
    token_type: str    # The type of the token (e.g., "bearer")
    
# TokenData Model for storing user information associated with the token
class TokenData(BaseModel):
    username: UUID | None = None  # The user's UUID identifier, or None if not provided
