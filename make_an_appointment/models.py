
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base


class ReserveRentFor(Base):
    __tablename__ = "rsv_rrf"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text(200), nullable=True)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    time_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reserve_period: Mapped[str] = mapped_column(String(), nullable=True)
    # ...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    rrf_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    rrf_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE")
    )
    rrf_rent_id: Mapped[int] = mapped_column(
        ForeignKey("rent_tm.id", ondelete="CASCADE")
    )
    rrf_sch_r_id: Mapped[int] = mapped_column(
        ForeignKey("sch_r.id", ondelete="CASCADE")
    )
    
    # ...
    rrf_user: Mapped[list["User"]] = relationship(
        back_populates="user_rrf",
    )
    rrf_item: Mapped[list["Item"]] = relationship(
        back_populates="item_rrf",
    )
    rrf_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_rrf",
    )

    def __str__(self):
        return str(self.id)


class ReserveServicerFor(Base):
    __tablename__ = "rsv_rsf"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text(200), nullable=True)
    reserve_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    rsf_owner: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    rsf_service_id: Mapped[int] = mapped_column(
        ForeignKey("service_tm.id", ondelete="CASCADE")
    )
    rsf_sch_s_id: Mapped[int] = mapped_column(
        ForeignKey("sch_s.id", ondelete="CASCADE")
    )
    # ...

    rsf_user: Mapped[list["User"]] = relationship(
        "User",
        back_populates="user_rsf",
    )
    rsf_service: Mapped[list["Service"]] = relationship(
        back_populates="service_rsf",
    )
    rsf_sch_s: Mapped[list["ScheduleService"]] = relationship(
        back_populates="sch_s_rsf",
    )

    def __str__(self):
        return str(self.id)
