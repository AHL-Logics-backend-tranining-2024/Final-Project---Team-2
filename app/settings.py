from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SQLALCHEMY_DATABASE_URL: str

    class Config:
        env_file = ".env"  # Specify the .env file to load environment variables from

settings = Settings() 