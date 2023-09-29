
from __future__ import annotations

from sqlalchemy import Text, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base, intpk, chapter, affair, pictures, points, user_fk


class GroupChat(Base):

    __tablename__ = "groups_ch"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    group_admin: Mapped[list["User"]] = relationship(
        back_populates="user_group",
    )
    group_chat: Mapped[list["MessageGroup"]] = relationship(
        back_populates="chat_group",
        cascade="all, delete-orphan"
    )
    group_request: Mapped[list["PersonParticipant"]] = relationship(
        back_populates="request_group",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return str(self.id)


class MessageGroup(Base):

    __tablename__ = "message_ch"

    id: Mapped[intpk]
    message: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
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

    id: Mapped[intpk]
    message: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    chat_one: Mapped[list["User"]] = relationship(
        back_populates="one_chat",
    )

    def __str__(self):
        return str(self.id)


class OneOneChat(Base):

    __tablename__ = "one_one_ch"

    id: Mapped[intpk]
    message: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    #...
    owner: Mapped[user_fk]
    one_one: Mapped[int] = mapped_column(
        ForeignKey("collocutor.id", ondelete="CASCADE"), nullable=False
    )
    #...
    one_one_user: Mapped[list["User"]] = relationship(
        back_populates="user_one_one",
    )
    one_collocutor: Mapped[list["PersonCollocutor"]] = relationship(
        back_populates="collocutor_one",
    )

    def __str__(self):
        return str(self.id)
