
from __future__ import annotations

from sqlalchemy import Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base, intpk, points


class PersonCollocutor(Base):

    __tablename__ = "collocutor"

    id: Mapped[intpk]
    ref_num: Mapped[str] = mapped_column(Text, nullable=True)
    explanatory_note: Mapped[str] = mapped_column(Text, nullable=True)
    permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[points]
    modified_at: Mapped[points]
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
