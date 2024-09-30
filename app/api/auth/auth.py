# app/auth/auth.py

from datetime import datetime
from uuid import uuid4
from app.models import User
from app.utils import get_password_hash, verify_password

fake_db_user = {
    str(uuid4()): {
        "id": str(uuid4()),
        "username": "regular_user",
        "email": "user@example.com",
        "hashed_password": get_password_hash("Test@1234"),
        "is_admin": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    },
    str(uuid4()): {
        "id": str(uuid4()),
        "username": "admin_user",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("Admin@1234"),
        "is_admin": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
}


def authenticate_user(username: str, password: str):
    user_data = next((u for u in fake_db_user.values() if u["username"] == username), None)
    
    if not user_data:
        return False
    
    if not verify_password(password, user_data["hashed_password"]):
        return False
    
    return user_data
