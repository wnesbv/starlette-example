
from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class GroupChat(Base):

    __tablename__ = "groups_ch"

    id = sa.Column(sa.Integer, primary_key=True, index=True)

    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    admin_group = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )

    #..
    group_admin = relationship(
        "User",
        back_populates="user_group",
    )
    group_chat = relationship(
        "MessageChat",
        back_populates="chat_group",
    )
    group_request = relationship(
        "PersonParticipant",
        back_populates="request_group",
    )

    def __str__(self):
        return str(self.id)


class MessageChat(Base):

    __tablename__ = "message_ch"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    message = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now())

    #..
    owner_chat = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    id_group = sa.Column(
        sa.Integer, sa.ForeignKey("groups_ch.id", ondelete="CASCADE")
    )

    #..
    chat_user = relationship(
        "User",
        back_populates="user_chat",
    )
    chat_group = relationship(
        "GroupChat",
        back_populates="group_chat",
    )

    def __str__(self):
        return str(self.id)
