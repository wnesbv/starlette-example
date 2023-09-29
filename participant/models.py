
from __future__ import annotations

from sqlalchemy import Boolean, Text, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base, intpk, points, user_fk


class PersonParticipant(Base):

    __tablename__ = "participant"

    id: Mapped[intpk]
    explanatory_note: Mapped[str] = mapped_column(Text, nullable=True)
    permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[points]
    modified_at: Mapped[points]
    #...
    owner: Mapped[user_fk]
    community: Mapped[int] = mapped_column(
        ForeignKey("groups_ch.id", ondelete="CASCADE"), nullable=False
    )
    #...
    participant_user: Mapped[list["User"]] = relationship(
        back_populates="user_participant",
    )
    request_group: Mapped[list["GroupChat"]] = relationship(
        back_populates="group_request",
    )

    def __str__(self):
        return str(self.id)
