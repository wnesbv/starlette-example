
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base

from .img import FileType


class Slider(Base):
    __tablename__ = "slider"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.Text, nullable=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())


class Item(Base):
    __tablename__ = "item_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    item_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )

    #..
    item_user = relationship(
        "User",
        back_populates="user_item",
    )
    item_cmt = relationship(
        "Comment",
        back_populates="cmt_item"
    )
    item_rent = relationship(
        "Rent",
        back_populates="rent_item",
    )
    item_service = relationship(
        "Service",
        back_populates="service_item",
    )
    item_rrf = relationship(
        "ReserveRentFor",
        back_populates="rrf_item",
    )

    def __str__(self):
        return str(self.id)


class Rent(Base):
    __tablename__ = "rent_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    rent_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    rent_belongs = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")

    )
    #..
    rent_user = relationship(
        "User",
        back_populates="user_rent",
    )
    rent_item = relationship(
        "Item",
        back_populates="item_rent",
    )
    rent_cmt = relationship(
        "Comment",
        back_populates="cmt_rent"
    )
    rent_sch_r = relationship(
        "ScheduleRent",
        back_populates="sch_r_rent",
    )
    rent_rrf = relationship(
        "ReserveRentFor",
        back_populates="rrf_rent",
    )

    def __str__(self):
        return str(self.id)


class Service(Base):
    __tablename__ = "service_tm"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    file = sa.Column(FileType.as_mutable(sa.JSON), nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #...
    service_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    service_belongs = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")
    )

    #..
    service_user = relationship(
        "User",
        back_populates="user_service",
    )
    service_item = relationship(
        "Item",
        back_populates="item_service",
    )
    service_cmt = relationship(
        "Comment",
        back_populates="cmt_service"
    )
    service_sch_s = relationship(
        "ScheduleService",
        back_populates="sch_s_service",
    )
    service_rsf = relationship(
        "ReserveServicerFor",
        back_populates="rsf_service",
    )
    service_dump_s = relationship(
        "DumpService",
        back_populates="dump_s_service",
    )

    def __str__(self):
        return str(self.id)


class ScheduleRent(Base):
    __tablename__ = "sch_r"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    #..
    start = sa.Column(sa.DateTime, nullable=True)
    end = sa.Column(sa.DateTime, nullable=True)
    #..
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    sch_r_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    sch_r_rent_id = sa.Column(
        sa.Integer, sa.ForeignKey("rent_tm.id", ondelete="CASCADE")
    )

    #..
    sch_r_user = relationship(
        "User",
        back_populates="user_sch_r",
    )
    sch_r_rent = relationship(
        "Rent",
        back_populates="rent_sch_r",
    )

    def __str__(self):
        return str(self.id)


class ScheduleService(Base):
    __tablename__ = "sch_s"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=True)
    type = sa.Column(sa.String, nullable=True)
    title = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.Text, nullable=True)
    #..
    date = sa.Column(sa.Date, nullable=True)
    there_is = sa.Column(sa.DateTime, nullable=True)
    #..
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    sch_s_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    sch_s_service_id = sa.Column(
        sa.Integer, sa.ForeignKey("service_tm.id", ondelete="CASCADE")
    )

    #..
    sch_s_user = relationship(
        "User",
        back_populates="user_sch_s",
    )
    sch_s_service = relationship(
        "Service",
        back_populates="service_sch_s",
    )
    sch_s_rsf = relationship(
        "ReserveServicerFor",
        back_populates="rsf_sch_s",
    )

    def __str__(self):
        return str(self.id)


class DumpService(Base):
    __tablename__ = "dump_s"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.DateTime, unique=True, index=True)
    #..

    dump_s_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    dump_s_service_id = sa.Column(
        sa.Integer, sa.ForeignKey("service_tm.id", ondelete="CASCADE")
    )

    #..
    dump_s_user = relationship(
        "User",
        back_populates="user_dump_s",
    )
    dump_s_service = relationship(
        "Service",
        back_populates="service_dump_s",
    )

    def __str__(self):
        return str(self.id)
