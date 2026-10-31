"""Lease endpoints and the nested rent-payment resource.

A lease places a resident in a room for a date range. The core business rule
lives here: a room may not hold more concurrent active leases than its
capacity, where "concurrent" means the date ranges overlap.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/leases", tags=["leases"])


def _get_lease(lease_id: int, db: Session) -> models.Lease:
    lease = db.get(models.Lease, lease_id)
    if lease is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lease not found")
    return lease


def _ranges_overlap(
    start_a: date,
    end_a: date | None,
    start_b: date,
    end_b: date | None,
) -> bool:
    """True if [start_a, end_a] and [start_b, end_b] overlap.

    A ``None`` end date means the lease is open-ended (no upper bound).
    """
    a_ends_before_b = end_a is not None and end_a < start_b
    b_ends_before_a = end_b is not None and end_b < start_a
    return not (a_ends_before_b or b_ends_before_a)


@router.post("", response_model=schemas.LeaseOut, status_code=status.HTTP_201_CREATED)
def create_lease(payload: schemas.LeaseCreate, db: Session = Depends(get_db)):
    room = db.get(models.Room, payload.room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    if db.get(models.Resident, payload.resident_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")

    if payload.end_date is not None and payload.end_date < payload.start_date:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "end_date must not be before start_date",
        )

    # Enforce room capacity against overlapping active leases.
    active = db.scalars(
        select(models.Lease).where(
            models.Lease.room_id == room.id,
            models.Lease.status == models.LeaseStatus.active,
        )
    ).all()
    overlapping = [
        lease
        for lease in active
        if _ranges_overlap(
            payload.start_date, payload.end_date, lease.start_date, lease.end_date
        )
    ]
    if len(overlapping) >= room.capacity:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Room is at capacity ({room.capacity}) for the requested period",
        )

    lease = models.Lease(
        room_id=payload.room_id,
        resident_id=payload.resident_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        monthly_rent=(
            payload.monthly_rent
            if payload.monthly_rent is not None
            else room.monthly_rent
        ),
    )
    db.add(lease)
    db.commit()
    db.refresh(lease)
    return lease


@router.get("", response_model=list[schemas.LeaseOut])
def list_leases(
    resident_id: int | None = None,
    room_id: int | None = None,
    status_filter: models.LeaseStatus | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(models.Lease)
    if resident_id is not None:
        stmt = stmt.where(models.Lease.resident_id == resident_id)
    if room_id is not None:
        stmt = stmt.where(models.Lease.room_id == room_id)
    if status_filter is not None:
        stmt = stmt.where(models.Lease.status == status_filter)
    return db.scalars(stmt).all()


@router.get("/{lease_id}", response_model=schemas.LeaseOut)
def get_lease(lease_id: int, db: Session = Depends(get_db)):
    return _get_lease(lease_id, db)


@router.post("/{lease_id}/end", response_model=schemas.LeaseOut)
def end_lease(
    lease_id: int,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    lease = _get_lease(lease_id, db)
    if lease.status == models.LeaseStatus.ended:
        raise HTTPException(status.HTTP_409_CONFLICT, "Lease is already ended")
    effective_end = end_date or date.today()
    if effective_end < lease.start_date:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "end_date must not be before the lease start_date",
        )
    lease.status = models.LeaseStatus.ended
    lease.end_date = effective_end
    db.commit()
    db.refresh(lease)
    return lease


# --- Nested payments ---------------------------------------------------

@router.post(
    "/{lease_id}/payments",
    response_model=schemas.PaymentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["payments"],
)
def record_payment(
    lease_id: int,
    payload: schemas.PaymentCreate,
    db: Session = Depends(get_db),
):
    _get_lease(lease_id, db)
    payment = models.Payment(
        lease_id=lease_id,
        amount=payload.amount,
        period=payload.period,
        paid_on=payload.paid_on or date.today(),
        method=payload.method,
    )
    db.add(payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A payment for period {payload.period} already exists on this lease",
        )
    db.refresh(payment)
    return payment


@router.get(
    "/{lease_id}/payments",
    response_model=list[schemas.PaymentOut],
    tags=["payments"],
)
def list_payments(lease_id: int, db: Session = Depends(get_db)):
    _get_lease(lease_id, db)
    stmt = (
        select(models.Payment)
        .where(models.Payment.lease_id == lease_id)
        .order_by(models.Payment.period)
    )
    return db.scalars(stmt).all()
