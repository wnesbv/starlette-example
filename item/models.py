
from __future__ import annotations

from datetime import datetime, date

import enum
from sqlalchemy import Column, String, Text, ForeignKey, Date, DateTime, Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class Slider(Base):
    __tablename__ = "slider"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_sl: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Item(Base):
    __tablename__ = "item_tm"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # ...
    item_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    item_user: Mapped[list["User"]] = relationship(
        back_populates="user_item",
    )
    item_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_item"
    )
    item_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_item",
    )
    item_service: Mapped[list["Service"]] = relationship(
        back_populates="service_item",
    )
    item_rrf: Mapped[list["ReserveRentFor"]] = relationship(
        back_populates="rrf_item",
    )

    def __str__(self):
        return str(self.id)


class Rent(Base):
    __tablename__ = "rent_tm"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    # ...
    file: Mapped[str] = mapped_column(String, nullable=True)
    # ...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    rent_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    rent_belongs: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    rent_user: Mapped[list["User"]] = relationship(
        back_populates="user_rent",
    )
    rent_item: Mapped[list["Item"]] = relationship(
        back_populates="item_rent",
    )
    rent_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_rent"
    )
    rent_sch_r: Mapped[list["ScheduleRent"]] = relationship(
        back_populates="sch_r_rent",
    )
    rent_rrf: Mapped[list["ReserveRentFor"]] = relationship(
        back_populates="rrf_rent",
    )

    def __str__(self):
        return str(self.id)


class Service(Base):
    __tablename__ = "service_tm"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text(200), nullable=True)
    # ...
    file: Mapped[str] = mapped_column(String, nullable=True)
    # ...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    service_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service_belongs: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    service_user: Mapped[list["User"]] = relationship(
        back_populates="user_service",
    )
    service_item: Mapped[list["Item"]] = relationship(
        back_populates="item_service",
    )
    service_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_service"
    )
    service_sch_s: Mapped[list["ScheduleService"]] = relationship(
        back_populates="sch_s_service",
    )
    service_rsf: Mapped[list["ReserveServicerFor"]] = relationship(
        back_populates="rsf_service",
    )
    service_dump_s: Mapped[list["DumpService"]] = relationship(
        back_populates="dump_s_service",
    )

    def __str__(self):
        return str(self.id)


class ScheduleRent(Base):
    __tablename__ = "sch_r"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text(200), nullable=True)
    # ...
    start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # ...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    sch_r_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sch_r_rent_id: Mapped[int] = mapped_column(
        ForeignKey("rent_tm.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    sch_r_user: Mapped[list["User"]] = relationship(
        "User",
        back_populates="user_sch_r",
    )
    sch_r_rent: Mapped[list["Rent"]] = relationship(
        "Rent",
        back_populates="rent_sch_r",
    )

    def __str__(self):
        return str(self.id)


class MyEnum(enum.Enum):
    event = 1
    holiday = 2
    birthday = 3


class ScheduleService(Base):
    __tablename__ = "sch_s"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text(200), nullable=True)
    # ...
    type_on: Mapped[str] = mapped_column(Enum(MyEnum), nullable=True)
    number_on: Mapped[date] = mapped_column(Date, nullable=True)
    there_is: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # ...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    sch_s_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sch_s_service_id: Mapped[int] = mapped_column(
        ForeignKey("service_tm.id", ondelete="CASCADE"), nullable=False
    )

    # ...
    sch_s_user: Mapped[list["User"]] = relationship(
        back_populates="user_sch_s",
    )
    sch_s_service: Mapped[list["Service"]] = relationship(
        back_populates="service_sch_s",
    )
    sch_s_rsf: Mapped[list["ReserveServicerFor"]] = relationship(
        back_populates="rsf_sch_s",
    )

    def __str__(self):
        return str(self.id)


class DumpService(Base):
    __tablename__ = "dump_s"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[datetime] = mapped_column(DateTime, unique=True, index=True)

    # ...
    dump_s_owner: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ), nullable=False
    )
    dump_s_service_id: Mapped[int] = mapped_column(
        ForeignKey(
            "service_tm.id",
            ondelete="CASCADE"
        ), nullable=False
    )

    # ...
    dump_s_user: Mapped[list["User"]] = relationship(
        back_populates="user_dump_s",
    )
    dump_s_service: Mapped[list["Service"]] = relationship(
        back_populates="service_dump_s",
    )

    def __str__(self):
        return str(self.id)
