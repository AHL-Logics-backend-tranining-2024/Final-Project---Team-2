from fastapi import FastAPI
from app.api.main import api_router
from app.connection_to_db import engine
from . import models

# Create the tables
models.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")