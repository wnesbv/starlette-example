from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class PersonCollocutor(Base):

    __tablename__ = "collocutor"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ref_num: Mapped[str] = mapped_column(Text, nullable=True)
    explanatory_note: Mapped[str] = mapped_column(Text, nullable=True)
    permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    #...
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    community: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    #...
    call_owner: Mapped[list["User"]] = relationship(
        foreign_keys=[owner]
    )
    call_community: Mapped[list["User"]] = relationship(
        foreign_keys=[community]
    )
    collocutor_one: Mapped[list["OneOneChat"]] = relationship(
        back_populates="one_collocutor",
    )

    def __str__(self):
        return str(self.id)
