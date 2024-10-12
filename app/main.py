from fastapi import FastAPI

from app.api.main import api_router
from app.connection_to_db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")