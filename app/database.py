from datetime import datetime
from uuid import uuid4

from app.utils import get_password_hash


users_db = {
    str(uuid4()): {
        "id": str(uuid4()),
        "username": "regular_user",
        "email": "user@example.com",
        "hashed_password": get_password_hash("Test@1234"),
        "is_admin": False,
        "is_active": True,
        "created_at": "2024-10-01 12:07:26",
        "updated_at": "2024-10-03 12:07:26"
    },
    str(uuid4()): {
        "id": str(uuid4()),
        "username": "admin_user",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("Admin@1234"),
        "is_admin": True,
        "is_active": True,
        "created_at": "2024-10-01 12:07:26",
        "updated_at": "2024-10-03 12:07:26"
    },
    str(uuid4()): {
        "id": str(uuid4()),
        "username": "admin_user",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("Admin@1234"),
        "is_admin": True,
        "is_active": True,
        "created_at": "2024-10-01 12:07:26",
        "updated_at": "2024-10-03 12:07:26"
    }
}


statusOrders_db = {}

orders_db = {}