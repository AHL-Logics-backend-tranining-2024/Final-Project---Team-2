# app/auth/auth.py
from app.database_models import User
from app.utils import verify_password
from app.database import users_db
from sqlalchemy.orm import Session


def authenticate_user(db:Session , username: str, password: str):
    user_data = db.query(User).filter(User.username == username).first()
    
    if not user_data:
        return False
    
    print(user_data.hashed_password)
    print(password)
    if not verify_password(password, user_data.hashed_password):
        return False
    
    return user_data
