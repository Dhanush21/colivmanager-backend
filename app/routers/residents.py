"""Resident endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/residents", tags=["residents"])


def _get_resident(resident_id: int, db: Session) -> models.Resident:
    resident = db.get(models.Resident, resident_id)
    if resident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
    return resident


@router.post("", response_model=schemas.ResidentOut, status_code=status.HTTP_201_CREATED)
def create_resident(payload: schemas.ResidentCreate, db: Session = Depends(get_db)):
    resident = models.Resident(**payload.model_dump())
    db.add(resident)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A resident with that email already exists"
        )
    db.refresh(resident)
    return resident


@router.get("", response_model=list[schemas.ResidentOut])
def list_residents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stmt = select(models.Resident).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{resident_id}", response_model=schemas.ResidentOut)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    return _get_resident(resident_id, db)


@router.patch("/{resident_id}", response_model=schemas.ResidentOut)
def update_resident(
    resident_id: int,
    payload: schemas.ResidentUpdate,
    db: Session = Depends(get_db),
):
    resident = _get_resident(resident_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resident, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A resident with that email already exists"
        )
    db.refresh(resident)
    return resident


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = _get_resident(resident_id, db)
    db.delete(resident)
    db.commit()
