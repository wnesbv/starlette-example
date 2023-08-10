
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class GroupChat(Base):

    __tablename__ = "groups_ch"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    file: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    admin_group: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    group_admin: Mapped[list["User"]] = relationship(
        back_populates="user_group",
    )
    group_chat: Mapped[list["MessageChat"]] = relationship(
        back_populates="chat_group",
    )
    group_request: Mapped[list["PersonParticipant"]] = relationship(
        back_populates="request_group",
    )

    def __str__(self):
        return str(self.id)


class MessageChat(Base):

    __tablename__ = "message_ch"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    owner_msg: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    id_group: Mapped[int] = mapped_column(
        ForeignKey("groups_ch.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    chat_user: Mapped[list["User"]] = relationship(
        back_populates="user_chat",
    )
    chat_group: Mapped[list["GroupChat"]] = relationship(
        back_populates="group_chat",
    )

    def __str__(self):
        return str(self.id)


class OneChat(Base):

    __tablename__ = "one_ch"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    owner_msg: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    chat_one: Mapped[list["User"]] = relationship(
        back_populates="one_chat",
    )

    def __str__(self):
        return str(self.id)
