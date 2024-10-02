# app/auth/auth.py

from datetime import datetime
from uuid import uuid4
from app.utils import get_password_hash, verify_password
from app.database import users_db


def authenticate_user(username: str, password: str):
    user_data = next((u for u in users_db.values() if u["username"] == username), None)
    
    if not user_data:
        return False
    
    if not verify_password(password, user_data["hashed_password"]):
        return False
    
    return user_data
