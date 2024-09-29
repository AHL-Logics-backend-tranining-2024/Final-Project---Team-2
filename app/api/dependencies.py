from datetime import datetime
import os
from typing import Annotated
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.models import *
from app.utils import get_password_hash, verify_password


fake_db_user = {
    "regular_user": {
        "id": uuid4(),
        "username": "regular_user",
        "email": "user@example.com",
        "hashed_password": get_password_hash("Test@1234"),
        "is_admin": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    },
    "admin_user": {
        "id": uuid4(),
        "username": "admin_user",
        "email": "admin@example.com",
        "hashed_password":get_password_hash("Admin@1234"),
        "is_admin": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = next((User(**u) for u in fake_db_user.values() if u["username"] == username), None)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_db_user, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user