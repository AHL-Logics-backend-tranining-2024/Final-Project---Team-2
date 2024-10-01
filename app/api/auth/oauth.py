# app/auth/oauth.py

from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
from app.settings import settings
from app.utils import ALGORITHM
from app.models import User
from app.api.auth.auth import fake_db_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")


# JWT token verification
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        exp: int = payload.get("exp")  # Expiration time from the token
        
        if user_id is None:
            raise credentials_exception
        
         # Check if the token has expired
        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        return user_id
    except JWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Verify the token and get the user ID
        user_id = verify_token(token, credentials_exception)

        #Fetch the user by ID
        user = next((u for u in fake_db_user.values() if str(u["id"]) == user_id), None) 
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    except Exception as e:
        # Catch all exceptions, including HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
      try:
        if not current_user["is_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
      except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking admin privileges: {str(e)}"
        )
      return current_user
