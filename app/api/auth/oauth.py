# app/auth/oauth.py

from uuid import UUID
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
import jwt
from app.models import TokenData
from app.models import User
from app.api.auth.auth import fake_db_user

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = next((u for u in fake_db_user.values() if str(u["id"]) == user_id), None) 
    if user is None:
        raise credentials_exception
    return TokenData(user_id=UUID(user_id))

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    # Check if user_id is present
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing user_id")

    # Find user by user_id in the fake database
    user = next((u for u in fake_db_user.values() if str(u["id"]) == str(current_user.user_id)), None)
    
    # If user not found
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if the user is active
    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Return the user as a dictionary (no need for .dict() since it's already a dict)
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    try:
        # Fetch the user data from the fake database using user_id
        user_data = next((u for u in fake_db_user.values() if str(u["id"]) == str(current_user["id"])), None)

        # Debugging: print user_data for inspection
        print(f"Fetched user_data: {user_data}")

        # Check if the user is found and has admin privileges
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not user_data["is_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        return user_data  # Return user data if they are an admin

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking admin privileges: {str(e)}"
        )