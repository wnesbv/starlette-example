
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from db_config.settings import settings


Base = declarative_base()

if settings.USE_SQLITE_DB == "True":
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3/"

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL
    )
else:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL
    )

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
