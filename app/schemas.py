"""Pydantic request/response schemas (pydantic v2)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import LeaseStatus

# A compact year-month pattern, e.g. "2026-10".
PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


# --- Property -----------------------------------------------------------

class PropertyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=120)


class PropertyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=120)


class PropertyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    created_at: datetime


# --- Room ---------------------------------------------------------------

class RoomCreate(BaseModel):
    number: str = Field(min_length=1, max_length=50)
    monthly_rent: float = Field(ge=0)
    capacity: int = Field(default=1, ge=1)


class RoomUpdate(BaseModel):
    number: str | None = Field(default=None, min_length=1, max_length=50)
    monthly_rent: float | None = Field(default=None, ge=0)
    capacity: int | None = Field(default=None, ge=1)


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    number: str
    monthly_rent: float
    capacity: int


# --- Resident -----------------------------------------------------------

class ResidentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)


class ResidentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)


class ResidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    created_at: datetime


# --- Lease --------------------------------------------------------------

class LeaseCreate(BaseModel):
    room_id: int
    resident_id: int
    start_date: date
    end_date: date | None = None
    # Optional: defaults to the room's monthly_rent when omitted.
    monthly_rent: float | None = Field(default=None, ge=0)


class LeaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    resident_id: int
    start_date: date
    end_date: date | None
    monthly_rent: float
    status: LeaseStatus
    created_at: datetime


# --- Payment ------------------------------------------------------------

class PaymentCreate(BaseModel):
    amount: float = Field(ge=0)
    period: str = Field(pattern=PERIOD_PATTERN, examples=["2026-10"])
    paid_on: date | None = None
    method: str | None = Field(default=None, max_length=40)


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lease_id: int
    amount: float
    period: str
    paid_on: date
    method: str | None
    created_at: datetime
