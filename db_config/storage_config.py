
from __future__ import annotations

from typing_extensions import Annotated

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey

from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column

from db_config.settings import settings


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
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
chapter = Annotated[str, mapped_column(String(30), unique=True, index=True)]
affair = Annotated[str, mapped_column(Text(200), nullable=True)]
pictures = Annotated[str, mapped_column(String, nullable=True)]
# ..
points = Annotated[datetime, mapped_column(DateTime, nullable=True)]
# ..
user_fk = Annotated[
    int, mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
]
