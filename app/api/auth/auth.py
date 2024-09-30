# app/auth/auth.py

from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.models import User
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
        "hashed_password": get_password_hash("Admin@1234"),
        "is_admin": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
}

load_dotenv()

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
