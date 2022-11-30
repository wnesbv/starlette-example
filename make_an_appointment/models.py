
import sqlalchemy as sa

from sqlalchemy.orm import relationship

from db_config.storage_config import Base


class ReserveRentFor(Base):
    __tablename__ = "rsv_rrf"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    description = sa.Column(sa.String, nullable=True)
    time_start = sa.Column(sa.DateTime, nullable=True)
    time_end = sa.Column(sa.DateTime, nullable=True)
    reserve_period = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    rrf_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    rrf_item_id = sa.Column(
        sa.Integer, sa.ForeignKey("item_tm.id", ondelete="CASCADE")
    )
    rrf_rent_id = sa.Column(
        sa.Integer, sa.ForeignKey("rent_tm.id", ondelete="CASCADE")
    )
    rrf_sch_r_id = sa.Column(
        sa.Integer, sa.ForeignKey("sch_r.id", ondelete="CASCADE")
    )
    #..

    rrf_user = relationship(
        "User",
        back_populates="user_rrf",
    )
    rrf_item = relationship(
        "Item",
        back_populates="item_rrf",
    )
    rrf_rent = relationship(
        "Rent",
        back_populates="rent_rrf",
    )

    def __str__(self):
        return str(self.id)


class ReserveServicerFor(Base):
    __tablename__ = "rsv_rsf"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    description = sa.Column(sa.String, nullable=True)
    reserve_time = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

    #..
    rsf_owner = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    rsf_service_id = sa.Column(
        sa.Integer, sa.ForeignKey("service_tm.id", ondelete="CASCADE")
    )
    rsf_sch_s_id = sa.Column(
        sa.Integer, sa.ForeignKey("sch_s.id", ondelete="CASCADE")
    )
    #..

    rsf_user = relationship(
        "User",
        back_populates="user_rsf",
    )
    rsf_service = relationship(
        "Service",
        back_populates="service_rsf",
    )
    rsf_sch_s = relationship(
        "ScheduleService",
        back_populates="sch_s_rsf",
    )

    def __str__(self):
        return str(self.id)
