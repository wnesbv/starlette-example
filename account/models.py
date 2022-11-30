
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True)
    email = sa.Column(sa.String, index=True)
    username = sa.Column(sa.String, unique=True, index=True)
    password = sa.Column(sa.String)
    #..
    email_verified = sa.Column(sa.Boolean, default=False)
    is_active = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    last_login_date = sa.Column(sa.DateTime, server_default=sa.func.now())
    #..
    is_admin = sa.Column(sa.Boolean, default=False)

    #..
    user_item = relationship(
        "Item",
        back_populates="item_user",
    )
    user_cmt = relationship(
        "Comment",
        back_populates="cmt_user",
    )
    #..
    user_group = relationship(
        "GroupChat",
        back_populates="group_admin",
    )
    user_chat = relationship(
        "MessageChat",
        back_populates="chat_user",
    )
    user_participant = relationship(
        "PersonParticipant",
        back_populates="participant_user",
    )
    #..
    user_rrf = relationship(
        "ReserveRentFor",
        back_populates="rrf_user",
    )
    user_rsf = relationship(
        "ReserveServicerFor",
        back_populates="rsf_user",
    )
    #..
    user_service = relationship(
        "Service",
        back_populates="service_user",
    )
    user_rent = relationship(
        "Rent",
        back_populates="rent_user",
    )
    #..
    user_sch_r = relationship(
        "ScheduleRent",
        back_populates="sch_r_user",
    )
    user_sch_s = relationship(
        "ScheduleService",
        back_populates="sch_s_user",
    )
    user_dump_s = relationship(
        "DumpService",
        back_populates="dump_s_user",
    )
    #..

    def __str__(self):
        return str(self.id)


    def get_display_name(self) -> str:
        return self.name or ""

    def get_id(self) -> int:
        assert self.id
        return self.id

    def get_hashed_password(self) -> str:
        return self.password or ""

    def get_scopes(self) -> list:
        return []
