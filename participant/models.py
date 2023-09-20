
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import Boolean, Column, String, Text, ForeignKey, Date, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class PersonParticipant(Base):

    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    explanatory_note: Mapped[str] = mapped_column(Text, nullable=True)
    permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    #..
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    group_participant: Mapped[int] = mapped_column(
        ForeignKey("groups_ch.id", ondelete="CASCADE")
    )

    #..
    participant_user: Mapped[list["User"]] = relationship(
        back_populates="user_participant",
    )
    request_group: Mapped[list["GroupChat"]] = relationship(
        back_populates="group_request",
    )

    def __str__(self):
        return str(self.id)
