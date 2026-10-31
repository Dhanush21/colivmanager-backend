"""SQLAlchemy ORM models for the co-living domain.

Domain model:

    Property 1--* Room 1--* Lease *--1 Resident
                                 Lease 1--* Payment

A Property is a co-living building. Each Room belongs to a Property and can
host up to `capacity` concurrent residents. A Lease places a Resident in a
Room for a period of time, and Payments record rent collected against a Lease.
"""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class LeaseStatus(str, enum.Enum):
    active = "active"
    ended = "ended"


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    rooms: Mapped[list["Room"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("property_id", "number", name="uq_room_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE")
    )
    number: Mapped[str] = mapped_column(String(50))
    monthly_rent: Mapped[float] = mapped_column(Float)
    capacity: Mapped[int] = mapped_column(default=1)

    property: Mapped["Property"] = relationship(back_populates="rooms")
    leases: Mapped[list["Lease"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    leases: Mapped[list["Lease"]] = relationship(back_populates="resident")


class Lease(Base):
    __tablename__ = "leases"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_rent: Mapped[float] = mapped_column(Float)
    status: Mapped[LeaseStatus] = mapped_column(
        Enum(LeaseStatus), default=LeaseStatus.active
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    room: Mapped["Room"] = relationship(back_populates="leases")
    resident: Mapped["Resident"] = relationship(back_populates="leases")
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="lease", cascade="all, delete-orphan"
    )


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("lease_id", "period", name="uq_payment_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lease_id: Mapped[int] = mapped_column(ForeignKey("leases.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float)
    # The rent month this payment settles, formatted "YYYY-MM".
    period: Mapped[str] = mapped_column(String(7))
    paid_on: Mapped[date] = mapped_column(Date, default=date.today)
    method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    lease: Mapped["Lease"] = relationship(back_populates="payments")
