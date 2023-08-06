
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Boolean, String, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=True)
    # ...
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # ..
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_login_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    user_item: Mapped[list["Item"]] = relationship(
        back_populates="item_user"
    )
    user_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_user"
    )
    # ...
    user_group: Mapped[list["GroupChat"]] = relationship(
        back_populates="group_admin"
    )
    user_chat: Mapped[list["MessageChat"]] = relationship(
        back_populates="chat_user"
    )
    one_chat: Mapped[list["OneChat"]] = relationship(
        back_populates="chat_one"
    )
    user_participant: Mapped[list["PersonParticipant"]] = relationship(
        back_populates="participant_user"
    )

    # ...
    user_rrf: Mapped[list["ReserveRentFor"]] = relationship(
        back_populates="rrf_user"
    )
    user_rsf: Mapped[list["ReserveServicerFor"]] = relationship(
        back_populates="rsf_user"
    )
    # ...
    user_service: Mapped[list["Service"]] = relationship(
        back_populates="service_user"
    )
    user_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_user"
    )
    # ...
    user_sch_r: Mapped[list["ScheduleRent"]] = relationship(
        back_populates="sch_r_user",
    )
    user_sch_s: Mapped[list["ScheduleService"]] = relationship(
        back_populates="sch_s_user"
    )
    user_dump_s: Mapped[list["DumpService"]] = relationship(
        back_populates="dump_s_user"
    )
    # ...

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
