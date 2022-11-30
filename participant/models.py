
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class PersonParticipant(Base):

    __tablename__ = "participant"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    explanations_person = sa.Column(sa.Text, nullable=True)
    permission = sa.Column(sa.Boolean, default=False, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    participant = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    group_participant = sa.Column(
        sa.Integer, sa.ForeignKey("groups_ch.id", ondelete="CASCADE")
    )

    #..
    participant_user = relationship(
        "User",
        back_populates="user_participant",
    )
    request_group = relationship(
        "GroupChat",
        back_populates="group_request",
    )

    def __str__(self):
        return str(self.id)
