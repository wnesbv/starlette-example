
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class Comment(Base):
    __tablename__ = "comment_cmt"

    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    opinion = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    cmt_user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    #..
    cmt_item_id = sa.Column(
        sa.Integer, sa.ForeignKey(
            "item_tm.id",
            ondelete="CASCADE",
        )
    )
    cmt_rent_id = sa.Column(
        sa.Integer, sa.ForeignKey(
            "rent_tm.id",
            ondelete="CASCADE",
        )
    )
    cmt_service_id = sa.Column(
        sa.Integer, sa.ForeignKey(
            "service_tm.id",
            ondelete="CASCADE",
        )
    )

    #..
    cmt_user = relationship(
        "User",
        back_populates="user_cmt"
    )
    cmt_item = relationship(
        "Item",
        back_populates="item_cmt"
    )
    cmt_rent = relationship(
        "Rent",
        back_populates="rent_cmt"
    )
    cmt_service = relationship(
        "Service",
        back_populates="service_cmt"
    )

    def __str__(self):
        return str(self.id)
