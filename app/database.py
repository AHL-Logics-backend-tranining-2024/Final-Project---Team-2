from datetime import datetime
from uuid import uuid4
from app.utils import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

users_db = {

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


statusOrders_db = {}

orders_db = {}

products_db = {}


SQLALCHEMY_DATABASE_URL = "postgresql://admin:adminpass@db:5432/fastapi_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()