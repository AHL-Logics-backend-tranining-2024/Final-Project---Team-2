from datetime import datetime
from fastapi import APIRouter, HTTPException,status

from app.models import User
from app.schemas.user import CreateUserRequestModel, CreateUserResponseModel
from app.utils import get_password_hash

# Router and fake database setup
router = APIRouter()
fake_db = {} # Using a dictionary for fake database

# Endpoint to create a new user
@router.post("/",response_model=CreateUserResponseModel,status_code = status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequestModel):
    # Check if user already exists by email
    if any(u.email == user.email for u in fake_db.values()):
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    # Store in fake_db
    fake_db[str(new_user.id)] = new_user
    
    # Return response excluding sensitive fields
    return CreateUserResponseModel(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_admin=new_user.is_admin,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )
    

    
# make sure to remove this function
@router.get("/example")
def example():
    return {"message": "this is an example"}
