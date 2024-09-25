from fastapi import APIRouter

from app.api.routes import user, login, status, order

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(status.router, prefix="/statuses", tags=["statuses"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
