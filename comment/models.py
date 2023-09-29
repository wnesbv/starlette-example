
from __future__ import annotations

from sqlalchemy import Text, ForeignKey, JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base, intpk, points, user_fk


class Comment(Base):
    __tablename__ = "comment_cmt"

    id: Mapped[intpk]
    opinion: Mapped[str] = mapped_column(Text(200), nullable=False)
    user_on: Mapped[dict|list] = mapped_column(JSON, nullable=True)
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    cmt_item_id: Mapped[int] = mapped_column(
        ForeignKey(
            "item_tm.id",
            ondelete="CASCADE",
        ), nullable=True
    )
    cmt_rent_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rent_tm.id",
            ondelete="CASCADE",
        ), nullable=True
    )
    cmt_service_id: Mapped[int] = mapped_column(
        ForeignKey(
            "service_tm.id",
            ondelete="CASCADE",
        ), nullable=True
    )

    # ...
    cmt_user: Mapped[list["User"]] = relationship(
        back_populates="user_cmt"
    )
    cmt_item: Mapped[list["Item"]] = relationship(
        back_populates="item_cmt"
    )
    cmt_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_cmt"
    )
    cmt_service: Mapped[list["Service"]] = relationship(
        back_populates="service_cmt"
    )

    def __str__(self):
        return str(self.id)
