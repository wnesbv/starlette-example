from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, String, Text

from sqlalchemy.orm import Mapped, mapped_column

from db_config.storage_config import Base


class Privileged(Base):
    __tablename__ = "privileged"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prv_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    prv_in: Mapped[str] = mapped_column(Text, nullable=True)

    # ...
    def __str__(self):
        return str(self.prv_key)
