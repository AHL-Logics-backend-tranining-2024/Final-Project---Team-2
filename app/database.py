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