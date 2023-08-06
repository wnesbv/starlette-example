
from pydantic import BaseModel
from decouple import config


class Settings(BaseModel):
    PROJECT_TITLE: str = "Starlette ALL auth"
    PROJECT_VERSION: str = "1.0.0"

    USE_SQLITE_DB: bool = config("USE_SQLITE_DB")

    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = config("POSTGRES_PORT")
    POSTGRES_DB: str = config("POSTGRES_DB")

    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    FROM: str = config("FROM")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    TO_MAIL: str = config("TO_MAIL")

    SECRET_KEY: str = config("SECRET")
    ALGORITHM: str = "HS256"

    DEBUG: str = config("DEBUG")
    ALLOWED_HOSTS: str = config("ALLOWED_HOSTS")
    JWT_PREFIX: str = config("JWT_PREFIX")

    JWT_ALGORITHM: str = config("JWT_ALGORITHM")

    EMAIL_TOKEN_EXPIRY_MINUTES: int = 120

    UPLOAD_FOLDER: str = config("UPLOAD_FOLDER")

    TIME_FORMAT: int = "%H:%M:%S"
    DATETIME_FORMAT: int = "%Y-%m-%d %H:%M:%S"
    DATE_TIME: int = "%Y-%m-%d:%H:%M"
    DATE_T: int = "%Y-%m-%dT%H:%M"
    DATE: int = "%Y-%m-%d"
    DATE_POINT: int = "%d.%m.%Y"
    DATE_L: int = "%Y-%m-%dT%H-%M"

settings = Settings()
