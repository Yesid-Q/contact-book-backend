from typing import List
from pydantic import BaseSettings

class SystemApp(BaseSettings):
    DEBUG: bool
    APP_NAME: str
    DESCRIPTION: str
    VERSION: str
    SECRET_KEY: str

    DATABASE_DRIVER: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DATABASE_DATABASE: str
    LIFETIME_AUTH: int
    LIFETIME_REFRESH: int

    TOKEN_ALGORITHM: str

    CORS_URL: str

    MODELS: List[str] = [
        'src.models.user_model',
        'src.models.session_model',
        'src.models.contact_model',
        'src.models.phone_model'
    ]

    class Config:
        env_file_encoding = 'utf-8'

system_app = SystemApp()
